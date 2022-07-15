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


def handle_export_dimensions(data: str) -> Iterable[Mapping]:

    dimensions = data.get("response").get("output").get("dimensions").get("dimension")

    dimensions_records = []

    for dimension in dimensions:
        dimension_id = dimension.get("@id")
        dimension_name = dimension.get("@name")
        dimension_short_name = dimension.get("@shortName")

        values = dimension.get("dimensionValue", None)
        if values:
            for value in values:
                value_id = value.get("@id")
                value_name = value.get("@name")
                value_description = value.get("@description")
                value_short_name = value.get("@shortName")

                attributes_dict = value.get("attributes", None)
                if attributes_dict:

                    attributes = attributes_dict.get("attribute", None)

                    if isinstance(attributes, dict):
                        attributes = [attributes]

                    for attribute in attributes:
                        attribute_id = attribute.get("@attributeId")
                        attribute_name = attribute.get("@name")
                        attribute_value_id = attribute.get("@valueId")
                        attribute_value = attribute.get("@value")

                        dimensions_records.append({
                            "dimension_id": dimension_id,
                            "dimension_name": dimension_name,
                            "dimension_short_name": dimension_short_name,
                            "value_id": value_id,
                            "value_name": value_name,
                            "value_description": value_description,
                            "value_short_name": value_short_name,
                            "attribute_id": attribute_id,
                            "attribute_name": attribute_name,
                            "attribute_value_id": attribute_value_id,
                            "attribute_value": attribute_value
                        })
                else:
                    dimensions_records.append({
                            "dimension_id": dimension_id,
                            "dimension_name": dimension_name,
                            "dimension_short_name": dimension_short_name,
                            "value_id": value_id,
                            "value_name": value_name,
                            "value_description": value_description,
                            "value_short_name": value_short_name,
                            "attribute_id": None,
                            "attribute_name": None,
                            "attribute_value_id": None,
                            "attribute_value": None
                        })
        else:
            dimensions_records.append({
                            "dimension_id": dimension_id,
                            "dimension_name": dimension_name,
                            "dimension_short_name": dimension_short_name,
                            "value_id": None,
                            "value_name": None,
                            "value_description": None,
                            "value_short_name": None,
                            "attribute_id": None,
                            "attribute_name": None,
                            "attribute_value_id": None,
                            "attribute_value": None
                        })

    return dimensions_records
