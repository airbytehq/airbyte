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
                name=None,
                nullable=False,
                customMetadata={},
                isUnnamed=True
            )
        )

        result = array_field.model_dump()

        self.assertEqual(result, {
            "type": "ARRAY",
            "nullable": False,
            "name": "array",
            "customMetadata": {},
            "arraySubtype": {
                "type": "STRING",
                "nullable": False,
                "customMetadata": {},
            }
        })

    def test_arrayField_nestedArrayType(self):
        array_field = foundry_schema.ArrayFieldSchema(
            name="array",
            nullable=False,
            arraySubtype=foundry_schema.ArrayFieldSchema(
                nullable=False,
                arraySubtype=foundry_schema.StringFieldSchema(
                    nullable=False,
                )
            )
        )

        result = array_field.model_dump()

        self.assertEqual(result, {
            "type": "ARRAY",
            "nullable": False,
            "name": "array",
            "customMetadata": {},
            "arraySubtype": {
                "type": "ARRAY",
                "nullable": False,
                "customMetadata": {},
                "arraySubtype": {
                    "type": "STRING",
                    "nullable": False,
                    "customMetadata": {},
                }
            }
        })

