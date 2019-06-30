import json
from bson import ObjectId



class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

json_encoder = JSONEncoder()

async def mongoObjectToJson(request, response):
    test = response
    result = json_encoder.encode(response.body)
    return test

__version__ = "0.0.1"  
__all__ = [
    "mongoObjectToJson"
]