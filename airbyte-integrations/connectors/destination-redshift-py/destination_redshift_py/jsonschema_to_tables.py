from collections import OrderedDict
from typing import Optional, List

from destination_redshift_py.data_type_converter import DataTypeConverter, FALLBACK_DATATYPE
from destination_redshift_py.field import Field
from destination_redshift_py.table import Table

PARENT_CHILD_SPLITTER = "."


class JsonToTables:
    def __init__(self, json_schema: dict, schema: str, root_table: str, primary_keys: Optional[List[str]]):
        self.json_schema = json_schema

        self.schema = schema
        self.root = root_table

        self.tables = OrderedDict()
        self.primary_keys = primary_keys

    def convert(self):
        for item_key, item_value in self.json_schema.items():
            if item_key == "properties":
                self._extract_tables(item_value, name=self.root, primary_keys=self.primary_keys)

    def _extract_tables(self, properties: dict, name: str, primary_keys: List[str] = None, references: Table = None):
        table_name = name.replace(PARENT_CHILD_SPLITTER, "_")
        table = Table(schema=self.schema, name=table_name, primary_keys=primary_keys, references=references)
        self.tables[name] = table

        for property_key, property_value in properties.items():
            item_type = property_value.get("type")
            if not set(item_type).intersection({"object", "array"}):
                data_type = DataTypeConverter.convert(property_value["type"], property_value.get("format"), property_value.get("maxLength"))
                table.fields.append(Field(name=property_key, data_type=data_type))
            else:
                if set(item_type).intersection({"object"}):
                    self._convert_object_to_table(name=name, property_key=property_key, property_value=property_value, references=table)
                else:  # array
                    if "items" in property_value:
                        property_value = property_value.get("items")
                        self._convert_object_to_table(name=name, property_key=property_key, property_value=property_value, references=table)
                    else:
                        table.fields.append(Field(name=property_key, data_type=FALLBACK_DATATYPE))

    def _convert_object_to_table(self, name: str, property_key: str, property_value: dict, references: Table):
        if "properties" in property_value:
            properties = property_value.get("properties")
            self._extract_tables(properties=properties, name=f"{name}.{property_key}", references=references)
        else:  # If no `properties`, treat the field as a string
            references.fields.append(Field(name=property_key, data_type=FALLBACK_DATATYPE))


