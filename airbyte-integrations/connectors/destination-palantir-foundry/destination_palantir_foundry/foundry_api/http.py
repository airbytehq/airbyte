from functools import wraps
from typing import Dict


# Methods
GET = "GET"
POST = "POST"


def build_path(path, parameters: Dict):
    for key, value in parameters.items():
        path = path.replace("{" + key + "}", value)
    
    return path
