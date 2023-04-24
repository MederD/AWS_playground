import logging
import boto3

logging.basicConfig(level=logging.INFO)

session = boto3.Session(profile_name = 'profile-name')
client = session.client('lambda', region_name = 'region-name')

try:
    lambda_list = []
    response = client.list_functions(FunctionVersion='ALL')
    results = response[ 'Functions' ]
    while 'NextMarker' in response:
        response = client.list_functions( Marker = response[ 'NextMarker' ], FunctionVersion='ALL')
        results.extend( response[ 'Functions' ] )
    for i in results:
        lambda_list.append( i[ 'FunctionName' ] )
    logging.info(f"Total functions: {len(lambda_list)}")

    for i in lambda_list:
        res = client.get_function_concurrency(FunctionName=i)
        if 'ReservedConcurrentExecutions' in res:
            logging.info(f"function: {i}, reserved: {res['ReservedConcurrentExecutions']}")

except Exception as e:
    logging.exception(e)    

