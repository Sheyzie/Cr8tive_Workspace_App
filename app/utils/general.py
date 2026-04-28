import json
from decimal import Decimal
from datetime import datetime
import uuid

class DecimalDatetimeUUIDEncoder(json.JSONEncoder):
    '''
    Class to parse Decimal, UUID, Datetime, Set object in test
    '''
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, uuid.UUID) or isinstance(obj, datetime):
            return str(obj)
        if obj == uuid.UUID or obj == datetime:
            return str(obj)
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)
    
def get_json(data, indent=3):
    '''
    Helper function to get dict response in json
    '''
    return json.dumps(data, indent=indent, cls=DecimalDatetimeUUIDEncoder)


def is_valid_date(date_string, date_format):
    try:
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False
    
def matches_regex(value, pattern, partial=False):
    import re

    if value is None:
        return False
    if partial:
        return re.search(pattern, str(value)) is not None
    return re.fullmatch(pattern, str(value)) is not None