# https://docs.aws.amazon.com/vpc/latest/userguide/amazon-vpc-limits.html#vpc-limits-security-groups
# Security group inbound rule quote can be increased, however this quota multiplied by the quota for security groups per network interface (5 default) cannot exceed 1,000.

# import required modules
import boto3, logging, time, math

# set logging configuration
logging.basicConfig( level=logging.INFO, format='%(levelname)s : %(asctime)s : %(message)s' )
logger = logging.getLogger(__name__)

# set aws session profile
session = boto3.Session(profile_name = 'YOUR-PROFILE-NAME')
client = session.client('ec2', region_name = 'YOUR-REGION)

# global variables
PrefixId = "YOUR-MANAGED-PREFIX-ID"
VpcId = "YOUR-VPC-ID"
security_group_tag = { 'KEY': 'VALUE' }
INGRESS_PORTS = YOUR-PORT/S

# get managed prefix list entries
def get_entries(PrefixId):
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

    except Exception as e:
        logging.error("Error", exc_info = e)

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
 
    except Exception as e:
        logging.error("Error", exc_info = e)

# create security group if noe existing
def create_sg(PrefixId, VpcId, security_group_tag):
    try:
        groups = []
        existing_sg = [group['GroupId'] for group in get_security_groups(security_group_tag)]
        entries = int(len(get_entries(PrefixId)))
        roundup = math.ceil(entries / 60)
  
        if len(existing_sg) == 0:
            logging.info( "No existing groups" )
            logging.info("Creating {0} security groups".format(roundup))
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
                                    'Key': 'KEY',
                                    'Value': 'VALUE'
                                },
                            ]
                        }
                    ]
                )
                count += 1
                logging.info("Created SG: {0}".format(response['GroupId']))
                groups.append(response['GroupId'])
            return groups
        else:
            logging.info("Existing security groups: {}".format(existing_sg))
            return existing_sg

    except Exception as e:
        logging.error("Error", exc_info = e)

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

    except Exception as e:
        logging.error("Error", exc_info = e)

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
                logging.info("No permissions rules found")
                existing_ranges = []
        return existing_ranges
        
    except Exception as e:
        logging.error("Error", exc_info = e)

# update groups with new inbound rules
def update_security_groups(PrefixId, VpcId, security_group_tag):
    try:      
        diff_list = set(get_entries(PrefixId)) - set(describe_security_group_rules(PrefixId, VpcId, security_group_tag))
        revoke_list = set(describe_security_group_rules(PrefixId, VpcId, security_group_tag)) - set(get_entries(PrefixId))
   
        chunk_size = 55

        groups = [group['GroupId'] for group in get_security_groups(security_group_tag)]

        # adding permissions
        if len(diff_list) == 0:
            logging.info("No ranges to add")
        else:
            g_INDEX = 0
            g_SIZE = 0
            for ip_ranges in list(diff_list):
                g_SIZE += 1
                # set add parameters
                permission = { 'ToPort': INGRESS_PORTS, 'FromPort': INGRESS_PORTS, 'IpProtocol': 'YOUR-PROTOCOL'}
                add_params = {
                    'ToPort': permission['ToPort'],
                    'FromPort': permission['FromPort'],
                    'IpRanges': [
                        {
                            'CidrIp': ip_ranges
                        },
                    ],
                    'IpProtocol': permission['IpProtocol']
                    }
                client.authorize_security_group_ingress( GroupId = groups[g_INDEX] , IpPermissions = [add_params] )
                logging.info("added range: {0} to group: {1} ".format(ip_ranges, groups[g_INDEX])) 
                if g_SIZE == chunk_size:
                    g_INDEX += 1
                    g_SIZE = 0

        # revoke permissions
        if len(revoke_list) == 0:
            logging.info("No ranges to revoke")
        else:
            logging.info("Ranges to revoke: {}".format(revoke_list))

            # get group id to be revoked
            for cidr in list(revoke_list):
                response = client.describe_security_groups(Filters=[{'Name':'ip-permission.cidr', 'Values': [cidr]}, {'Name': 'tag-key', 'Values': list(security_group_tag.keys())}] )
                get_group_id_to_revoke = ([group['GroupId'] for group in response['SecurityGroups']])

                # set revoke parameters
                permission = { 'ToPort': INGRESS_PORTS, 'FromPort': INGRESS_PORTS, 'IpProtocol': 'YOUR-PROTOCOL'}
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
                    logging.info("Revoked ranges: {0} from group: {1}".format(cidr,to_revoke))
                        
    except Exception as e:
        logging.error("Error", exc_info = e)

update_security_groups(PrefixId, VpcId, security_group_tag)

