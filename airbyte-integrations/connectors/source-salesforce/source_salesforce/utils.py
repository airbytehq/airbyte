#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


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


def filter_streams_for_test(streams_list: list, search_word: str, search_criteria: str):
    if search_word.isupper():
        search_word = search_word.lower()

    new_streams_list = []
    for stream in streams_list:
        stream = stream.lower()
        if search_criteria == "starts with" and stream.startswith(search_word):
            new_streams_list.append(stream)
        elif search_criteria == "starts not with" and not stream.startswith(search_word):
            new_streams_list.append(stream)
        elif search_criteria == "ends with" and stream.endswith(search_word):
            new_streams_list.append(stream)
        elif search_criteria == "ends not with" and not stream.endswith(search_word):
            new_streams_list.append(stream)
        elif search_criteria == "contains" and search_word in stream:
            new_streams_list.append(stream)
        elif search_criteria == "not contains" and search_word not in stream:
            new_streams_list.append(stream)
        elif search_criteria == "exacts" and search_word == stream:
            new_streams_list.append(stream)
        elif search_criteria == "not exacts" and search_word != stream:
            new_streams_list.append(stream)

    return new_streams_list
