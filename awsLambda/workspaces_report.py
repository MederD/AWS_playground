import boto3
import os
from datetime import datetime, timedelta

# Constants
THRESHOLD_DAYS = 15

def handler(event: dict, context: dict) -> None:
    """
    AWS Lambda handler function to generate a report on AWS Workspace usage and send notifications.
    
    Parameters:
        event (dict): The Lambda event.
        context (dict): The Lambda context.
    """
    # Create AWS clients
    aws = boto3.session.Session()
    client = aws.client('workspaces')
    client_sns = boto3.client('sns')
    topic = os.environ['sns_topic']

    # Retrieve list of workspaces
    workspaces = retrieve_workspaces(client)

    # Process workspaces and send notifications
    running_count, non_used_count, threshold_count = process_workspaces(client_sns, topic, workspaces)

    # Prepare and send summary message
    message = "Total Workspaces: {}, Never Been Used: {}, Past threshold: {} haven't been used in the last {} days".format(
        running_count, non_used_count, threshold_count, THRESHOLD_DAYS)

    client_sns.publish(TargetArn=topic, Message=message, Subject='Workspaces report')

def retrieve_workspaces(client: boto3.client) -> list:
    """
    Retrieve the list of all workspaces.
    
    Parameters:
        client (boto3.client): The AWS Workspaces client.
    
    Returns:
        list: List of workspace dictionaries.
    """
    workspaces = []
    response = client.describe_workspaces()

    while 'Workspaces' in response:
        workspaces.extend(response['Workspaces'])
        if 'NextToken' in response:
            response = client.describe_workspaces(NextToken=response['NextToken'])
        else:
            break

    return workspaces

def process_workspaces(client_sns: boto3.client, topic: str, workspaces: list) -> tuple:
    """
    Process each workspace, calculate usage, and send notifications.
    
    Parameters:
        client_sns (boto3.client): The AWS SNS client.
        topic (str): The SNS topic to publish messages to.
        workspaces (list): List of workspace dictionaries.
    
    Returns:
        tuple: A tuple containing running_count, non_used_count, and threshold_count.
    """
    running_count = 0
    non_used_count = 0
    threshold_count = 0

    for workspace in workspaces:
        workspace_id = workspace['WorkspaceId']
        user_name = workspace['UserName']
        connection_status = workspace.get('LastKnownUserConnectionTimestamp')

        days, last_used_date_v1 = calculate_usage(connection_status)

        if days < 0:
            non_used_count += 1
        if days > THRESHOLD_DAYS:
            threshold_count += 1

        running_count += 1
        send_usage_notification(client_sns, topic, days, workspace_id, user_name, last_used_date_v1)

    return running_count, non_used_count, threshold_count

def calculate_usage(connection_status: str) -> tuple:
    """
    Calculate usage and determine last used date.
    
    Parameters:
        connection_status (str): Last known user connection timestamp.
    
    Returns:
        tuple: A tuple containing days and last_used_date_v1.
    """
    if connection_status:
        last_used_date = connection_status.replace(tzinfo=None)
        last_used_date_v1 = last_used_date.date()

        today = datetime.now()
        delta = today - last_used_date
        days = delta.days
    else:
        days = -1
        last_used_date_v1 = None

    return days, last_used_date_v1

def send_usage_notification(client_sns: boto3.client, topic: str, days: int, workspace_id: str, user: str, last_used_date_v1: datetime) -> None:
    """
    Send usage notification for a workspace.
    
    Parameters:
        client_sns (boto3.client): The AWS SNS client.
        topic (str): The SNS topic to publish messages to.
        days (int): Number of days since last usage.
        workspace_id (str): Workspace ID.
        user (str): Workspace user name.
        last_used_date_v1 (datetime): Last used date of the workspace.
    """
    message = "Days: {}, WorkspaceId: {}, UserName: {}, LastUsedDate: {}".format(
        days, workspace_id, user, last_used_date_v1)

    client_sns.publish(TargetArn=topic, Message=message, Subject='Workspaces report')

if __name__ == "__main__":
    handler(None, None)  # This allows you to test the handler function locally if needed
