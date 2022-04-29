from typing import Iterator, TextIO, BinaryIO, Union, Mapping
from fastavro import reader
import fastavro

from .abstract_file_parser import AbstractFileParser
from typing import Any

# TODO: DONE - complete list of mappings
# TODO: DONE - Adding avro class to the spec
# TODO: DONE - Handle multiple data types in the conversion
# TODO: DONE (doesn't take any additional columns) - check arguments avro reader
# TODO: DONE - Install everything from readme and run spec to setup the integration
# TODO: Test locally with different files
# TODO: Write unit tests
# TODO: Write integration tests
# TODO: Update docs

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
            elif data_type in data_type_mapping:
                schema_dict[i["name"]] = data_type_mapping[data_type]
            else:
                raise TypeError(f"unsupported data type: {data_type} found in avro file")
        return schema_dict

    @staticmethod
    def get_avro_schema(file) -> dict:
        avro_reader = fastavro.reader(file)
        schema = avro_reader.writer_schema
        if not schema['type'] == "record":
            unsupported_type = schema['type']
            raise TypeError(f"Only record based avro files are supported. Found {unsupported_type}")
        else:
            return schema

    def get_inferred_schema(self, file: Union[TextIO, BinaryIO]) -> dict:
        """
        :param file: file-like object (opened via StorageFile)
        :return: mapping of {columns:datatypes} where datatypes are JsonSchema types
        """
        avro_schema = self.get_avro_schema(file)
        schema_dict = self.parse_data_type(data_type_mapping, avro_schema)
        return schema_dict

    def stream_records(self, file: Union[TextIO, BinaryIO]) -> Iterator[Mapping[str, Any]]:
        """
        :param file: file-like object (opened via StorageFile)
        :yield: data record as a mapping of {columns:values}
        """
        avro_reader = reader(file)
        rows = (user for user in avro_reader)
        yield from rows
