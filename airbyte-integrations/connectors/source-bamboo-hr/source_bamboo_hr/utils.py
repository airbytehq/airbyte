#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Iterable, Iterator, TypeVar, Tuple, Mapping, Any
import itertools

T = TypeVar('T')

def get_json_schema_for_field_type(field_type: str) -> Mapping[str, Any]:
    """
    Returns the JSON schema for the given BambooHR field type.
    """
    # As per https://documentation.bamboohr.com/docs/field-types
    default_field_schema = {"type": ["string", "null"]}
    if field_type == "currency":
        currency_field_schema = {
            "type": ["object", "null"],
            "properties": {
                "value": {"type": ["string"]},
                "currency": {"type": ["string"]},
            },
        }
        return currency_field_schema
    else:
        return default_field_schema

def chunk_iterable(iterable: Iterable[T], chunk_size: int) -> Iterator[Tuple[T, ...]]:
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
