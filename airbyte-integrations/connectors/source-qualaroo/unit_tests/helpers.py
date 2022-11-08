#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


NO_SLEEP_HEADERS = {
    "x-rate-limit-api-token-max": "1",
    "x-rate-limit-api-token-remaining": "1",
    "x-rate-limit-api-key-max": "1",
    "x-rate-limit-api-key-remaining": "1",
}


def read_all_records(stream):
    records = []
    slices = stream.stream_slices(sync_mode=None)
    for slice in slices:
        for record in stream.read_records(sync_mode=None, stream_slice=slice):
            records.append(record)
    return records
