import json
import unittest

from destination_palantir_foundry.foundry_schema import foundry_schema


# TODO(jcrowson): Add additional tests for other field types


class TestFoundryFields(unittest.TestCase):
    def test_arrayField_basicArrayType(self):
        array_field = foundry_schema.ArrayFieldSchema(
            name="array",
            nullable=False,
            customMetadata={},
            arraySubtype=foundry_schema.StringFieldSchema(
                name="string",
                nullable=False,
                customMetadata={}
            )
        )

        result = json.loads(array_field.json(by_alias=True))

        self.assertEqual(result, {
            "type": "ARRAY",
            "nullable": False,
            "name": "array",
            "customMetadata": {},
            "arraySubtype": {
                "type": "STRING",
                "name": "string",
                "nullable": False,
                "customMetadata": {},
            }
        })

    def test_arrayField_nestedArrayType(self):
        array_field = foundry_schema.ArrayFieldSchema(
            name="array",
            nullable=False,
            arraySubtype=foundry_schema.ArrayFieldSchema(
                name="array2",
                nullable=False,
                arraySubtype=foundry_schema.StringFieldSchema(
                    name="string",
                    nullable=False,
                )
            )
        )

        result = json.loads(array_field.json(by_alias=True))

        self.assertEqual(result, {
            "type": "ARRAY",
            "nullable": False,
            "name": "array",
            "customMetadata": {},
            "arraySubtype": {
                "type": "ARRAY",
                "name": "array2",
                "nullable": False,
                "customMetadata": {},
                "arraySubtype": {
                    "type": "STRING",
                    "name": "string",
                    "nullable": False,
                    "customMetadata": {},
                }
            }
        })
