from typing import Mapping, List, Any

def get_field_value(record: Mapping[str, Any], field: str) -> str:
    field_path = field.split('.')
    tmp = record

    for path in field_path:
        if not tmp:
            break
        tmp = tmp.get(path, None)

    return tmp

def get_fields_from_schema(schema: Mapping[str, Any]) -> List[str]:
    properties = schema.get("properties")
    return list(properties.keys())

def parse_single_record(schema: Mapping[str, Any], record: Mapping[str, Any]) -> Mapping[str, Any]:
    fields = get_fields_from_schema(schema)
    single_record = {field: get_field_value(record, field) for field in fields}
    return single_record