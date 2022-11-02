This is improved version of [previously][1] shared creating/updating security groups from managed prefix list. Update: New rules will be added with descriptions. This script can be used as a response for [this][2] script.

```python
# import required modules
import boto3, logging, math

# set logging configuration
thelogcount = 1
class ContextFilter( logging.Filter ):
    def filter( self, record ):
        global thelogcount
        record.count = thelogcount
        thelogcount += 1
        return True
logger = logging.getLogger( 'LOGGING' )
logger.setLevel( logging.INFO )
handler = logging.StreamHandler()
formatter = logging.Formatter( '%(asctime)s - %(name)s - %(count)s - %(levelname)s - %(message)s' )
handler.setFormatter( formatter )
logging.getLogger().addHandler( handler )
logger.addFilter( ContextFilter() )

# set aws session profile
session = boto3.Session(profile_name = 'YOUR-PROFILE-NAME')
client = session.client('ec2', region_name = 'YOUR-REGION')

# global variables
PrefixId = "YOUR-MANAGED-PREFIX-ID"
VpcId = "YOUR-VPC-ID"
security_group_tag = { 'KEY': 'VALUE' }
INGRESS_PORTS = "YOUR-PORTS"

# get cidrs from managed prefix
def get_entries_cidr(PrefixId):
    try:
        existing_entry = []
        response = client.get_managed_prefix_list_entries(PrefixListId = PrefixId, MaxResults = 100)
        results = response['Entries']
        while 'NextToken' in response:
            response = client.get_managed_prefix_list_entries(PrefixListId = PrefixId, NextToken = response['NextToken'])
            results.extend(response['Entries'])
        for i in results:
            existing_entry.append(i['Cidr'])

        return existing_entry

    except Exception as error:
        logger.error( error )

# get all values from managed prefix list
def get_entries_result(PrefixId):
    try:
        response = client.get_managed_prefix_list_entries(PrefixListId = PrefixId, MaxResults = 100)
        results = response['Entries']
        while 'NextToken' in response:
            response = client.get_managed_prefix_list_entries(PrefixListId = PrefixId, NextToken = response['NextToken'])
            results.extend(response['Entries'])
        return results

    except Exception as error:
        logger.error( error )

# look for existing security groups
def get_security_groups(security_group_tag):
    try:
        filters = list()
        for key, value in security_group_tag.items():
            filters.extend(
                [
                    { 'Name': "tag-key", 'Values': [ key ] },
                    { 'Name': "tag-value", 'Values': [ value ] }
                ]
            )
        response = client.describe_security_groups(Filters=filters)
        return response['SecurityGroups']
 
    except Exception as error:
        logger.error( error )
        
# Create security groups
def create_sg(PrefixId, VpcId, security_group_tag):
    try:
        groups = []
        existing_sg = [group['GroupId'] for group in get_security_groups(security_group_tag)]
        entries = int(len(get_entries(PrefixId)))
        roundup = math.ceil(entries / 60)
  
        if len(existing_sg) == 0:
            logger.info( "No existing groups" )
            logger.info("Creating {0} security groups".format(roundup))
            count = 0
            # Limit per security group rule is 60
            while count <= roundup:
                response = client.create_security_group(
                    Description = ''.join(PrefixId) + "-" + str(count),
                    GroupName = ''.join(PrefixId) + "-" + str(count),
                    VpcId = VpcId,
                    TagSpecifications=[
                        {
                            'ResourceType': 'security-group',
                            'Tags': [
                                {
                                    'Key': 'Name',
                                    'Value': ''.join(PrefixId) + "-" + str(count)
                                },
                                {
                                    'Key': 'Sonicwall',
                                    'Value': 'True'
                                },
                            ]
                        }
                    ]
                )
                count += 1
                logger.info("Created SG: {0}".format(response['GroupId']))
                groups.append(response['GroupId'])
            return groups
        else:
            return existing_sg

    except Exception as error:
        logger.error( error )

# look for existing security group permissions
def get_security_group_permissions(security_group_tag):
    try:
        filters = list()
        for key, value in security_group_tag.items():
            filters.extend(
                [
                    { 'Name': "tag-key", 'Values': [ key ] },
                    { 'Name': "tag-value", 'Values': [ value ] }
                ]
            )
        response = client.describe_security_groups(Filters=filters)
        g_permissions = []
        for GroupId in response['SecurityGroups']:
            g_permissions.append(GroupId['IpPermissions'])
        return g_permissions

    except Exception as error:
        logger.error( error )

# describe security group rules
def describe_security_group_rules(PrefixId, VpcId, security_group_tag):
    try:
        existing_ranges = list()
        for rule in get_security_group_permissions(security_group_tag):
            if len(rule) > 0:
                for permission in rule:
                    for range in permission['IpRanges']:
                        existing_ranges.append(range['CidrIp'])
            else:
                logger.info("No permissions rules found")
                existing_ranges = []
        return existing_ranges
        
    except Exception as error:
        logger.error( error )

# update groups with new inbound rules
def update_security_groups(PrefixId, VpcId, security_group_tag):
    try:      
        diff_list = set(get_entries_cidr(PrefixId)) - set(describe_security_group_rules(PrefixId, VpcId, security_group_tag))
        logger.info('Number of entries: {0}, and entries to add: {1}'.format(len(diff_list), diff_list))
        revoke_list = set(describe_security_group_rules(PrefixId, VpcId, security_group_tag)) - set(get_entries_cidr(PrefixId))
        logger.info('Number of entries: {0}, and entries to revoke: {1}'.format(len(revoke_list), revoke_list))
        
        chunk_size = 55

        groups = [group['GroupId'] for group in get_security_groups(security_group_tag)]
        
        # adding permissions
        if len(diff_list) == 0:
            logger.info("No ranges to add")
        else:
            g_INDEX = 0
            g_SIZE = 0
            for ip_ranges in list(diff_list):
                descr = ''.join([key['Description'] for key in get_entries_result(PrefixId) if ip_ranges in key['Cidr']])
                logger.info(descr)
                
                g_SIZE += 1
                # set add parameters
                permission = { 'ToPort': INGRESS_PORTS, 'FromPort': INGRESS_PORTS, 'IpProtocol': '-1'}
                add_params = {
                    'ToPort': permission['ToPort'],
                    'FromPort': permission['FromPort'],
                    'IpRanges': [
                        {
                            'CidrIp': ip_ranges,
                            'Description': descr
                        },
                    ],
                    'IpProtocol': permission['IpProtocol']
                    }
                client.authorize_security_group_ingress( GroupId = groups[g_INDEX] , IpPermissions = [add_params] )
                logger.info("added range: {0} to group: {1} ".format(ip_ranges, groups[g_INDEX])) 
                if g_SIZE == chunk_size:
                    g_INDEX += 1
                    g_SIZE = 0

        # revoke permissions
        if len(revoke_list) == 0:
            logger.info("No ranges to revoke")
        else:
            logger.info("Ranges to revoke: {}".format(revoke_list))
            # get group id to be revoked
            for cidr in list(revoke_list):
                response = client.describe_security_groups(Filters=[{'Name':'ip-permission.cidr', 'Values': [cidr]}, {'Name': 'tag-key', 'Values': list(security_group_tag.keys())}] )
                get_group_id_to_revoke = ([group['GroupId'] for group in response['SecurityGroups']])

                # set revoke parameters
                permission = { 'ToPort': INGRESS_PORTS, 'FromPort': INGRESS_PORTS, 'IpProtocol': '-1'}
                revoke_params = {
                    'ToPort': permission['ToPort'],
                    'FromPort': permission['FromPort'],
                    'IpRanges': [
                        {
                            'CidrIp': cidr
                        },
                    ],
                    'IpProtocol': permission['IpProtocol']
                    }
                for to_revoke in get_group_id_to_revoke:
                    revoke = client.revoke_security_group_ingress(GroupId = to_revoke, IpPermissions=[revoke_params])
                    logger.info("Revoked ranges: {0} from group: {1}".format(cidr,to_revoke))
                        
    except Exception as error:
        logger.error( error )
```
[1]: https://github.com/MederD/AWS_playground/blob/main/awsLambda/populate_sg_rules.py
[2]: https://github.com/MederD/AWS_playground/blob/main/awsLambda/updated_modify_managed_prefix_list.md
