import boto3
import json
 
#assigning session variable profile
session = boto3.Session(profile_name = 'development')

#global variables for regions
east = 'us-east-1'
west = 'us-west-2'

#declaring EC2 variable to use session.client
ec2East = session.client('ec2', region_name = east)

#Get instance IDs
def getEC2withTags():
    ec2IDs = []

    stateInstances = ec2East.describe_instances()
    a = stateInstances['Reservations']
    
    for i in a:
        for j in i['Instances']:
            ec2IDs.append(j['InstanceId'])
            
    print('EC2 IDs: ', ec2IDs)
    return ec2IDs

#Stopping all running instances
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

#Starting all stopped instances
stopped_instances = getEC2withTags()
def startEc2(stopped_instances):
    for i in stopped_instances:
        response = ec2East.start_instances(
            InstanceIds=[
                i,
            ],
            DryRun=False
        )
    print(response)

startEc2(stopped_instances)