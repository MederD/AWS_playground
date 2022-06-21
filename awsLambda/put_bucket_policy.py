import boto3, json, traceback, logging, os
from botocore.exceptions import ClientError
from pprint import pprint

logging.basicConfig(level=logging.INFO, 
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S')
logger = logging.getLogger()

client = boto3.client('s3')

def list_buckets():
    no_policy = []
    response = client.list_buckets()
    for i in response['Buckets']:
        try:
            bucket = i['Name']
            logger.info("Bucket: {}".format(bucket))
            response = client.get_bucket_policy(
                Bucket = bucket
            )
        except Exception as NoSuchBucketPolicy:
            no_policy.append(bucket)
            response = client.put_bucket_policy(
                Bucket=bucket,
                Policy='{"Version": "2012-10-17", "Statement": [{ "Sid": "AllowSSLRequestsOnly","Effect": "Deny","Principal": "*", "Action": "s3:*", "Resource": ["arn:aws:s3:::'+bucket+'", "arn:aws:s3:::'+bucket+'/*" ], "Condition": {"Bool": {"aws:SecureTransport": "false"}} } ]}'
            )
    print(len(no_policy))
list_buckets()