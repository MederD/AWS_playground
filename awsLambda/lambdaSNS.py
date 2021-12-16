"""
Customizing codepipeline norifications 
"""
import json
import boto3
import datetime
import time
from datetime import datetime, timedelta

sns = boto3.client('sns')
pipe = boto3.client('codepipeline')

def lambda_handler(event, context):
    pipeline = event["detail"]["pipeline"] 
    executionId = event["detail"]["execution-id"] 
    executionStatus = event["detail"]["state"] 
    executionTime = event["time"]
    region = event["region"]

    get_message = pipe.list_pipeline_executions(
            pipelineName = pipeline,
            maxResults = 1
        )
    for i in get_message['pipelineExecutionSummaries']:
        # executionId = i['pipelineExecutionId']
        status = i['status']
        date = (i['startTime']).date()
        for j in i['sourceRevisions']:
            CommitSummary= j['revisionSummary']
    
    message = "Region: {0} \npipeline: {1} \nexecutionId: {2} \nStatus: [{3}] \nDate: {4} \nCommitSummary: {5}".format(region, pipeline, executionId, executionStatus, date, CommitSummary)
    response = sns.publish(
            TopicArn = "TOPIC-ARN",
            Message = message
            )
    return {
      'statusCode': 200,
      'body': json.dumps('Success!')
}

