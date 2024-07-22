import json
from typing import Any, Dict, List

from dateutil import parser, tz

from destination_palantir_foundry.foundry_schema.foundry_schema import FoundrySchema, FoundryFieldSchema


def _find_field_schema(field_name: str, field_schemas: List[FoundryFieldSchema]) -> FoundryFieldSchema:
    for field_schema in field_schemas:
        if field_schema.name == field_name:
            return field_schema

    raise ValueError(f"Could not find field schema for field {field_name} in Foundry schema.")


def convert_timestamp_to_unix_ms(timestamp: str) -> float:
    dt = parser.parse(timestamp)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz.UTC)

    unix_timestamp = dt.timestamp()
    return int(unix_timestamp) * 1000


def convert_field(value: Any, field_schema: FoundryFieldSchema):
    if value is None and field_schema.nullable:
        return None
    if value is None and not field_schema.nullable:
        raise ValueError(f"Cannot parse null value for nonnullable field {field_schema.name}")

    if field_schema.type_ == "ARRAY":
        if not isinstance(value, list):
            raise ValueError(f"Cannot parse nonlist array type {value}")

        return [convert_field(item, field_schema.arraySubtype) for item in value]

    elif field_schema.type_ == "BINARY":
        raise NotImplementedError("BINARY type not yet implemented.")

    elif field_schema.type_ == "BOOLEAN":
        if isinstance(value, str) and value.lower() == "true":
            return True
        elif isinstance(value, str) and value.lower() == "false":
            return False
        elif isinstance(value, bool):
            return value
        elif isinstance(value, int) or isinstance(value, float):
            return bool(value)

        raise ValueError(f"Cannot parse boolean type {value}")

    elif field_schema.type_ == "BYTE":
        raise NotImplementedError("BYTE type not yet implemented.")

    elif field_schema.type_ == "DATE":
        if isinstance(value, str):
            if value.endswith("BC"):
                raise ValueError("Cannot parse BC date type")
            
            return value

        raise ValueError(f"Cannot parse nonstring date type {value}")

    elif field_schema.type_ == "DECIMAL":
        raise NotImplementedError("DECIMAL type not yet implemented.")

    elif field_schema.type_ == "DOUBLE":
        # may throw
        return float(value)

    elif field_schema.type_ == "FLOAT":
        # may throw
        return float(value)
    elif field_schema.type_ == "INTEGER":
        # may throw
        return int(value)

    elif field_schema.type_ == "LONG":
        # may throw
        return int(value)

    elif field_schema.type_ == "MAP":
        raise NotImplementedError("MAP type not yet implemented.")

    elif field_schema.type_ == "SHORT":
        # may throw
        return int(value)

    elif field_schema.type_ == "STRING":
        if isinstance(value, str):
            return value
        else:
            return json.dumps(value)

    elif field_schema.type_ == "STRUCT":
        converted = {}
        for key, value in value.items():
            field_sub_schema = _find_field_schema(key, field_schema.subSchemas)
            converted[key] = convert_field(value, field_sub_schema)

        return converted

    elif field_schema.type_ == "TIMESTAMP":
        if isinstance(value, str):
            return convert_timestamp_to_unix_ms(value)
        elif isinstance(value, int):
            # unix?
            return value

        raise ValueError(f"Cannot parse datetime type {value}")


def convert_ab_record(airbyte_record: Dict[str, Any], foundry_schema: FoundrySchema) -> Dict[str, Any]:
    converted = {}

    for key, value in airbyte_record.items():
        field_schema = _find_field_schema(key, foundry_schema.fieldSchemaList)
        converted[key] = convert_field(value, field_schema)

    return converted
