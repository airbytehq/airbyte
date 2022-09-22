from typing import Any, Dict


def transform_custom_fields(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Method to detect custom fields that start with 'cf_' from chargbee models.
    Args:
        record:
        {
            ...
            'cf_custom_fields': 'some_value',
            ...
        }

    Returns:
        record:
        {
            ...
            'custom_fields': [{
                'name': 'cf_custom_fields',
                'value': some_value'
            }],
            ...
        }
    """

    custom_fields = [key for key in record.keys() if key.startswith('cf_')]
    new_custom_fields = []

    if custom_fields:
        for custom_field in custom_fields:
            new_custom_fields.append({"name": custom_field, "value": record[custom_field]})

        record['custom_fields'] = new_custom_fields

    yield record
