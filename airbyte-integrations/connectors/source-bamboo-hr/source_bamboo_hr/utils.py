#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import itertools

def convert_custom_reports_fields_to_list(custom_reports_fields: str) -> list:
    return custom_reports_fields.split(",") if custom_reports_fields else []


def validate_custom_fields(custom_fields, available_fields):
    denied_fields = []
    for custom_field in custom_fields:
        has_access_to_custom_field = any(available_field.get("name") == custom_field for available_field in available_fields)
        if not has_access_to_custom_field:
            denied_fields.append(custom_field)

    return denied_fields

def chunk_iterable(iterable, chunk_size):
    """
    Generates chunks of the given iterable with the specified size.

    Args:
        iterable: An iterable to be chunked.
        chunk_size: The size of each chunk.

    Yields:
        Chunks of the iterable, each up to the specified size.
    """
    # An iterator for the input iterable
    iterator = iter(iterable)
    
    while True:
        # Take the next chunk_size elements from the iterator
        chunk = tuple(itertools.islice(iterator, chunk_size))
        
        if not chunk:
            # If the chunk is empty, stop the loop
            break
        
        yield chunk