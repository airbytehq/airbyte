"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import tempfile

from normalization.destination_type import DestinationType
from normalization.transform_catalog.catalog_processor import CatalogProcessor


def test_generating_tables():
    with tempfile.TemporaryDirectory() as tmp_dir:
        catalog_processor = CatalogProcessor(tmp_dir, DestinationType.POSTGRES)
        catalog_processor.process("unit_tests/simple_cac.json", "unused_for_this_test", "target_schema")

        expected_table_names = {
            "key1_bf23fa",
            "key1_bf23fa_ab1",
            "key1_bf23fa_ab2",
            "key1_bf23fa_ab3",
            "key2_24b1bb",
            "key2_24b1bb_ab1",
            "key2_24b1bb_ab2",
            "key2_24b1bb_ab3",
            "long_name_012345678901__567890123456789_24b1bb",
            "long_name_012345678901__567890123456789_bf23fa",
            "long_name_012345678901__90123456789_24b1bb_ab1",
            "long_name_012345678901__90123456789_24b1bb_ab2",
            "long_name_012345678901__90123456789_24b1bb_ab3",
            "long_name_012345678901__90123456789_bf23fa_ab1",
            "long_name_012345678901__90123456789_bf23fa_ab2",
            "long_name_012345678901__90123456789_bf23fa_ab3",
            "long_name_no_conflicts__567890123456789_bf23fa",
            "long_name_no_conflicts__90123456789_bf23fa_ab1",
            "long_name_no_conflicts__90123456789_bf23fa_ab2",
            "long_name_no_conflicts__90123456789_bf23fa_ab3",
            "short_name_24b1bb",
            "short_name_24b1bb_ab1",
            "short_name_24b1bb_ab2",
            "short_name_24b1bb_ab3",
            "short_name_bf23fa",
            "short_name_bf23fa_ab1",
            "short_name_bf23fa_ab2",
            "short_name_bf23fa_ab3",
            "stream_name",
            "stream_name_4858be_ab1",
            "stream_name_4858be_ab2",
            "stream_name_4858be_ab3",
        }

        # for debugging
        for table in catalog_processor.tables_registry:
            print(f'"{table}",')

        assert catalog_processor.tables_registry == expected_table_names
