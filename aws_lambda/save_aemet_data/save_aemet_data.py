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
aemet_table = dynamodb.Table('aemet_data')


def save_aemet_data(event, context):
    out = {
        'statusCode': 200
    }
    try:
        body = json.loads(event['body'])
        #logger.info(body)
        
        data = {
            'timestamp': body['timestamp'],
            'hour': Decimal(body.get('hour', 0)),
            'sky_condition': body.get('sky', ''),
            'wind_direction': body.get('wind_direction', ''),
            'warning_level': body.get('warning_level', 0),
            'temperature': Decimal(body.get('temperature', 0)),
            'thermal_sensation': Decimal(body.get('thermal_sensation', 0)),
            'avg_wind_speed': body.get('avg_wind_speed', 0),
            'max_wind_speed': body.get('max_wind_speed', 0),
            'precipitation': body.get('precipitation', 0),
            'snow': body.get('snow', 0),
            'humidity': body.get('relative_humidity', 0),
            'precipitation_probability': body.get('precipitation_probability', 0),
            'snow_probability': body.get('snow_probability', 0),
            'storm_probability': body.get('storm_probability', 0)
        }
        aemet_table.put_item(Item = data)
        
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
