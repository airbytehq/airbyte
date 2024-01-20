#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level

# Define the global logger function
def log(level: Level, message: str):
    log_message = AirbyteLogMessage(level=level, message=message)
    print(AirbyteMessage(type="LOG", log=log_message).json(exclude_unset=True))


def find_id_by_name(data, name_to_find):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'name' and value == name_to_find:
                return data.get('id', None)
            else:
                found_id = find_id_by_name(value, name_to_find)
                if found_id:
                    return found_id
    elif isinstance(data, list):
        for item in data:
            found_id = find_id_by_name(item, name_to_find)
            if found_id:
                return found_id
    return None