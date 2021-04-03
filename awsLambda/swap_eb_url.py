# Python script to swap ElasticBeanstalk environment cnames.
# In this case 'blue' deployment environment name need to have word 'blue' in it.

import boto3, json

client       = boto3.client('elasticbeanstalk')

# get list of all applications
get_app_name = client.describe_applications()
names        = [name['ApplicationName'] for name in get_app_name['Applications']]

# get list of environments based on application name
for i in names:
    get_env_name = client.describe_environments(ApplicationName = i)
    env_names    = [env_name['EnvironmentName'] for env_name in get_env_name['Environments']]
    cnames       = [cname['CNAME'] for cname in get_env_name['Environments']]

# filter out environment name which meets our requirements, in this case if name has 'blue' in it.
blue  = []
green = []
for j in env_names:
    if 'blue' in str(j):
        blue.append(j)
    else:
        green.append(j)

str_blue   = ' '.join(map(str, blue))
str_green  = ' '.join(map(str, green))

# swap cnames from blue env to green env
client.swap_environment_cnames(
    SourceEnvironmentName       = str_blue,
    DestinationEnvironmentName  = str_green
)

