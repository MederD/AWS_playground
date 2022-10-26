import boto3
import logging, os

#assigning session variable profile and Boto3 configuration
client = boto3.client( 'lambda' )

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
Tag1Var = os.environ[ 'Tag1' ]
Tag2Var = os.environ[ 'Tag2' ]

# Creating dictionary for tags
tags_dict =  { 
    'Tag1': Tag1Var,
    'Tag2': Tag2Var
}

# Resource variables
caller = client.list_functions
resource = 'Functions'
resource_id = 'FunctionName'

def lambda_handler( event, context ):
    try:
        lambda_list = []
        response = caller()
        results = response[ resource ]
        while 'NextMarker' in response:
            response = caller( Marker = response[ 'NextMarker' ] )
            results.extend( response[ resource ] )
        for i in results:
            lambda_list.append( i[ resource_id ] )
        for _function in lambda_list:
            response = client.get_function( FunctionName = _function )
            logger.info('--- FunctionName:{}'.format( _function ) )
            tags_dict[ 'Name' ] = _function
            if 'Tags' not in response:
                logger.info( 'Start adding all tags to {}'.format( _function ) )
                client.tag_resource( 
                    Resource = response[ 'Configuration' ][ 'FunctionArn' ],
                    Tags = tags_dict  )   
            else:
                tags = response[ 'Tags' ].keys()
                for tag_key in tags_dict.keys():
                    if len( [ key for key in tags if key == tag_key ] ) == 0:
                        logger.info( 'Start adding tags {0} to {1}'.format( tag_key, _function ) )
                        client.tag_resource( Resource = response[ 'Configuration' ][ 'FunctionArn' ], Tags = { tag_key: tags_dict[ tag_key ]  } )
  
    except Exception as error:
        logger.error( error )
