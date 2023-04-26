#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import tracemalloc

import pytest
import requests_mock
from conftest import generate_stream
from source_salesforce.streams import BulkIncrementalSalesforceStream


@pytest.mark.parametrize(
    "n_records, first_size, first_peak",
    (
        (1000, 0.4, 1),
        (10000, 1, 2),
        (100000, 4, 9),
        (200000, 7, 19),
    ),
    ids=[
        "1k recods",
        "10k records",
        "100k records",
        "200k records",
    ],
)
def test_memory_download_data(stream_config, stream_api, n_records, first_size, first_peak):
    job_full_url: str = "https://fase-account.salesforce.com/services/data/v53.0/jobs/query/7504W00000bkgnpQAA"
    stream: BulkIncrementalSalesforceStream = generate_stream("Account", stream_config, stream_api)
    content = b'"Id","IsDeleted"'
    for _ in range(n_records):
        content += b'"0014W000027f6UwQAI","false"\n'

    with requests_mock.Mocker() as m:
        m.register_uri("GET", f"{job_full_url}/results", content=content)
        tracemalloc.start()
        for x in stream.read_with_chunks(*stream.download_data(url=job_full_url)):
            pass
        fs, fp = tracemalloc.get_traced_memory()
        first_size_in_mb, first_peak_in_mb = fs / 1024**2, fp / 1024**2

        assert first_size_in_mb < first_size
        assert first_peak_in_mb < first_peak
