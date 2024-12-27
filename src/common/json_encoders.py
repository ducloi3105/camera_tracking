import json
from bson import ObjectId
from datetime import datetime, date


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, o: any) -> any:
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, ObjectId):
            return str(o)
        return super(CustomJsonEncoder, self).default(o)
