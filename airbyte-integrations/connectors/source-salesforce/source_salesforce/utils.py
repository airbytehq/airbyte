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


def group_by_size(g, buff_size: int, delimiter_size: int = 1):
    assert buff_size > 0
    assert delimiter_size >= 0

    res = []
    cur_buff_size = buff_size

    for item in g:
        item_size = len(item)
        if item_size == 0:
            continue
        if item_size > buff_size:
            raise ValueError(f"item '{item}' size: {item_size} more then buffer size: {buff_size}")

        if cur_buff_size + item_size + delimiter_size > buff_size:
            buff = []
            cur_buff_size = 0
            res.append(buff)

        buff.append(item)
        cur_buff_size += item_size + delimiter_size

    return res
