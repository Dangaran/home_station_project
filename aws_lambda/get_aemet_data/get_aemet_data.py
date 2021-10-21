import json
import boto3
import sys
import logging
import traceback
from time import time
from decimal import Decimal
from boto3.dynamodb.conditions import Attr
from .functions.DecimalEncoder import DecimalEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)
dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
aemet_table = dynamodb.Table('aemet_data')

def get_aemet_data(event, context):
    out = {
        'statusCode': 200
    }
    try:
        # get dates from body
        if event['body'] is not None:
            body = json.loads(event['body'])
        else:
            body = {}
        logger.info(body)
        
        # if there are not dates in body set to 1 week
        time_now = int(time())
        date_start = body['date_start'] if 'date_start' in body else (time_now - 604800)
        date_end = body['date_end'] if 'date_end' in body else time_now
        
        # scan table for that dates using pagination to get all data
        response = aemet_table.scan(
            FilterExpression=Attr('timestamp').gte(date_start) & Attr('timestamp').lte(date_end)
            )
        aemet_data = response['Items']
        
        while 'LastEvaluatedKey' in response:
            response = table.scan(FilterExpression=Attr('timestamp').gte(date_start) & Attr('timestamp').lte(date_end), ExclusiveStartKey=response['LastEvaluatedKey'])
            aemet_data.extend(response['Items'])
        
        out['body'] = json.dumps(aemet_data, cls=DecimalEncoder)
        
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
