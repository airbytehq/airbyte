#!/usr/bin/env python3
import collections
import decimal
import json
import re
import time
from datetime import datetime
from decimal import Decimal

import logging

LOGGER = logging.getLogger()


def validate_config(config):
    """Validates config"""
    errors = []
    required_config_keys = [
        's3_bucket_name',
        's3_access_key_id',
        's3_secret_access_key',
        's3_bucket_path'
    ]

    # Check if mandatory keys exist
    for k in required_config_keys:
        if not config.get(k, None):
            errors.append("Required key is missing from config: [{}]".format(k))

    return errors


def float_to_decimal(value):
    """Walk the given data structure and turn all instances of float into
    double."""
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, list):
        return [float_to_decimal(child) for child in value]
    if isinstance(value, dict):
        return {k: float_to_decimal(v) for k, v in value.items()}
    return value


def add_metadata_columns_to_schema(schema_message):
    """Metadata _sdc columns according to the stitch documentation at
    https://www.stitchdata.com/docs/data-structure/integration-schemas#sdc-columns

    Metadata columns gives debugrmation about data injections
    """
    extended_schema_message = schema_message
    extended_schema_message['schema']['properties']['_sdc_batched_at'] = {'type': ['null', 'string'],
                                                                          'format': 'date-time'}
    extended_schema_message['schema']['properties']['_sdc_deleted_at'] = {'type': ['null', 'string']}
    extended_schema_message['schema']['properties']['_sdc_extracted_at'] = {'type': ['null', 'string'],
                                                                            'format': 'date-time'}
    extended_schema_message['schema']['properties']['_sdc_primary_key'] = {'type': ['null', 'string']}
    extended_schema_message['schema']['properties']['_sdc_received_at'] = {'type': ['null', 'string'],
                                                                           'format': 'date-time'}
    extended_schema_message['schema']['properties']['_sdc_sequence'] = {'type': ['integer']}
    extended_schema_message['schema']['properties']['_sdc_table_version'] = {'type': ['null', 'string']}

    return extended_schema_message


def add_metadata_values_to_record(record_message, schema_message):
    """Populate metadata _sdc columns from incoming record message
    The location of the required attributes are fixed in the stream
    """
    extended_record = record_message['record']
    extended_record['_sdc_batched_at'] = datetime.now().isoformat()
    extended_record['_sdc_deleted_at'] = record_message.get('record', {}).get('_sdc_deleted_at')
    extended_record['_sdc_extracted_at'] = record_message.get('time_extracted')
    extended_record['_sdc_primary_key'] = schema_message.get('key_properties')
    extended_record['_sdc_received_at'] = datetime.now().isoformat()
    extended_record['_sdc_sequence'] = int(round(time.time() * 1000))
    extended_record['_sdc_table_version'] = record_message.get('version')

    return extended_record


def remove_metadata_values_from_record(record_message):
    """Removes every metadata _sdc column from a given record message
    """
    cleaned_record = record_message['record']
    cleaned_record.pop('_sdc_batched_at', None)
    cleaned_record.pop('_sdc_deleted_at', None)
    cleaned_record.pop('_sdc_extracted_at', None)
    cleaned_record.pop('_sdc_primary_key', None)
    cleaned_record.pop('_sdc_received_at', None)
    cleaned_record.pop('_sdc_sequence', None)
    cleaned_record.pop('_sdc_table_version', None)

    return cleaned_record


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


def flatten(dictionary, parent_key=False, separator='_'):
    """
    Turn a nested dictionary into a flattened dictionary
    :param dictionary: The dictionary to flatten
    :param parent_key: The string to prepend to dictionary's keys
    :param separator: The string used to separate flattened keys
    :return: A flattened dictionary
    """

    items = []
    for key, value in dictionary.items():
        new_key = str(parent_key) + separator + key if parent_key else key
        if isinstance(value, collections.MutableMapping):
            if not value.items():
                items.append((new_key, None))
            else:
                items.extend(flatten(value, new_key, separator).items())
        elif isinstance(value, list):
            if len(value):
                listCollection = []
                for k, v in enumerate(value):
                    if isinstance(v, collections.MutableMapping):
                        items.extend(flatten({str(k): v}, new_key).items())
                    else:
                        listCollection.append(v)
                if len(listCollection): items.append((new_key, listCollection))
            else:
                items.append((new_key, None))
        else:
            items.append((new_key, value))
    return dict(items)


def camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
