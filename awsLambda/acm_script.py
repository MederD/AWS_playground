import boto3, json
from botocore.exceptions import ClientError
import datetime
import time
from datetime import datetime, timedelta

#----------------------------------------------------
now = datetime.utcnow()
only_date = now.date()
print ("Today's date is:", (only_date))
deadline = 30
#------------------------------------------------------

acm_client = boto3.client('acm')
ses_client = boto3.client('ses')

acm_list = []
source_email = '<< enter SES verified source email'
dest_email = '<< enter SES verified dest email'

#------------------------------------
def list_acm():
    try:
        response = acm_client.list_certificates(
            CertificateStatuses=['ISSUED']
        )
        for i in response['CertificateSummaryList']:
            acm_list.append(i['CertificateArn'])
    except Exception as error:
        print(error)

list_acm()

#------------------------------------------
def describe_acm():
    try:
        for acm in acm_list:
            response = acm_client.describe_certificate(
                CertificateArn = acm
            )
            dt = response['Certificate']
            CertARN = acm
            ExpireDate = (dt['NotAfter']).date()
            RenewalEligibility = dt['RenewalEligibility']
            if RenewalEligibility == 'INELIGIBLE':
                if (ExpireDate - only_date) < timedelta(deadline):
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
                        print ("Certificate is older than configured deadline of %d days" % (deadline))

    except Exception as error:
        print(error)
describe_acm()
