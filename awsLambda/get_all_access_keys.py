import boto3, json

iam = boto3.client('iam')

response = iam.list_users(
    PathPrefix  = '/',
    MaxItems    = 10)
# print(response)
users = [user['UserName'] for user in response['Users']]
print(users)
for i in users:
    paginator = iam.get_paginator('list_access_keys')
    for metadata in paginator.paginate(UserName = i):
        keys = [key['AccessKeyId'] for key in metadata['AccessKeyMetadata']]
        print(keys)

