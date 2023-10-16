#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import itertools
import traceback


def format_exception(exception: Exception) -> str:
    return str(exception) + "\n" + "".join(traceback.TracebackException.from_exception(exception).format())


def create_chunks(iterable, batch_size):
    """A helper function to break an iterable into chunks of size batch_size."""
    it = iter(iterable)
    chunk = tuple(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it, batch_size))
