import unittest
import json, os
import code
from code import handler

class TestLambdaHandler(unittest.TestCase):
    def setUp(self):
  
        os.environ['STAGE'] = 'DEVELOPMENT'
        os.environ['sns_topic'] = 'my-sns-topic'
        
        # Print the values of the environment variables for troubleshooting
        print('STAGE:', os.environ['STAGE'])
        print('sns_topic:', os.environ['sns_topic'])

    def test_handler(self):
        # Define the triggering event
        event = {
            'region':'us-east-1',
            'account': '123456789',
            'detail':{
                'region' : 'us-east-1',
                'account' : '123456789',
                'eventName' : 'TerminateInstances',
                'eventTime' : '2019-11-11T21:29:54Z',
                'sourceIPAddress' : 'AWS Internal',
                'userIdentity': {
                    'arn': 'arn:aws:iam::123456789:user/User'
                    },
                'eventSource': 'ec2.amazonaws.com',
                'requestParameters': {
                    'instancesSet': {
                        'items': [
                            {
                                'instanceId': 'i-00000000000001'
                            }
                        ]
                    }
                },
                'responseElements': {
                    'instancesSet': {
                        'items': [
                        {
                            'instanceId': 'i-00000000000001'
                        }
                        ]
                    }
                }
            }
        }   

        # Invoke the lambda_handler() function
        result= handler(event, None)

        # Ensure the function returns the expected output
        self.assertEqual(result, 'Success')

if __name__ == '__main__':
    unittest.main()
