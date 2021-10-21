# This script will work with the below EventBridge rule:
#################################################################
#{                                                              #
#  "source": ["aws.ec2"],                                       #
#  "detail-type": ["EC2 Instance State-change Notification"],   #
#  "detail": {                                                  #
#    "state": ["stopped"],                                      #
#    "instance-id": ["INSTANCE ID", ""]                         #
#  }                                                            #  
#}                                                              #
#################################################################

import json
import boto3
import os

region = 'us-east-1'
ec2 = boto3.client('ec2', region_name=region)

def lambda_handler(event, context):
    try:
        print("Received event:" + json.dumps(event))
        instances=[ event['detail']['instance-id'] ]
        ec2.start_instances(InstanceIds=instances)
        print('Protected instances stopped - starting instance:' + str(instances))
    except Exception as error:
        print(error)
