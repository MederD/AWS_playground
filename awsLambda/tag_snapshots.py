import boto3
import logging, os

#assigning session variable profile and Boto3 configuration
client = boto3.client( 'ec2' )

# Logger cofiguration
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
formatter = logging.Formatter( '%(asctime)s - %(name)s - %(count)s - %(levelname)s - %(message)s' )
handler.setFormatter( formatter )
logging.getLogger().addHandler( handler )
logger.addFilter( ContextFilter() )

# Setting variables for tags
Tag1 = os.environ[ 'Tag1' ]
Tag2 = os.environ[ 'Tag2' ]
Tag3 = os.environ[ 'Tag3' ]
Tag4 = os.environ[ 'Tag4' ]
OwnerId = os.environ[ 'OwnerId' ]

# Creating dictionary for tags
tags_dict =  { 
    'Tag1': Tag1,
    'Tag2': Tag2,
    'Tag3': Tag3,
    'Tag4': Tag4
 }

# Resource variables
caller = client.describe_snapshots
resource = 'Snapshots'
resource_id = 'SnapshotId'

def lambda_handler( event, context ):
    try:
        response = caller( OwnerIds = [ OwnerId ] )
        for i in response[ resource ]:
            ResourceId = i[ resource_id ]
            if 'Tags' in i:
                tags_dict[ 'Name' ] = ResourceId
                tags = i[ 'Tags' ]
                for tag_key in tags_dict.keys():
                    if len( [ key for key in tags if key[ 'Key' ] == tag_key ] ) == 0:
                        logger.info( 'Start adding tags {0} to {1}'.format( tag_key, ResourceId ) )
                        client.create_tags( Resources = [ ResourceId ], Tags = [ { 'Key': tag_key, 'Value': tags_dict[ tag_key ]  } ] )
            else:
                logger.info( 'Start adding tags to {}'.format( ResourceId ) )
                client.create_tags( 
                    Resources = [ ResourceId ],
                    Tags = [ { 'Key': k, 'Value': v } for k, v in tags_dict.items() ]  )
  
    except Exception as error:
        logger.error( error )
