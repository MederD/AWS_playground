# This script will copy snapshot with matching tags from "us-east-1" to "us-west-1".

import boto3, json

session = boto3.Session(profile_name = 'development')

east1 = 'us-east-1'
west1 = 'us-west-1'

ec2East = session.client('ec2', region_name = east1)
ec2West = session.client('ec2', region_name = west1)
 
tag_match = ec2East.describe_snapshots ( Filters = [ {'Name': 'tag:Copy', 'Values': ['True'] } ] )
SnapshotIDs = []
snap = tag_match['Snapshots']
for i in snap:
    SnapshotIDs.append(i['SnapshotId'])
print('Target Snapshot ID: ', SnapshotIDs)

for j in SnapshotIDs:
    response = ec2West.copy_snapshot(
        Description='This is my copied snapshot.',
        DestinationRegion = west1,
        SourceRegion = east1,
        SourceSnapshotId = j,
    )
print(response)