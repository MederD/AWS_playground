import boto3, json
from botocore.exceptions import ClientError

ec2 = boto3.resource("ec2")
ec2_client = boto3.client("ec2")
VPCId = "" # Write your VPC ID
S3_bucket = "" # Write your S3 bucket

def create_flow_log():
    try:
        response = ec2_client.create_flow_logs(
            ResourceIds=[
                VPCId,
            ],
            ResourceType = 'VPC',
            TrafficType = 'ALL',
            LogDestinationType = 's3',
            LogDestination = S3_bucket
        )
    except Exception as error:
        print(error)

create_flow_log()
