# -*- coding: utf-8 -*-
from _decimal import Decimal
from datetime import datetime, date

from bson.decimal128 import Decimal128
from bson.objectid import ObjectId
from bson.dbref import DBRef
from flask.json import JSONEncoder
from pymongo.cursor import Cursor

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, bytes):
            return str(obj, 'utf-8')
        elif isinstance(obj, Cursor):
            return [self.default(i) for i in obj]
        elif isinstance(obj, Decimal128):
            return obj.to_decimal()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, (datetime, date)):
            return obj.strftime(DATETIME_FORMAT)
        elif isinstance(obj, DBRef):
            return str(obj.id)
        return JSONEncoder.default(self, obj)
