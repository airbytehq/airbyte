#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Mapping


def transform_properties(record: Mapping[str, Any], dict_key: str = "properties") -> Mapping[str, Any]:
    """
    Transform nested `properties` object.
    Move unique named entities into `name`, `value` to handle normalization.
    EXAMPLE INPUT:
    {
        {...},
        "properties": {
            "some_unique_name1": {
                "id": "some_id",
                "type": "relation",
                "relation": []
            },
            "some_unique_name2": {
                "id": "some_id",
                "type": "date",
                "date": null
            },
            ...
        },
        {...}
    }

    EXAMPLE OUTPUT:
    {
        {...},
        "properties": [
            {
                "name": "some_unique_name1",
                "value": {
                    "id": "some_id",
                    "type": "relation",
                    "relation": []
                }
            },
            {
                "name": "some_unique_name2",
                "value": {
                    "id": "some_id",
                    "type": "date",
                    "date": null
                }
            },
        ],
        {...}
    }

    """
    properties = record.get(dict_key)
    if properties:
        new_properties = []
        for k, v in properties.items():
            new_properties.append({"name": k, "value": v})
        record[dict_key] = new_properties
    yield record
