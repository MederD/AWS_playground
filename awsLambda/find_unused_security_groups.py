import boto3, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

session = boto3.Session(profile_name='PROFILE_NAME')
client = session.client('ec2', region_name='us-east-1')
ec2 = session.resource('ec2', region_name='us-east-1')

def sg_list():
    """
    :return: list of security group ids
    """
    try:
        return [sg.id for sg in ec2.security_groups.all()]
    except Exception as error:
        logger.info("Error: {}".format(error))
        return []

def ni_list(sg_ids):
    try:
        """
        :return: set of network interface ids filtered by security group ids
        """
        filtered_network_interfaces = set()
        response = client.describe_network_interfaces(Filters=[{'Name': 'group-id', 'Values': sg_ids}])
        results = response['NetworkInterfaces']

        while 'NextMarker' in response:
            response = client.describe_network_interfaces(
                Filters=[{'Name': 'group-id', 'Values': sg_ids}],
                Marker=response['NextMarker'])
            results.extend(response['NetworkInterfaces'])

        for i in results:
            for group in i['Groups']:
                filtered_network_interfaces.add(group['GroupId'])
        
        return filtered_network_interfaces

    except Exception as error:
        logger.info("Error: {}".format(error))
        return set()

def main():
    try:
        """
        :return: list of security groups with no matching network interfaces
        """
        sg_ids = sg_list()
        ni_list_data = ni_list(sg_ids)

        result = [sg_id for sg_id in sg_ids if sg_id not in ni_list_data]

        logger.info(result)
    except Exception as error:
        logger.info("Error: {}".format(error))

main()
