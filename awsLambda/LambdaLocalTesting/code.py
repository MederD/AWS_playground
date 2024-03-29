import json, boto3, traceback, logging, os
from datetime import datetime
from dateutil import tz

# set logging configuration
thelogcount = 1
class ContextFilter( logging.Filter ):
    def filter( self, record ):
        global thelogcount
        record.count = thelogcount
        thelogcount += 1
        return True
logger = logging.getLogger( 'LOGGING' )
logger.setLevel( logging.INFO )
handler = logging.StreamHandler()
formatter = logging.Formatter( '%(asctime)s > %(name)s > %(count)s > %(levelname)s > %(message)s' )
handler.setFormatter( formatter )
logging.getLogger().addHandler( handler )
logger.addFilter( ContextFilter() )

from_zone = tz.gettz('UTC')
to_zone = tz.gettz('America/Phoenix')

sns = boto3.client('sns')
sns_topic = os.environ['sns_topic']

# Get the environment, so we can run appropriate scripts
IS_DEVELOPMENT = os.environ['STAGE'] == 'DEVELOPMENT'

#Getting environment values for troubleshooting
logger.info("Environment value: {}".format(IS_DEVELOPMENT))
logger.info("SNSTopic: {}".format(sns_topic))

def handler(event, context):
    try:
        region = event['region']
        account = event['account']
        eventname = event['detail']['eventName']
        eventtime = event['detail']['eventTime']
        sourceIP = event['detail']['sourceIPAddress']
        requesting = event['detail']['userIdentity']['arn']
        eventsource = event['detail']['eventSource']
        utc = datetime.strptime(eventtime, '%Y-%m-%dT%H:%M:%SZ')
        utc = utc.replace(tzinfo=from_zone)
        local = utc.astimezone(to_zone)
        
        if eventname == 'TerminateInstances' or eventname == 'RunInstances':
            instance_list =  event['detail']['responseElements']['instancesSet']['items']
            for instance in instance_list:
                logger.info('Constructing message for Instance: %s' % instance['instanceId'] )
                message = "Region: {0} \nEventName: {1} \nEventTime: {2} \nInstance: {3} \nSourceIP: {4} \nRequestor: {5} \nAccount: {6} \nEventSource: {7} ".format(region, eventname, local, instance['instanceId'], sourceIP, requesting, account, eventsource)
                if IS_DEVELOPMENT:
                    logger.info("Environment is DEVELOPMENT - testing locally")
                else:
                    logger.info("Environment is: PRODUCTION - sending message to SNS")
                    response = sns.publish(
                            TopicArn = sns_topic,
                            Message = message
                            )
        else:
            logger.info('Event is not TerminateInstances or RunInstances')
          
    except Exception as error:
        logger.error("Error: {}".format(error))

if __name__ == '__main__':
    handler(event, context)
