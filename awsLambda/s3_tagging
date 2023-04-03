"""
This Lambda function parses the non-compliance message from SNS and checks if the compliance is NON_COMPLIANT. 
If it is, it extracts the name of the non-compliant S3 bucket from the resource field. 
It then uses the get_bucket_tagging method from the boto3 client object to retrieve the existing tags on the bucket. 
It iterates over each of the specified tags and checks if they are present on the bucket. 
If any tags are missing, it uses the put_bucket_tagging method to add them to the bucket.
"""
import boto3
import json
import logging
import os

""" configure logging """
logger = logging.getLogger()
logging.basicConfig(
    format = "[%(asctime)s] %(levelname)s [%(module)s.%(funcName)s:%(lineno)d] %(message)s", 
    datefmt = "%H:%M:%S"
)
logger.setLevel(os.getenv('log_level', logging.INFO))

""" Initialize the boto3 S3 resource and client """
s3 = boto3.resource('s3')
client = boto3.client('s3')
client_sns = boto3.client('sns')

def handle_exception(e):
    """
    Handles exceptions by logging the error and sending a message to an SNS topic.

    :param e: The exception to handle.
    """
    account_id = os.environ['AccountId']
    function_name = os.environ['AWS_LAMBDA_FUNCTION_NAME']
    log_group_name = os.environ['AWS_LAMBDA_LOG_GROUP_NAME']
    sns_topic = os.environ['sns_topic']
    construct_message = f":rotating-light-red: Lambda: {function_name}, in account: {account_id} has failed, check the log: {log_group_name}"
    client_sns.publish(
        TargetArn = sns_topic,
        Message = construct_message,
        Subject = '--- LAMBDA FAILURE ---'
    )

def lambda_handler(event, context):
    """
    Tags a non-compliant S3 bucket when triggered by an SNS event.

    :param event: The triggering event.
    :type event: dict
    :param context: The context in which the function is running.
    :type context: LambdaContext
    """
    try:
        # Parse the non-compliance message
        message = json.loads(event['Records'][0]['Sns']['Message'])
        logger.info(f'Message received: {message}')
        # Check if the compliance type is NON_COMPLIANT
        if message['status'] == 'NON_COMPLIANT':
            # Extract the name of the non-compliant bucket
            bucket_name = message['resource']
            # Define the tags that should be present on each bucket
            all_tags = {
                'tag1': bucket_name,
                'tag2': os.environ['value2'],
                'tag3': os.environ['value3'],
                'tag4': os.environ['value4'],
                'tag5': os.environ['value5']
            }
            # Retrieve the existing tags on the bucket
            existing_tags = {}
            try:
                response = client.get_bucket_tagging(Bucket = bucket_name)
                existing_tags = {tag['Key']: tag['Value'] for tag in response['TagSet']}
                logger.info(f'Existing tags: {existing_tags}')
            except Exception as e:
                logger.error(f'An error occurred: {e}')
                handle_exception(e)
                
            # Create a list of all the tags that should be applied to the bucket
            tag_set = [{'Key': k, 'Value': v} for k, v in existing_tags.items()]
            for tag_key, tag_value in all_tags.items():
                if tag_key not in existing_tags:
                    tag_set.append({'Key': tag_key, 'Value': tag_value})
                    logger.info(f'Added tag {tag_key} to bucket {bucket_name}')

            # Apply all the tags to the bucket at once
            client.put_bucket_tagging(
                Bucket = bucket_name,
                Tagging = {
                    'TagSet': tag_set
                }
            )

        else:
            logger.info('Do nothing, status: COMPLIANT')
    except Exception as e:
        logger.error(f'An error occurred: {e}')
        handle_exception(e)
