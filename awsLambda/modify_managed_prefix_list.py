# import required modules
import pandas, boto3, logging
import numpy, time

# set logging configuration
logging.basicConfig( level=logging.INFO, format='%(levelname)s : %(asctime)s : %(message)s' )
logger = logging.getLogger(__name__)

# set aws session profile
session = boto3.Session(profile_name = 'test')
client = session.client('ec2', region_name = 'ENTER-YOUR-REGION')

# define excel file with data
file_location = 'ENTER-YOUR-FILE-LOCATION'
df = pandas.read_excel(file_location)

# converting excel columns (IP and Store No) to a list
values = df['COLUMN-NAME-1'].values
stores = df['COLUMN-NAME-2'].values
my_list = values.tolist()
my_stores = stores.tolist()

# Removing unnecessary entries
val = my_list.index('STRING-1')
val2 = my_stores.index('STRING-2')
del my_list[val]
del my_stores[val2]

# create CIDR blocks from an IP list
ip_set = [x + '/32' for x in my_list]

# create dictionary for possible use in the future
my_dict = dict(zip(ip_set, my_stores))

# compare new entries with existing and find differences
def compare(PrefixId):
    try:
        existing_entry = []
        response = client.get_managed_prefix_list_entries(PrefixListId = PrefixId, MaxResults = 100)
        results = response['Entries']
        while 'NextToken' in response:
            response = client.get_managed_prefix_list_entries(PrefixListId = PrefixId, NextToken = response['NextToken'])
            results.extend(response['Entries'])
        for i in results:
            existing_entry.append(i['Cidr'])

        diff_list = set(ip_set) - set(existing_entry)
        return diff_list

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
        logging.info("Count of new entries: {0}".format(len(compare(PrefixId))))
        if len(compare(PrefixId)) < 1:
            logging.info("No new entries to add")
        else:
            for i in compare(PrefixId):
                # update list with new entries
                logging.info("Adding new CIDR block {0}".format(i))
                response = client.modify_managed_prefix_list(
                    PrefixListId = PrefixId, 
                    CurrentVersion = get_version(PrefixId),
                    AddEntries = [ { 'Cidr': i }] )

                logging.info('Check state...')
                response = client.describe_managed_prefix_lists(  PrefixListIds = [ PrefixId] )
                if [i['State'] for i in response['PrefixLists']] != ['modify-complete']:
                    logging.info('Sleep...')
                    time.sleep(2)
                else:
                    continue
    except Exception as e:
        logging.error("Error", exc_info = e)

