#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


def filter_streams_by_criteria(streams_list: list, search_word: str, search_criteria: str):
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
