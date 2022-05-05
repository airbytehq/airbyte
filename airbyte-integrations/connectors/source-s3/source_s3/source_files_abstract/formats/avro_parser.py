import logging
from typing import Iterator, TextIO, BinaryIO, Union, Mapping
from fastavro import reader
import fastavro

from .abstract_file_parser import AbstractFileParser
from typing import Any


# mapping from apache avro docs: https://avro.apache.org/docs/current/spec.html#schema_complex
data_type_mapping = {
    "null": "null",
    "boolean": "boolean",
    "int": "integer",
    "long": "integer",
    "float": "number",
    "double": "number",
    "bytes": "string",
    "string": "string",
    "record": "object",
    "enum": "string",
    "array": "array",
    "map": "object",
    "fixed": "string",
}


class AvroParser(AbstractFileParser):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @property
    def is_binary(self) -> bool:
        return True

    @staticmethod
    def parse_data_type(data_type_mapping: dict, avro_schema: dict) -> dict:
        """ Convert data types from avro to json format
        :param data_type_mapping: mapping from avro to json data types
        :param avro_schema: schema comes with the avro file
        :return schema_dict with data types converted from avro to json standards
        """
        schema_dict = {}
        for i in avro_schema["fields"]:
            data_type = i["type"]
            # If field is nullable there will be a list of types and we need to make sure to map the whole list according to data_type_mapping
            if type(data_type) is list:
                datatype_list = []
                for dt in data_type:
                    dt = data_type_mapping[dt]
                    datatype_list.append(dt)
                schema_dict[i["name"]] = datatype_list
            elif type(data_type) is dict:
                raise TypeError(f"nested records not supported")
            elif data_type in data_type_mapping:
                schema_dict[i["name"]] = data_type_mapping[data_type]
            else:
                raise TypeError(f"unsupported data type: {data_type} found in avro file")
        return schema_dict

    @staticmethod
    def get_avro_schema(file: Union[TextIO, BinaryIO]) -> dict:
        """ Extract schema for records
        :param file: file-like object (opened via StorageFile)
        :return schema extracted from the avro file
        """
        avro_reader = fastavro.reader(file)
        schema = avro_reader.writer_schema
        if not schema['type'] == "record":
            unsupported_type = schema['type']
            raise (f"Only record based avro files are supported. Found {unsupported_type}")
        else:
            return schema

    def get_inferred_schema(self, file: Union[TextIO, BinaryIO]) -> dict:
        """ Return schema 
        :param file: file-like object (opened via StorageFile)
        :return: mapping of {columns:datatypes} where datatypes are JsonSchema types
        """
        avro_schema = self.get_avro_schema(file)
        schema_dict = self.parse_data_type(data_type_mapping, avro_schema)
        return schema_dict

    def stream_records(self, file: Union[TextIO, BinaryIO]) -> Iterator[Mapping[str, Any]]:
        """ Stream the data using a generator
        :param file: file-like object (opened via StorageFile)
        :yield: data record as a mapping of {columns:values}
        """
        avro_reader = reader(file)
        rows = (user for user in avro_reader)
        yield from rows
