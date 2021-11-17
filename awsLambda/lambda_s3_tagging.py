import boto3
from botocore.exceptions import ClientError

region = "us-east-1"
client = boto3.client('s3', region_name = region)

# -----------------LIST ALL THE BUCKETS
def list_buckets():
    try:
      response = client.list_buckets()
      buckets = []
      for i in response['Buckets']:
          buckets.append(i['Name'])
      return(buckets)
    except Exception as error:
        print(error)

# ------------------LIST TAGS FOR THE BUCKETS & LIST BUCKET WITHOUT tag:Name
list_buckets = list_buckets()
def get_bucket_tagging(list_buckets):
    try:
        for i in list_buckets:
          response = client.get_bucket_tagging(
            Bucket= i
          )
          tag_keys = {}
          tag_items = tag_keys.items()
          for j in response['TagSet']:
            tag_keys.update(j)
          no_name_bucket = []
          if tag_keys['Key'] != 'Name':
            no_name_bucket.append(i)
            return(no_name_bucket)
    except Exception as error:
        print(error)

# --------------------------------- CREATE/UPDATE TAGS
# get_bucket_tagging = get_bucket_tagging(list_buckets) >>> IF there is no tag:Name
# def put_bucket_tagging(get_bucket_tagging):
def put_bucket_tagging(list_buckets):
    try:
        # for i in get_bucket_tagging:  >>> IF there is no tag:Name
        for i in list_buckets:
          response = client.put_bucket_tagging(
            Bucket = i,
            Tagging = {
              'TagSet': [
                {
                  'Key': 'Name',
                  'Value': i
                },
                {
                  'Key': 'CreatedBy',
                  'Value': 'Med'
                },
              ]
            }
           )
    except Exception as error:
        print(error)
# put_bucket_tagging(get_bucket_tagging)  >>> IF there is no tag:Name
put_bucket_tagging(list_buckets)