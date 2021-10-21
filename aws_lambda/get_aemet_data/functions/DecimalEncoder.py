# Info from https://forums.aws.amazon.com/message.jspa?messageID=689708
import json
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
   def default(self, o):
        if isinstance(o, Decimal):
            if o % 1 > 0:
               return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)