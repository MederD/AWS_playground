import boto3
import json
 
#assigning session variable profile
session = boto3.Session(profile_name = 'development')

#global variables for regions
east = 'us-east-1'
west = 'us-west-2'

#declaring EC2 variable to use session.client
ec2East = session.client('ec2', region_name = east)

def getEC2withTags():
    running_ec2IDs = []

    stateInstances = ec2East.describe_instances(
        Filters = [
            {
                'Name': 'tag:Team', 
                'Values': ['DevOps',]
            }, 
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            }],
    )
    a = stateInstances['Reservations']
    for i in a:
        for j in i['Instances']:
            running_ec2IDs.append(j['InstanceId'])
            
    print('Running EC2 ID: ', running_ec2IDs)
    return running_ec2IDs

# getEC2withTags()

running_instances = getEC2withTags()
def shutdownEc2(running_instances):
    for i in running_instances:
        response = ec2East.stop_instances(
            InstanceIds=[
                i,
            ],
            DryRun=False,
            Force=True
    )
    print(response)

shutdownEc2(running_instances)