import boto3, json
import datetime
import time
from datetime import datetime, timedelta
import inspect

boto3.setup_default_session(profile_name='development')

resource = boto3.resource('iam')
client = boto3.client("iam")

#----------------------------------------------------
now = datetime.utcnow()
only_date = now.date()
print ("Today's date is:", (only_date))
retention_days = 90
#------------------------------------------------------

KEY = 'LastUsedDate'

# ---------- LIST USERS AND ACCESS-KEYS
for user in resource.users.all():
    Metadata = client.list_access_keys(UserName=user.user_name)
    if Metadata['AccessKeyMetadata'] :
        for key in user.access_keys.all():
            AccessId = key.access_key_id
            Status = key.status
            LastUsed = client.get_access_key_last_used(AccessKeyId=AccessId)
            if (Status == "Active"):
                if KEY in LastUsed['AccessKeyLastUsed']:
                    time = LastUsed['AccessKeyLastUsed'][KEY]
                    just_time = time.date()
                    print ("User: " , user.user_name ,  ",Key: " , AccessId , ",AK Last Used: " , just_time)
                else:
                    print ("User: ", user.user_name  , ",Key: ",  AccessId , ",Key is Active but NEVER USED")
            else:
                print ("User: ", user.user_name  , ",Key: ",  AccessId , ",Keys is InActive")
    else:
        print ("User: ", user.user_name  , ",No KEYS for this USER") 

# ---------- INACTIVATE KEYS IF OLDER THAN RETENTION DAY
for user in resource.users.all():
    Metadata = client.list_access_keys(UserName=user.user_name)
    if Metadata['AccessKeyMetadata'] :
        for key in user.access_keys.all():
            AccessId = key.access_key_id
            Status = key.status
            LastUsed = client.get_access_key_last_used(AccessKeyId=AccessId)
            if (Status == "Active"):
                if KEY in LastUsed['AccessKeyLastUsed']:
                    time = LastUsed['AccessKeyLastUsed'][KEY]
                    just_time = time.date()
            if (only_date - just_time) > timedelta(retention_days):
                    print ("Key is older than configured retention of %d days" % (retention_days))
                    client.update_access_key(
                    AccessKeyId = AccessId,
                    UserName = user.user_name,
                    Status='Inactive',)
            else:
                    print ("Key is younger than configured retention of %d days" % (retention_days))