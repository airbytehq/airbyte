from destination_redshift_py.field import DataType

VARCHAR = "VARCHAR"
TIMESTAMP_WITHOUT_TIME_ZONE = "TIMESTAMP WITHOUT TIME ZONE"
MAX_LENGTH = "MAX"
FALLBACK_DATATYPE = DataType(name=VARCHAR, length=MAX_LENGTH)


class DataTypeConverter:
    @staticmethod
    def convert(json_schema_type: str, json_schema_format: str = None, json_schema_max_length: str = None) -> DataType:
        return {
            "string": DataTypeConverter._convert_string(json_schema_format, json_schema_max_length),
            "number": DataType(name="DOUBLE"),
            "integer": DataType(name="INTEGER"),
            "boolean": DataType(name="BOOLEAN")
        }.get(json_schema_type, FALLBACK_DATATYPE)

    @staticmethod
    def _convert_string(json_schema_format: str = None, json_schema_max_length: str = None) -> DataType:
        data_type = {
            "date-time": "TIMESTAMP WITHOUT TIME ZONE",
            "time": "TIME",
            "date": "DATE"
        }.get(json_schema_format, VARCHAR)

        if data_type == VARCHAR:
            return DataType(name=VARCHAR, length=json_schema_max_length or MAX_LENGTH)
        else:
            return DataType(name=data_type)



