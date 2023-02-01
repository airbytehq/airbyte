#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from source_sftp_bulk import SourceFtp

source = SourceFtp()


def test_generate_json_schema():
    dtypes = {
        "col1": "int64",
        "col2": "float64",
        "col3": "bool",
        "col4": "object",
        "col5": "string",
        "last_modified": "datetime64[ns]",
    }

    result = source._generate_json_schema(dtypes)
    assert result == {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "properties": {
            "col1": {"type": ["null", "integer"]},
            "col2": {"type": ["null", "number"]},
            "col3": {"type": ["null", "boolean"]},
            "col4": {"type": ["null", "string"]},
            "col5": {"type": ["null", "string"]},
            "last_modified": {"format": "date-time", "type": ["null", "string"]},
        },
        "type": "object",
    }
