#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from pathlib import Path

from source_file.source import SourceFile

HERE = Path(__file__).parent.absolute()


def test_csv_with_utf16_encoding():

    config_local_csv_utf16 = {
        "dataset_name": "AAA",
        "format": "csv",
        "reader_options": '{"encoding":"utf_16"}',
        "url": f"{HERE}/../integration_tests/sample_files/test_utf16.csv",
        "provider": {"storage": "local"},
    }
    expected_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "properties": {
            "header1": {"type": ["string", "null"]},
            "header2": {"type": ["number", "null"]},
            "header3": {"type": ["number", "null"]},
            "header4": {"type": ["boolean", "null"]},
        },
        "type": "object",
    }

    catalog = SourceFile().discover(logger=logging.getLogger("airbyte"), config=config_local_csv_utf16)
    stream = next(iter(catalog.streams))
    assert stream.json_schema == expected_schema
