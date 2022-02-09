import json, boto3, traceback, logging, os
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO, 
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

# These environment variables are provided in SAM template.
Environment = os.environ['Environment']
Service = os.environ['Service']
AccountNumber = os.environ['AccountNumber']
CreatedBy = 'Auto-remediation'

class ConfigWrapper:

    def __init__(self, config_client):
        self.config_client = config_client    

    def describe_config_rule(self):
        try:
            response = self.config_client.describe_config_rules()
            logger.info("Got data for rules %s.", response['ConfigRules'])
            return response['ConfigRules']

        except ClientError:
            logger.exception("Error: {}".format(traceback.print_exc()))
            raise
    
    def list_tags_for_resource(self):
        try:
            rules = self.describe_config_rule()
            for rule in rules:
                response = self.config_client.list_tags_for_resource( ResourceArn = rule['ConfigRuleArn'] )
                if len(response['Tags']) == 0:
                    logger.info("No tags for rules %s.", rule['ConfigRuleName'])
                    self.config_client.tag_resource( ResourceArn = rule['ConfigRuleArn'],
                        Tags = [
                            { 'Key': 'Name', 'Value': rule['ConfigRuleName'] },
                            { 'Key': 'Service', 'Value': Service },
                            { 'Key': 'Environment', 'Value': Environment },
                            { 'Key': 'AccountNumber', 'Value': AccountNumber },
                            { 'Key': 'CreatedBy', 'Value': AccountNumber }
                        ] )
                else:
                    # Name
                    keys = [tag for tag in response['Tags'] if tag['Key'] == 'Name']
                    if len(keys) == 0:
                        logger.info("Start tagging Name: %s.", rule['ConfigRuleName'])
                        self.config_client.tag_resource(ResourceArn = rule['ConfigRuleArn'], 
                            Tags = [{'Key': 'Name', 'Value': rule['ConfigRuleName'] } ] )
                    # AccountNumber
                    keys = [tag for tag in response['Tags'] if tag['Key'] == 'AccountNumber']
                    if len(keys) == 0:
                        logger.info("Start tagging AccountNumber: %s.", rule['ConfigRuleName'])
                        self.config_client.tag_resource(ResourceArn = rule['ConfigRuleArn'], 
                            Tags = [{'Key': 'AccountNumber', 'Value': AccountNumber } ] )
                    # Service
                    keys = [tag for tag in response['Tags'] if tag['Key'] == 'Service']
                    if len(keys) == 0:
                        logger.info("Start tagging Service: %s.", rule['ConfigRuleName'])
                        self.config_client.tag_resource(ResourceArn = rule['ConfigRuleArn'], 
                            Tags = [{'Key': 'Service', 'Value': Service } ] )
                    # Environment
                    keys = [tag for tag in response['Tags'] if tag['Key'] == 'Environment']
                    if len(keys) == 0:
                        logger.info("Start tagging Environment: %s.", rule['ConfigRuleName'])
                        self.config_client.tag_resource(ResourceArn = rule['ConfigRuleArn'], 
                            Tags = [{'Key': 'Environment', 'Value': Environment } ] )
                    # CreatedBy
                    keys = [tag for tag in response['Tags'] if tag['Key'] == 'CreatedBy']
                    if len(keys) == 0:
                        logger.info("Start tagging CreatedBy: %s.", rule['ConfigRuleName'])
                        self.config_client.tag_resource(ResourceArn = rule['ConfigRuleArn'], 
                            Tags = [{'Key': 'CreatedBy', 'Value': CreatedBy } ] )

            return

        except ClientError:
            logger.exception("Error: {}".format(traceback.print_exc()))
            raise

def lambda_handler(event, context):
    config = ConfigWrapper(boto3.client('config'))
    try: 
        response = config.list_tags_for_resource()

    except Exception as e:
        logger.info("Error: {}".format(traceback.print_exc()))
        return {
            'statusCode': 404,
            'body': json.dumps("Error: {}".format(e))
        }
    else:
        logger.info("Success, tagging complete!")
        return {
            'statusCode': 200,
            'body': json.dumps("Success, tagging complete!")
        }

if __name__ == '__main__':
    lambda_handler(event, context)
