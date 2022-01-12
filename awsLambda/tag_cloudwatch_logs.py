import json, boto3, traceback, logging, os
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO, 
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S')
logger = logging.getLogger()

# Environmental variables
CreatedBy = os.environ['CreatedBy']
Environment = os.environ['Environment']
AccountNumber = os.environ['AccountNumber']
Service = os.environ['Service']

client = boto3.client('logs')

def lambda_handler(event, context):
    try:
        # Get the complete log list
        log_list = []
        response = client.describe_log_groups() # >>> default limit is 50
        results = response['logGroups']
        while 'nextToken' in response:
            response = client.describe_log_groups(nextToken = response['nextToken'])
            results.extend(response['logGroups'])
        for i in results:
            log_list.append(i['logGroupName'])
        # List tags and start tagging
        for logs in log_list:
            list_tags = client.list_tags_log_group(logGroupName = logs)
            if len(list_tags['tags']) == 0:
                start_tagging = client.tag_log_group(
                    logGroupName = logs,
                    tags = {
                        'Name': logs,
                        'CreatedBy': CreatedBy,
                        'Environment': Environment,
                        'Service': Service,
                        'AccountNumber': AccountNumber
                    }
                )
            else:
                # Name
                tags = [tag for tag in list_tags['tags'] if tag == 'Name']
                if len(tags) == 0:
                    logger.info('Start tagging Name: %s' % (logs) )
                    start_tagging = client.tag_log_group( logGroupName = logs, tags = { 'Name': logs })
                # Environment
                tags = [tag for tag in list_tags['tags'] if tag == 'Environment']
                if len(tags) == 0:
                    logger.info('Start tagging Environment: %s' % (logs) )
                    start_tagging = client.tag_log_group( logGroupName = logs, tags = { 'Environment': Environment })
                # Service
                tags = [tag for tag in list_tags['tags'] if tag == 'Service']
                if len(tags) == 0:
                    logger.info('Start tagging Service: %s' % (logs) )
                    start_tagging = client.tag_log_group( logGroupName = logs, tags = { 'Service': Service })
                # AccountNumber
                tags = [tag for tag in list_tags['tags'] if tag == 'AccountNumber']
                if len(tags) == 0:
                    logger.info('Start tagging AccountNumber: %s' % (logs) )
                    start_tagging = client.tag_log_group( logGroupName = logs, tags = { 'AccountNumber': AccountNumber })
                # CreatedBy
                tags = [tag for tag in list_tags['tags'] if tag == 'CreatedBy']
                if len(tags) == 0:
                    logger.info('Start tagging CreatedBy: %s' % (logs) )
                    start_tagging = client.tag_log_group( logGroupName = logs, tags = { 'CreatedBy': CreatedBy })

    except Exception as e:
        logger.info("Error: {}".format(traceback.print_exc()))
        return {
            'statusCode': 404,
            'body': json.dumps("Error: {}".format(e))
        }
    else:
        logger.info("Success!")
        return {
            'statusCode': 200,
            'body': json.dumps("Success, tagging complete!")
        }

