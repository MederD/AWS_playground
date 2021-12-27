import json
import boto3
from botocore.exceptions import ClientError
import traceback
import os

client = boto3.client('ecs')

# These environment variables are provided in SAM template.
Environment = os.environ['Environment']
Service = os.environ['Service']
AccountNumber = os.environ['AccountNumber']
CreatedBy = os.environ['CreatedBy']

def lambda_handler(event, context):
    try:
        response = client.list_task_definitions()
        for i in response['taskDefinitionArns']:
            response = client.list_tags_for_resource(
                resourceArn = i
            )
            all_tags = response['tags']
            matches = [tag for tag in all_tags if tag['key'] == 'Name']
            if len(matches) == 0:
                response = client.tag_resource(
                    resourceArn = i,
                    tags = [{'key': 'Name', 'value': i.split("/")[1] }]
                )
            matches = [tag for tag in all_tags if tag['key'] == 'Service']
            if len(matches) == 0:
                        response = client.tag_resource(
                            resourceArn = i,
                            tags = [{'key': 'Service', 'value': Service }]
                        )
            matches = [tag for tag in all_tags if tag['key'] == 'Environment']
            if len(matches) == 0:
                        response = client.tag_resource(
                            resourceArn = i,
                            tags = [{'key': 'Environment', 'value': Environment }]
                        )
            matches = [tag for tag in all_tags if tag['key'] == 'AccountNumber']
            if len(matches) == 0:
                        response = client.tag_resource(
                            resourceArn = i,
                            tags = [{'key': 'AccountNumber', 'value': AccountNumber }]
                        )
            matches = [tag for tag in all_tags if tag['key'] == 'CreatedBy']
            if len(matches) == 0:
                        response = client.tag_resource(
                            resourceArn = i,
                            tags = [{'key': 'CreatedBy', 'value': CreatedBy }]
                        )
                   
        response = client.list_clusters()
        for j in response['clusterArns']:
            response = client.list_tags_for_resource(
                resourceArn = j
            )
            all_cluster_tags = response['tags']
            cluster_matches = [t for t in all_cluster_tags if t['key'] == 'Name']
            if len(cluster_matches) == 0:
                        response = client.tag_resource(
                            resourceArn = j,
                            tags = [{'key': 'Name', 'value': j.split("/")[1] }]
                        )
            cluster_matches = [t for t in all_cluster_tags if t['key'] == 'Service']
            if len(cluster_matches) == 0:
                        response = client.tag_resource(
                            resourceArn = j,
                            tags = [{'key': 'Service', 'value': Service }]
                        )
            cluster_matches = [t for t in all_cluster_tags if t['key'] == 'Environment']
            if len(cluster_matches) == 0:
                        response = client.tag_resource(
                            resourceArn = j,
                            tags = [{'key': 'Environment', 'value': Environment }]
                        )
            cluster_matches = [t for t in all_cluster_tags if t['key'] == 'CreatedBy']
            if len(cluster_matches) == 0:
                        response = client.tag_resource(
                            resourceArn = j,
                            tags = [{'key': 'CreatedBy', 'value': CreatedBy }]
                        )
            cluster_matches = [t for t in all_cluster_tags if t['key'] == 'AccountNumber']
            if len(cluster_matches) == 0:
                        response = client.tag_resource(
                            resourceArn = j,
                            tags = [{'key': 'AccountNumber', 'value': AccountNumber }]
                        )
            
                             
    except Exception as error:
        traceback.print_exc()
        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }