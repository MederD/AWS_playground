import boto3, json

#assigning session variable profile
session = boto3.Session(profile_name='development')

#global variables for regions
east = 'us-east-1'
west = 'us-west-2'

#declaring EC2 variable to use session.client
ec2East = session.client('ec2', region_name = east)

def instance_info():
    ec2IDs = []
    ec2AMIs = []
    get_info = ec2East.describe_instances()
    a = get_info['Reservations']
    
    for i in a:
        #print(i['Instances'])
        for j in i['Instances']:
            ec2IDs.append(j['ImageId'])
            ec2AMIs.append(j['InstanceId'])
            
    print('EC2 ID: ', ec2IDs)
    print('EC2 AMI: ', ec2AMIs)   
    return (ec2AMIs, ec2IDs)     

listofEC2s, listofAMIs = instance_info()

def updateTags(listofEC2s):
    for i in listofEC2s:
        response = ec2East.create_tags(
            Resources = [i,],
            Tags = [{'Key': 'Day', 'Value': 'Saturday',}, {'Key': 'Team', 'Value': 'DevOps',},],
        )
    return response

updateTags(listofEC2s)


