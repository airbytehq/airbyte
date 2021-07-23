#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import logging
from collections import defaultdict
from typing import List, Mapping

from airbyte_cdk.models import AirbyteRecordMessage, ConfiguredAirbyteCatalog
from jsonschema import Draft4Validator, ValidationError


def verify_records_schema(
    records: List[AirbyteRecordMessage], catalog: ConfiguredAirbyteCatalog
) -> Mapping[str, Mapping[str, ValidationError]]:
    """Check records against their schemas from the catalog, yield error messages.
    Only first record with error will be yielded for each stream.
    """
    validators = {}
    for stream in catalog.streams:
        validators[stream.stream.name] = Draft4Validator(stream.stream.json_schema)

    stream_errors = defaultdict(dict)

    for record in records:
        validator = validators.get(record.stream)
        if not validator:
            logging.error(f"Record from the {record.stream} stream that is not in the catalog.")
            continue

        errors = list(validator.iter_errors(record.data))
        for error in errors:
            stream_errors[record.stream][str(error.schema_path)] = error

    return stream_errors
