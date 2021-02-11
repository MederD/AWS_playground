# Filter snapshots by tags and delete if older than retention days.
import boto3, json
import datetime
from datetime import datetime, timedelta
from boto3 import ec2

session = boto3.Session(profile_name = 'development')
east = 'us-east-1'
ec2East = session.client('ec2', region_name = east)

now = datetime.now()
# print(now)
retention_days = 1

ebsAllSnapshots = ec2East.describe_snapshots ( Filters = [ {'Name': 'tag:TechnicalTeam', 'Values': ['DevOps'] } ] )
snap = (ebsAllSnapshots['Snapshots'])
# print(snap)
for i in snap:
    snap_time = i['StartTime'].replace(tzinfo=None)
    # print('snapshot time: ', snap_time)
    if (now - snap_time) > timedelta(retention_days):
        print ("Snapshot is older than configured retention of %d days" % (retention_days))
        print("[Deleted Snapshot]: %s" % i['SnapshotId'])
        ec2East.delete_snapshot(SnapshotId = i['SnapshotId'])
    else:
        print ("Snapshot is newer than configured retention of %d days so we keep it" % (retention_days))  
