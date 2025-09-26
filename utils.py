import json
from datetime import datetime

def read_json(path):
    with open(path, "r") as f:
        return json.load(f)

def write_json(data, path):
    with open(path, 'w') as json_file:
        json.dump(data, json_file, indent=4, default=datetime_serializer)

def datetime_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
