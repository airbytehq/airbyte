from typing import (
    Any,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    Union
)
import hashlib


class Dimension:
    def __init__(self, version: str):
        self.id = None
        self.dimension_id = None
        self.dimension_name = None
        self.dimension_short_name = None
        self.value_id = None
        self.value_name = None
        self.value_description = None
        self.value_short_name = None
        self.attribute_id = None
        self.attribute_name = None
        self.attribute_value_id = None
        self.attribute_value = None
        self.version = version

    def parse_dict(self, d: dict, _type: str) -> None:
        if _type == "dimension":
            self.dimension_id = int(d.get("@id"))
            self.dimension_name = d.get("@name")
            self.dimension_short_name = d.get("@shortName")
        elif _type == "values":
            self.value_id = int(d.get("@id"))
            self.value_name = d.get("@name")
            self.value_description = d.get("@description")
            self.value_short_name = d.get("@shortName")
        elif _type == "attributes":
            self.attribute_id = int(d.get("@attributeId"))
            self.attribute_name = d.get("@name")
            self.attribute_value_id = int(d.get("@valueId"))
            self.attribute_value = d.get("@value")

        _id = f"{self.dimension_id}{self.value_id}{self.attribute_id}".encode("utf-8")
        self.id = int(hashlib.sha1(_id).hexdigest(), 16) % (10 ** 12)

    def to_record(self) -> dict:
        return {
            "id": self.id,
            "dimension_id": self.dimension_id,
            "dimension_name": self.dimension_name,
            "dimension_short_name": self.dimension_short_name,
            "value_id": self.value_id,
            "value_name": self.value_name,
            "value_description": self.value_description,
            "value_short_name": self.value_short_name,
            "attribute_id": self.attribute_id,
            "attribute_name": self.attribute_name,
            "attribute_value_id": self.attribute_value_id,
            "attribute_value": self.attribute_value,
            "version": self.version
        }


def handle_export_dimensions(data: str, version: str) -> Iterable[Mapping]:

    dimensions = data.get("response").get("output").get("dimensions").get("dimension")

    dimensions_records = []

    for dimension in dimensions:

        values = dimension.get("dimensionValue", None)

        if values:
            if isinstance(values, dict):
                values = [values]

            for value in values:
                attributes_dict = value.get("attributes", None)
                if attributes_dict:

                    attributes = attributes_dict.get("attribute", None)

                    if isinstance(attributes, dict):
                        attributes = [attributes]

                    for attribute in attributes:
                        d = Dimension(version=version)
                        
                        d.parse_dict(dimension, _type="dimension")
                        d.parse_dict(value, _type="values")
                        d.parse_dict(attribute, _type="attributes")
                        
                        dimensions_records.append(d.to_record())
                else:
                    d = Dimension(version=version)
                        
                    d.parse_dict(dimension, _type="dimension")
                    d.parse_dict(value, _type="values")
                    
                    dimensions_records.append(d.to_record())
        else:
            d = Dimension(version=version)       
            d.parse_dict(dimension, _type="dimension")
            
            dimensions_records.append(d.to_record())

    return dimensions_records
