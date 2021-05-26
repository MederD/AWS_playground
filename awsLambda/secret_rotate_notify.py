import boto3
import base64
from botocore.exceptions import ClientError
import datetime
import time
from datetime import datetime, timedelta

#----------------------------------------------------
now = datetime.utcnow()
only_date = now.date()
print ("Today's date is:", (only_date))
deadline = 3
#------------------------------------------------------

secret_name = "demo-secret"
region_name = "us-east-1"
secret_ARN  = []
source_email = '<< enter SES verified source email'
dest_email = '<< enter SES verified dest email'

ses_client = boto3.client('ses')
session = boto3.session.Session()
client = session.client(
    service_name='secretsmanager',
    region_name=region_name
)

def list_secrets():
    try:
        response = client.list_secrets(
            MaxResults = 5,
            Filters=[
                {
                    'Key': 'name',
                    'Values': [
                        secret_name,
                    ]
                }
            ]
        )

        for arn in response['SecretList']:
            secret_ARN.append(arn['ARN'])
    except Exception as error:
        print(error)

list_secrets()

d = []
def describe_secret():
    try:
        for i in secret_ARN:
            response = client.describe_secret(
                SecretId = i
            )
            d.append(response)
            if response['RotationEnabled']:
                for j in d:
                    LastChangedDate =  (j['LastChangedDate']).date()
                    next_date = LastChangedDate + timedelta(30)
                    print ("Next rotation date is:", next_date)
                    # print("LastChangedDate:", LastChangedDate)

                    if (next_date - only_date) < timedelta(deadline):
                        print("Sending notification email to", dest_email)
                        response = ses_client.send_email(
                            Source = source_email,
                            Destination={
                            'ToAddresses': [ dest_email ],
                            },
                            Message={
                                'Subject': {
                                    'Data': 'ACM renewal notification!'
                                    },
                                'Body': {
                                    'Text': {
                                        'Data': 'Please renew your certificate, it will expire soon.',
                                        },
                                    'Html': {
                                        'Data': 'Please renew your certificate, it will expire soon.'
                                        }
                                    }
                            },
                            Tags=[
                            {
                                'Name': 'Team',
                                'Value': 'DevOps'
                                },
                            ],
                            )
                    else:
                        print ("Rotation date not due yet.")

            else:
                print("Rotation is not enabled")
    except Exception as error:
        print(error)
describe_secret()
