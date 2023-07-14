#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
import random
import string
from random import randrange
from typing import Any, Mapping

from avro import datafile, io, schema
from source_s3.source_files_abstract.formats.avro_parser import AvroParser

from .abstract_test_parser import AbstractTestParser
from .conftest import TMP_FOLDER

simple_schema_str = """{
    "type": "record",
    "name": "sampleAvro",
    "namespace": "AVRO",
    "fields": [
        {"name": "name", "type": "string"},
        {"name": "age", "type": ["int", "null"]},
        {"name": "address", "type": ["float", "null"]},
        {"name": "street", "type": "float"},
        {"name": "valid", "type": "boolean"}
    ]
}"""

nested_records_schema_str = """{
    "type": "record",
    "name": "sampleAvroNested",
    "namespace": "AVRO",
    "fields": [
        {"name": "lastname", "type": "string"},
        {"name": "address","type": {
                        "type" : "record",
                        "name" : "AddressUSRecord",
                        "fields" : [
                            {"name": "streetaddress", "type": "string"},
                            {"name": "city", "type": "string"}
                        ]
                    }
        }
    ]
}"""

nested_schema_output = {"address": {"type": ["object", "null"],
                                    "city": {"type": ["string", "null"]},
                                    "streetaddress": {"type": ["string", "null"]},
                                    },
                        "lastname": {"type": ["string", "null"]}}

master_schema = {"address": {"type": ["number", "null"]},
                 "age": {"type": ["integer", "null"]},
                 "name": {"type": ["string", "null"]},
                 "street": {"type": ["number", "null"]},
                 "valid": {"type": ["boolean", "null"]}
                 }


class TestAvroParser(AbstractTestParser):
    filetype = "avro"

    @classmethod
    def generate_avro_file(cls, out_file, num_rows: int) -> str:
        """Creates an avro file and saves to tmp folder to be used by test cases
        :param schema_str: valid avro schema as a string
        :param out_file: name of file to be created
        :param num_rows: number of rows to be generated
        :return: string with path to the file created
        """
        filename = os.path.join(TMP_FOLDER, out_file + "." + cls.filetype)
        parsed_schema = schema.parse(simple_schema_str)
        rec_writer = io.DatumWriter(parsed_schema)
        file_writer = datafile.DataFileWriter(open(filename, "wb"), rec_writer, parsed_schema)
        for _ in range(num_rows):
            data = {}
            data["name"] = "".join(random.choice(string.ascii_letters) for i in range(10))
            data["age"] = randrange(-100, 100)
            data["address"] = random.uniform(1.1, 100.10)
            data["street"] = random.uniform(1.1, 100.10)
            data["valid"] = random.choice([True, False])
            file_writer.append(data)
        file_writer.close()
        return filename

    @classmethod
    def generate_nested_avro_file(cls, out_file, num_rows: int) -> str:
        """Creates an avro file and saves to tmp folder to be used by test cases
        :param schema_str: valid avro schema as a string
        :param out_file: name of file to be created
        :param num_rows: number of rows to be generated
        :return: string with path to the file created
        """
        filename = os.path.join(TMP_FOLDER, out_file + "." + cls.filetype)
        parsed_schema = schema.parse(nested_records_schema_str)
        rec_writer = io.DatumWriter(parsed_schema)
        file_writer = datafile.DataFileWriter(open(filename, "wb"), rec_writer, parsed_schema)
        for _ in range(num_rows):
            data = {}
            data["lastname"] = "".join(random.choice(string.ascii_letters) for i in range(10))
            data["address"] = {
                "streetaddress": "".join(random.choice(string.ascii_letters) for i in range(10)),
                "city": "".join(random.choice(string.ascii_letters) for i in range(10))
            }
            file_writer.append(data)
        file_writer.close()
        return filename

    @classmethod
    def cases(cls) -> Mapping[str, Any]:
        """
        return test cases
        """
        cases = {}
        # test basic file with data type conversions
        cases["simple_test"] = {
            "AbstractFileParser": AvroParser(format=cls.filetype),
            "filepath": cls.generate_avro_file("test_file", 1000),
            "num_records": 1000,
            "inferred_schema": master_schema,
            "line_checks": {},
            "fails": [],
        }
        # test file with 0 records. Will pass but not ingest anything
        cases["test_zero_rows"] = {
            "AbstractFileParser": AvroParser(format=cls.filetype),
            "filepath": cls.generate_avro_file("test_file_zero_rows", 0),
            "num_records": 0,
            "inferred_schema": master_schema,
            "line_checks": {},
            "fails": [],
        }

        # test for avro schema with nested records. This will pass as all nested records are returned as one string
        cases["test_nested_records"] = {
            "AbstractFileParser": AvroParser(format=cls.filetype),
            "filepath": cls.generate_nested_avro_file("test_nested_records", 10),
            "num_records": 10,
            "inferred_schema": nested_schema_output,
            "line_checks": {},
            "fails": [],
        }

        return cases
