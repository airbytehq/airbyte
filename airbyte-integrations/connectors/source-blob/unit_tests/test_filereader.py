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


import pyarrow as pa
from source_blob.filereader import FileReader


def test_json_type_to_pyarrow_type():
    # testing all datatypes as laid out here: https://arrow.apache.org/docs/python/api/datatypes.html
    # PyArrow -> Json direction (reverse=True)
    type_tests = (
        ((pa.null(), ), "string"),  # null type
        ((pa.bool_(), ), "boolean"),  # boolean type
        ((pa.int8(), pa.int16(), pa.int32(), pa.int64(), pa.uint8(), pa.uint16(), pa.uint32(), pa.uint64()), "integer"),  # integer types
        ((pa.float16(), pa.float32(), pa.float64(), pa.decimal128(5, 10), pa.decimal256(3, 8)), "number"),  # number types
        ((pa.time32("s"), pa.time64("ns"), pa.timestamp("ms"), pa.date32(), pa.date64()), "string"),  # temporal types
        ((pa.binary(), pa.large_binary()), "string"),  # binary types
        ((pa.string(), pa.utf8(), pa.large_string(), pa.large_utf8()), "string"),  # string types
        ((pa.list_(pa.string()), pa.large_list(pa.timestamp("us"))), "string"),  # array types
        ((pa.map_(pa.string(), pa.float32()), pa.dictionary(pa.int16(), pa.list_(pa.string()))), "string")  # object types
    )
    for pyarrow_types, json_type in type_tests:
        print(pyarrow_types, json_type)
        for typ in pyarrow_types:
            assert FileReader.json_type_to_pyarrow_type(typ, reverse=True) == json_type
