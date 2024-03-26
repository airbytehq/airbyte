#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level

# Define the global logger function
def log(level: Level, message: str):
    log_message = AirbyteLogMessage(level=level, message=message)
    print(AirbyteMessage(type="LOG", log=log_message).json(exclude_unset=True))
        
def find_id_by_name(data, key_name, name_to_find, id_key):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == key_name and value == name_to_find:
                return data.get(id_key, None)
            else:
                found_id = find_id_by_name(value, key_name, name_to_find, id_key)
                if found_id:
                    return found_id
    elif isinstance(data, list):
        for item in data:
            found_id = find_id_by_name(item, key_name, name_to_find, id_key)
            if found_id:
                return found_id
    return None