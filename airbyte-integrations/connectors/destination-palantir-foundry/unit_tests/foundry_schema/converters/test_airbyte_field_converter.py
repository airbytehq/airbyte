import unittest

from destination_palantir_foundry.foundry_schema.converters.airbyte_field_converter import \
    convert_ab_field_to_foundry_field
from destination_palantir_foundry.foundry_schema.foundry_schema import StringFieldSchema, BooleanFieldSchema, \
    DateFieldSchema, TimestampFieldSchema, IntegerFieldSchema, DoubleFieldSchema, ArrayFieldSchema, StructFieldSchema


class TestAirbyteSchemaConverter(unittest.TestCase):
    def test_convertAbFieldToFoundryField_stringNotNull_convertsToString(self):
        ab_string_field_schema = {
            "type": "string",
            "description": "test description",
        }

        foundry_field_schema = convert_ab_field_to_foundry_field("test_field_name", ab_string_field_schema)

        self.assertEquals(foundry_field_schema, StringFieldSchema(
            name="test_field_name",
            nullable=False,
            customMetadata={}
        ))

    def test_convertAbFieldToFoundryField_stringNull_convertsToString(self):
        ab_string_field_schema = {
            "type": ["null", "string"],
        }

        foundry_field_schema = convert_ab_field_to_foundry_field("test_field_name", ab_string_field_schema)

        self.assertEquals(foundry_field_schema, StringFieldSchema(
            name="test_field_name",
            nullable=True,
            customMetadata={}
        ))

    def test_convertAbFieldToFoundryField_boolean_convertsToBoolean(self):
        ab_string_field_schema = {
            "type": "boolean",
        }

        foundry_field_schema = convert_ab_field_to_foundry_field("test_field_name", ab_string_field_schema)

        self.assertEquals(foundry_field_schema, BooleanFieldSchema(
            name="test_field_name",
            nullable=False,
            customMetadata={}
        ))

    def test_convertAbFieldToFoundryField_date_convertsToDate(self):
        ab_string_field_schema = {
            "type": "string",
            "format": "date"
        }

        foundry_field_schema = convert_ab_field_to_foundry_field("test_field_name", ab_string_field_schema)

        self.assertEquals(foundry_field_schema, DateFieldSchema(
            name="test_field_name",
            nullable=False,
            customMetadata={}
        ))

    def test_convertAbFieldToFoundryField_timestampWithoutTimezone_convertsToTimestamp(self):
        ab_string_field_schema = {
            "type": "string",
            "format": "date-time",
            "airbyte_type": "timestamp_without_timezone"
        }

        foundry_field_schema = convert_ab_field_to_foundry_field("test_field_name", ab_string_field_schema)

        self.assertEquals(foundry_field_schema, TimestampFieldSchema(
            name="test_field_name",
            nullable=False,
            customMetadata={}
        ))

    def test_convertAbFieldToFoundryField_timestampWithTimezone_convertsToTimestamp(self):
        ab_string_field_schema = {
            "type": "string",
            "format": "date-time",
            "airbyte_type": "timestamp_with_timezone"
        }

        foundry_field_schema = convert_ab_field_to_foundry_field("test_field_name", ab_string_field_schema)

        self.assertEquals(foundry_field_schema, TimestampFieldSchema(
            name="test_field_name",
            nullable=False,
            customMetadata={}
        ))

    def test_convertAbFieldToFoundryField_timestampWithTimezoneNoAirbyteType_convertsToTimestamp(self):
        ab_string_field_schema = {
            "type": "string",
            "format": "date-time",
        }

        foundry_field_schema = convert_ab_field_to_foundry_field("test_field_name", ab_string_field_schema)

        self.assertEquals(foundry_field_schema, TimestampFieldSchema(
            name="test_field_name",
            nullable=False,
            customMetadata={}
        ))

    def test_convertAbFieldToFoundryField_timeWithoutTimezone_convertsToString(self):
        ab_string_field_schema = {
            "type": "string",
            "format": "time",
            "airbyte_type": "timestamp_without_timezone",
        }

        foundry_field_schema = convert_ab_field_to_foundry_field("test_field_name", ab_string_field_schema)

        self.assertEquals(foundry_field_schema, StringFieldSchema(
            name="test_field_name",
            nullable=False,
            customMetadata={}
        ))

    def test_convertAbFieldToFoundryField_timeWithTimezone_convertsToString(self):
        ab_string_field_schema = {
            "type": "string",
            "format": "time",
            "airbyte_type": "timestamp_with_timezone",
        }

        foundry_field_schema = convert_ab_field_to_foundry_field("test_field_name", ab_string_field_schema)

        self.assertEquals(foundry_field_schema, StringFieldSchema(
            name="test_field_name",
            nullable=False,
            customMetadata={}
        ))

    def test_convertAbFieldToFoundryField_integer_convertsToInteger(self):
        ab_string_field_schema = {
            "type": "integer",
        }

        foundry_field_schema = convert_ab_field_to_foundry_field("test_field_name", ab_string_field_schema)

        self.assertEquals(foundry_field_schema, IntegerFieldSchema(
            name="test_field_name",
            nullable=False,
            customMetadata={}
        ))

    def test_convertAbFieldToFoundryField_integerNumberSpecialCase_convertsToInteger(self):
        ab_string_field_schema = {
            "type": "number",
            "airbyte_type": "integer",
        }

        foundry_field_schema = convert_ab_field_to_foundry_field("test_field_name", ab_string_field_schema)

        self.assertEquals(foundry_field_schema, IntegerFieldSchema(
            name="test_field_name",
            nullable=False,
            customMetadata={}
        ))

    def test_convertAbFieldToFoundryField_number_convertsToDouble(self):
        ab_string_field_schema = {
            "type": "number",
        }

        foundry_field_schema = convert_ab_field_to_foundry_field("test_field_name", ab_string_field_schema)

        self.assertEquals(foundry_field_schema, DoubleFieldSchema(
            name="test_field_name",
            nullable=False,
            customMetadata={}
        ))

    def test_convertAbFieldToFoundryField_arrayNoItems_convertsToArrayWithStringType(self):
        ab_string_field_schema = {
            "type": "array",
        }

        foundry_field_schema = convert_ab_field_to_foundry_field("test_field_name", ab_string_field_schema)

        self.assertEquals(foundry_field_schema, ArrayFieldSchema(
            name="test_field_name",
            nullable=False,
            customMetadata={},
            arraySubtype=StringFieldSchema(
                nullable=True,
            )
        ))

    def test_convertAbFieldToFoundryField_objectNoProperties_convertsToEmptyStruct(self):
        ab_string_field_schema = {
            "type": "object",
        }

        foundry_field_schema = convert_ab_field_to_foundry_field("test_field_name", ab_string_field_schema)

        self.assertEquals(foundry_field_schema, StructFieldSchema(
            name="test_field_name",
            nullable=False,
            customMetadata={},
            subSchemas=[]
        ))

    def test_convertAbFieldToFoundryField_objectProperties_convertsToStruct(self):
        ab_string_field_schema = {
            "type": "object",
            "properties": {
                "test_prop_name": {
                    "type": ["string", "null"],
                }
            }
        }

        foundry_field_schema = convert_ab_field_to_foundry_field("test_field_name", ab_string_field_schema)

        self.assertEquals(foundry_field_schema, StructFieldSchema(
            name="test_field_name",
            nullable=False,
            customMetadata={},
            subSchemas=[StringFieldSchema(
                name="test_prop_name",
                nullable=True,
                customMetadata={},
            )]
        ))

    def test_convertAbFieldToFoundryField_oneOf_convertsToString(self):
        ab_string_field_schema = {
            "type": "object",
            "oneOf": [
                {
                    "type": "string"
                },
                {
                    "type": "number"
                }
            ]
        }

        foundry_field_schema = convert_ab_field_to_foundry_field("test_field_name", ab_string_field_schema)

        self.assertEquals(foundry_field_schema, StringFieldSchema(
            name="test_field_name",
            nullable=False,
            customMetadata={},
        ))

    def test_convertAbFieldToFoundryField_oneOfNoType_convertsToString(self):
        ab_string_field_schema = {
            "oneOf": [
                {
                    "type": "string"
                },
                {
                    "type": "number"
                }
            ]
        }

        foundry_field_schema = convert_ab_field_to_foundry_field("test_field_name", ab_string_field_schema)

        self.assertEquals(foundry_field_schema, StringFieldSchema(
            name="test_field_name",
            nullable=False,
            customMetadata={},
        ))

    def test_convertAbFieldToFoundryField_unknown_convertsToString(self):
        ab_string_field_schema = {
            "type": "unknown",
        }

        foundry_field_schema = convert_ab_field_to_foundry_field("test_field_name", ab_string_field_schema)

        self.assertEquals(foundry_field_schema, StringFieldSchema(
            name="test_field_name",
            nullable=False,
            customMetadata={},
        ))
