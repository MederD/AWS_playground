Modified version of [previously](https://github.com/MederD/AWS_playground/blob/main/awsLambda/modify_managed_prefix_list.py) uploaded script. 
This one updates prefix list with "Cidr" and "Description".  
In this case excel data looks like below:  

 | A       | B         | C         | D           |
 |---------|-----------|-----------|-------------|
 |Header 1 |Header 2   |Device Name|Management IP|
 |Some Data|Some Data  |Some Data  |Some Data    | 

```
# import required modules
import pandas, boto3, logging
import numpy, time

# set logging configuration
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# set aws session profile
session = boto3.Session(profile_name = 'YOUR-PROFILE-NAME')
client = session.client('ec2', region_name = 'YOUR-REGION')

# define excel file with data
file_location = 'YOUR-FILE-LOCATION'
df = pandas.read_excel(file_location)

# converting excel columns D and C to a list
values = df['Unnamed: 3'].values
stores = df['Unnamed: 2'].values
my_list = values.tolist()
my_stores = stores.tolist()

# Removing unnecessary entries. 'Management IP' from column 3 and 'Device Name' from column 2.
val = my_list.index('Management IP')
val2 = my_stores.index('Device Name')
del my_list[val]
del my_stores[val2]

# Need to add '/32' to create CIDR blocks from an IP list. 
ip_set = [x + '/32' for x in my_list]

# create dictionary for to compare with the existing managed prefix entries, which has format {'Cidr': x, 'Description': x}.
my_dict = [{'Cidr': k, 'Description': v} for k, v in zip(ip_set, my_stores)]

# compare two lists of dictionaries
def compare_lists(PrefixId):
    try:
        response = client.get_managed_prefix_list_entries(PrefixListId = PrefixId, MaxResults = 100)
        results = response['Entries']
        while 'NextToken' in response:
            response = client.get_managed_prefix_list_entries(PrefixListId = PrefixId, NextToken = response['NextToken'])
            results.extend(response['Entries'])
 
        res = [i for i in my_dict if i not in results]
        return res

    except Exception as e:
        logging.error("Error", exc_info = e)

# get managed_prefix_list version number
def get_version(PrefixId):
    try:
        response = client.describe_managed_prefix_lists( PrefixListIds = [ PrefixId ] )
        version = [str(i['Version']) for i in response['PrefixLists']]
        version_string = "".join(version)
        return int(version_string)
    except Exception as e:
        logging.error("Error", exc_info = e)

# update managed prefix list
def update_managed_prefix_list(PrefixId):
    try:
        logging.info("Count of new entries: {0}".format(len(compare_lists(PrefixId))))
        if len(compare_lists(PrefixId)) < 1:
            logging.info("No new entries to add")
        else:
            for element in compare_lists(PrefixId):
                # update list with new entries
                logging.info("Adding cidr: {0}, with description: {1}".format(element.get('Cidr'), element.get('Description')))
                try:
                    response = client.describe_managed_prefix_lists(  PrefixListIds=[ PrefixId] )
                    if [i['State'] for i in response['PrefixLists']] == ['modify-in-progress']:
                        logging.info('Sleep 10 ...')
                        time.sleep(10)
                    else:
                        response = client.modify_managed_prefix_list(
                            PrefixListId = PrefixId, 
                            CurrentVersion = get_version(PrefixId),
                            AddEntries = [ {
                                'Cidr': element.get('Cidr'),
                                'Description': element.get('Description')
                            },] )
                except:
                    pass
    except Exception as e:
        logging.error("Error", exc_info = e)
```

