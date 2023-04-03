import boto3
import datetime, os
import logging
import dateutil.parser

logger = logging.getLogger()
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s [%(module)s.%(funcName)s:%(lineno)d] %(message)s", datefmt="%H:%M:%S"
)
logger.setLevel(os.getenv('log_level', logging.INFO))

resource = boto3.resource('iam')
client = boto3.client("iam")
client_sns = boto3.client("sns")
sns_topic = os.environ['sns_topic']
accountId = os.environ['accountId']

# Check expiration for the access key, based on created date.
def days_till_expire(last_created, max_age):
    if type(last_created) is str:
        last_created_date=dateutil.parser.parse(last_created).date()
    elif type(last_created) is datetime.datetime:
        last_created_date=last_created.date()
    else:
        return -99999
    expires = (last_created_date + datetime.timedelta(max_age)) - datetime.date.today()
    return(expires.days)

# Get the password maximum age policy
def get_max_password_age(client):
    try: 
        response = client.get_account_password_policy()
        return response['PasswordPolicy']['MaxPasswordAge']
    except Exception as e:
        logger.exception(e)
        print("Unexpected error in get_max_password_age: %s" + e.message) 

# Main function
def handler(event, context):
    try:
        now = datetime.date.today()
        logger.info("Today's date is: {}".format(now))

        max_age = get_max_password_age(client)

        for user in resource.users.all():
            Metadata = client.list_access_keys(UserName=user.user_name)
            if Metadata['AccessKeyMetadata'] != []:
                try:
                    for key in user.access_keys.all():
                        message = ""
                        unmasked = key.access_key_id
                        KeyId = len(unmasked[:-4])*"*"+unmasked[-4:]
                        Status = key.status
                        key_expires = days_till_expire(key.create_date, max_age)
                        if Status == 'Active':
                            if key_expires < 0:
                                message = (':rotating-light-red: ATTENTION! Account: {}, User: {}, KeyId: {}, Status: {}, Expired: {} days ago'.format(accountId, user.user_name, KeyId, Status, (key_expires * -1)))
                                logger.info(message)
                                client_sns.publish(
                                    TargetArn = sns_topic,
                                    Message = message,
                                    Subject = '--- ACCESS KEYS EXPIRATION REPORT ---'
                                )
                            elif key_expires > 0:
                                message = ('Account: {}, User: {}, KeyId: {}, Status: {}, Expires in: {} days'.format(accountId, user.user_name, KeyId, Status, abs(key_expires * -1)))
                                logger.info(message)
                                client_sns.publish(
                                    TargetArn = sns_topic,
                                    Message = message,
                                    Subject = '--- ACCESS KEYS EXPIRATION REPORT ---'
                                )
                except Exception as e:
                    logger.exception(e)
            else:
                logger.info("Skipping users with no access keys: {}".format(user.user_name))

    except Exception as e:
        logger.exception(e)
