# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, Optional
from urllib.parse import urlencode, urlparse, urlunparse
from xml.etree import ElementTree

import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.utils import AirbyteTracedException


TYPE_MAP = {
    "xsd:decimal": "number",
    "xsd:string": "string",
    "xsd:boolean": "boolean",
}


class ReportXMLSchemaHelper:
    default_string_type = "xsd:string"
    default_report_entry = "Report_EntryType"

    def __init__(self, config, report_id):
        self._PROPERTIES = {}
        self.config = config
        self.report_id = report_id
        self.root = self._get_xml_tree()
        self.namespace = self._extract_namespace()

    @property
    def _xml_schema_url(self):
        """
        Creates xml url to the report document tree.
        Removes query params if they were provided.
        Example: https://host.myworkday.com/ccx/service/customreport2/tenant/report/id?xsd
        """

        base_url = f"https://{self.config['host']}/ccx/service/customreport2/{self.config['tenant_id']}/{self.report_id}"
        # removes query params from report id (for reports which support filtering)
        parsed = urlparse(base_url)
        query_new = urlencode({}, doseq=True)
        parsed = parsed._replace(query=query_new)

        return f"{urlunparse(parsed)}?xsd"

    def _extract_namespace(self):
        # tag {http://www.w3.org/2001/XMLSchema}schema
        namespace = self.root.tag[self.root.tag.index("{") + 1 : self.root.tag.index("}")]
        return {"xsd": namespace}

    def _get_xml_tree(self) -> ElementTree:
        """
        Makes request to xml url and creates xml.etree.ElementTree object.
        """

        try:
            xml_data = requests.get(url=self._xml_schema_url)
            xml_data.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            raise AirbyteTracedException(
                failure_type=FailureType.system_error,
                internal_message=str(http_err),
                message=f"Error occurred while reading schema for Report {self.report_id}: {self._xml_schema_url}",
            )
        return ElementTree.fromstring(xml_data.content)

    def _find_elements_types(self, complex_type: str, default_name: str = "") -> Dict[str, Optional[Any]]:
        """
        Searches for type of field name in sequence in complexType element.
        If sequence not found uses basic extension in simpleContent element and uses default name for field name.
        Returns types dict with field and found type for it.
        If field not found default_name and default string type will be used.
        """

        types = {}

        complex_type_entry = self.root.find(f'.//xsd:complexType[@name="{complex_type}"]', self.namespace)
        if complex_type_entry is None:
            raise ValueError(f"No {complex_type} element found")

        sequence = complex_type_entry.find(".//xsd:sequence", self.namespace)

        if sequence is not None:
            for element in sequence.findall(".//xsd:element", self.namespace):
                # indicates array of items. when element ID we should use element type instead of array
                if element.get("maxOccurs") == "unbounded" and element.get("name") != "ID":
                    array_item_type = self._find_elements_types(element.get("type").replace("wd:", ""), element.get("name"))
                    # adding to properties instead of types as type is already known
                    self._PROPERTIES[element.get("name")] = {
                        "type": "array",
                        "items": array_item_type,
                    }
                else:
                    types[element.get("name")] = element.get("type")
        else:
            # if sequence element not found we should search for type in simpleContent/extension
            extension = complex_type_entry.find(".//xsd:simpleContent", self.namespace).find(".//xsd:extension", self.namespace).get("base")
            # if simpleContent/extension is None use default string type
            types[default_name] = extension or self.default_string_type

        return types

    def _validate_types(self, types: Dict[str, Optional[Any]]) -> Dict[str, Optional[Any]]:
        """
        Adds known types to _PROPERTIES. deletes it from types .
        Returns updated types dict
        """

        types_copy = types.copy()

        for field_name, field_type in types_copy.items():
            if field_type in TYPE_MAP.keys():
                # add to properties
                self._PROPERTIES[field_name] = field_type
                # remove from types
                del types[field_name]

        return types

    def find_element_types(self, types: Dict[str, Optional[Any]], default_name) -> None:
        """
        Searches for element types in xml tree until _validate_types returns empty types dict,
        which means that all found field types were added to _PROPERTIES.
        """

        for field, field_types in types.items():
            field_types = self._find_elements_types(field_types.replace("wd:", ""), default_name)
            field_types = self._validate_types(field_types)
            if field_types != {}:
                self.find_element_types(field_types, field)

    def _create_array_type(self, field_type: Dict[str, Optional[Any]]) -> Dict[str, Optional[Any]]:
        """
        Creates json schema notation for array types.
        """

        final_type = [field_type["type"], "null"]
        items = field_type["items"]
        k, v = list(items.keys())[0], list(items.values())[0]
        final_items = {
            "type": ["object", "null"],
            "properties": {k: {"type": [TYPE_MAP.get(v, "string"), "null"]}},
        }

        return {"type": final_type, "items": final_items}

    def final_properties(self) -> Dict[str, Optional[Any]]:
        """
        For each field in _PROPERTIES creates json schema notation.
        """

        final_properties = {"data": {"type": ["object", "null"]}}

        for field, f_type in self._PROPERTIES.items():
            if isinstance(f_type, dict):
                if f_type["type"] == "array":
                    final_properties[field] = self._create_array_type(f_type)
            else:
                final_properties[field] = {"type": [TYPE_MAP.get(f_type, "string"), "null"]}

        return final_properties

    def get_properties(self) -> Dict[str, Optional[Any]]:
        """
        Returns properties for stream json schema.
        """

        types = self._find_elements_types(self.default_report_entry, "")
        types = self._validate_types(types)

        self.find_element_types(types, "")

        schema = self.final_properties()

        return schema

    def fields_transform_string_array(self):
        """
        There is a case when workday returns string for fields that declared as unbounded(can have more than 1 value in it).
        So this method finds all such fields and creates a transformation object for them.
        [{'ID': record['{field}']}] if record['field'] is string else record['field']
        """

        properties = self.get_properties()
        to_transform = []

        for field, field_type in properties.items():
            if field_type.get("items", {}).get("properties", {}).get("ID"):
                to_transform.append(field)

        transformations = []
        for field in to_transform:
            t = {
                "path": [field],
                "type": "AddedFieldDefinition",
                "value": "{{ [{ 'ID':"
                + f" record['{field}']"
                + " }] "
                + f"if (record['{field}'] is string) else record['{field}']"
                + " }}",
            }
            transformations.append(t)

        return transformations
