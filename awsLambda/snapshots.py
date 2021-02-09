# Take snapshot of volumes with specific tags
import boto3, json
session = boto3.Session(profile_name='development')

east = 'us-east-1'
ec2East = session.client('ec2', region_name = east)

#filter both matching tag and in-use volumes in that region
response = ec2East.describe_volumes(
        Filters=[
            {
                'Name': 'tag:TechnicalTeam',
                'Values': [
                    'DevOps',
                ]
            }, 
            {
                'Name': 'status',
                'Values': [
                    'in-use',
                ]
            },
        ],
    )
volumeIDs=[]
vol=response['Volumes']
for i in vol:
    volumeIDs.append(i['VolumeId'])
print(volumeIDs)

#assign retention and take snapshot
retention = 3
for i in volumeIDs:
    response = ec2East.create_snapshot(
        Description='DevOps Team Snapshots',
        VolumeId=i,
        TagSpecifications=[
            {
                'ResourceType': 'snapshot',
                'Tags': [
                    {
                        'Key': 'Retention',
                        'Value': str(retention)
                    },
                    {
                        'Key': 'TechnicalTeam',
                        'Value': 'DevOps'
                    },
                ]
            },
        ],
    )