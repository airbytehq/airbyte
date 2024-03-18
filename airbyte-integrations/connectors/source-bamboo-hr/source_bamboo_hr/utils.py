#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Iterable, Iterator, TypeVar, Tuple
import itertools

T = TypeVar('T')

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