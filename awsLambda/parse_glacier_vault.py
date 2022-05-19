import json, traceback, logging
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO, 
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S')
logger = logging.getLogger()

def create():
    try:
        with open('OUTPUT-ARCHIVE-FILE-JSON', 'r') as f:
            with open("YOUR-OUTPUT-FILE", "w",  encoding='utf-8') as outfile:
                data = json.load(f)
                datalist = data['ArchiveList']
                for i in datalist[0:100]: # If the file is big, better to output in ranges
                    line = i['ArchiveId']
                    outfile.write(line + "\n") 
        f.close()
        outfile.close()
    except Exception:
        logger.exception(i)
        raise
create()