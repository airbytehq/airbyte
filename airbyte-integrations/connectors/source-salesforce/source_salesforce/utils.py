#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from requests import exceptions, codes
from functools import wraps


def filter_streams(streams_list: list, search_word: str, search_criteria: str):
    search_word = search_word.lower()
    criteria_mapping = {
        "starts with": lambda stream_name: stream_name.startswith(search_word),
        "starts not with": lambda stream_name: not stream_name.startswith(search_word),
        "ends with": lambda stream_name: stream_name.endswith(search_word),
        "ends not with": lambda stream_name: not stream_name.endswith(search_word),
        "contains": lambda stream_name: search_word in stream_name,
        "not contains": lambda stream_name: search_word not in stream_name,
        "exacts": lambda stream_name: search_word == stream_name,
        "not exacts": lambda stream_name: search_word != stream_name,
    }
    new_streams_list = []
    for stream in streams_list:
        if criteria_mapping[search_criteria](stream.lower()):
            new_streams_list.append(stream)
    return new_streams_list


def rate_limit_handler(logger=None):  # TODO
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            try:
                yield from func(*args, **kwargs)
            except exceptions.HTTPError as error:
                error_data = error.response.json()[0]
                error_code = error_data.get("errorCode")
                if error.response.status_code == codes.FORBIDDEN and error_code == "REQUEST_LIMIT_EXCEEDED":
                    if logger:
                        logger.warn(f"API Call limit is exceeded'. Error message: '{error_data.get('message')}'")
                    return None
                raise error

        return wrapped
    return wrapper
