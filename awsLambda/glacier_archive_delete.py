import json, boto3, traceback, logging
from botocore.exceptions import ClientError

thelogcounts = { 'INFO':0, 'ERROR':0, 'DEBUG':0}

class ContextFilter(logging.Filter):
    def filter(self, record):
        global thelogcounts
        record.count = thelogcounts[record.levelname]
        thelogcounts[record.levelname] += 1
        return True

logging.basicConfig(level=logging.INFO, 
    format='%(asctime)s- %(levelname)s- %(count)s- %(message)s',
    datefmt='%H:%M:%S')

logger = logging.getLogger(__name__)
logger.addFilter(ContextFilter())

client = boto3.client('glacier')


vaultName = 'YOUR-VAULT-NAME'
def main():
    try:
        a = open('YOUR-OUTPUT-FILE', 'r')
        b = a.readlines()

        new_list = []
        for line in b:
            for item in line.strip().split():
                new_list.append(item)
        for i in new_list:
           
            logger.info('Deleting: Archive Id- %s' % i )
        
            response = client.delete_archive(
                vaultName = vaultName,
                archiveId = i
            )
        
    except Exception:
        logger.exception('ERROR: Archive Id- %s' % i)
        raise
main()
        