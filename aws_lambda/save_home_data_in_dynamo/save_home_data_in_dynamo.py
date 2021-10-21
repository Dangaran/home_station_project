import json
import boto3
import sys
import logging
import traceback
from decimal import Decimal
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)
dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
temp_hum_table = dynamodb.Table('temperature_humidity_data')

def save_home_data_in_dynamo(event, context):
    out = {
        'statusCode': 200
    }
    try:
        #logger.info(event)
        body = json.loads(event['body'])
        #logger.info(body)
        unique_id = str(uuid.uuid1())
        
        data = {
            'timestamp': body['timestamp'],
            'id': unique_id,
            'temperature': Decimal(body.get('temperature', 0)),
            'pressure': Decimal(body.get('pressure', 0)),
            'humidity': Decimal(body.get('humidity', 0)),
            'people_count': body.get('people_count', 0)
        }
        if 'pic_name' in body: data['pic_name'] = body['pic_name']
            
        temp_hum_table.put_item(Item = data)
        out['body'] = 'Information save correctly in DynamoDB'
    except Exception as exp:
        exception_type, exception_value, exception_traceback = sys.exc_info()
        traceback_string = traceback.format_exception(exception_type, exception_value, exception_traceback)
        err_msg = json.dumps({
            "errorType": exception_type.__name__,
            "errorMessage": str(exception_value),
            "stackTrace": traceback_string
        })
        logger.error(err_msg)
        out['statusCode'] = 404
        out['body'] = 'Something went wrong'
    
    return out
