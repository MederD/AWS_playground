# Find Security Groups with "0.0.0.0/0" and revoke.
import boto3, json

session = boto3.Session(profile_name='development')

east = 'us-east-1'
ec2East = session.client('ec2', region_name = east)

response = ec2East.describe_security_groups(
    Filters=[ { 'Name': 'ip-permission.cidr', 'Values': [ '0.0.0.0/0' ] } ] )
sgs = response['SecurityGroups']
sgwithopenport = []
for i in sgs:
    sgwithopenport.append(i['GroupId'])
print(sgwithopenport)

#revoke 0.0.0.0/0 on ports 443, 80, 22 for the given SG lists
for i in sgwithopenport:
    ports = [80, 22, 443]
    for j in ports:
        response = ec2East.revoke_security_group_ingress(
            CidrIp = '0.0.0.0/0',
            FromPort = j,
            GroupId = i,
            IpProtocol = 'TCP',
            ToPort = j,
        )
print("Revoke success")
