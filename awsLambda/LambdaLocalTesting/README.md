## AWS lambda python local testing

We will test our lambda code written in python locally, lambda code is triggered by EventBridge rule and sends message to SNS topic.

First we need to install [python-lambda-local](https://pypi.org/project/python-lambda-local/). For this we will create *"requirements.txt"* file within our project folder.
Then run:
```
python -m pip install -r requirements.txt
```
This is our sample lambda code, the file name is *"code.py"*:
```python
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
        item_count = event['detail']['requestParameters']['instancesSet']['items'][0]['minCount']
        logger.info('Count of instances: %s' % item_count )
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
```
where *"region", "account", "eventname", "eventtime", "sourceIP", "requesting details"* and *"eventsource"* are loaded to function from triggering event. Then, message will be constructed and sent to SNS topic if it matches the environment.
For environments, we need to create *"env.json"* file with our environment values for local testing. Our *"env.json"* file will look like this:
```json
{

    "sns_topic":"arn-of-your-sns-topic",
    "STAGE":"DEVELOPMENT"

}
```
Also, we need to create *"event.json"* file for trigger, it will look like this:
```json
{
   "id":"7bf73129-1428-4cd3-a780-95db273d1602",
   "detail-type":"AWS API Call via CloudTrail",
   "source":"aws.ec2",
   "account":"123456789012",
   "time":"2019-11-11T21:29:54Z",
   "region":"us-east-1",
   "resources":[
      ""
   ],
   "detail":{
      "eventVersion": "1.08",
      "userIdentity": {...},
      "eventTime":"",
      etc.
   }
}
```
Then, finally when everything is ready, we can run the command:
```
python-lambda-local -f handler -e env.json code.py event.json
```


