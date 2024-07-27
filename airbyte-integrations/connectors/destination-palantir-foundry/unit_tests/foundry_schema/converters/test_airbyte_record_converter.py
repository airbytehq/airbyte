import unittest

from destination_palantir_foundry.foundry_schema.converters.airbyte_record_converter import convert_field, \
    convert_ab_record
from destination_palantir_foundry.foundry_schema.foundry_schema import ArrayFieldSchema, StringFieldSchema, \
    BooleanFieldSchema, DateFieldSchema, DoubleFieldSchema, IntegerFieldSchema, FloatFieldSchema, LongFieldSchema, \
    StructFieldSchema, TimestampFieldSchema, FoundrySchema


class TestAirbyteRecordConverter(unittest.TestCase):
    def test_convertField_nullableNone_returnsNone(self):
        value = None

        result = convert_field(
            value,
            StringFieldSchema(
                name="string",
                nullable=True,
            )
        )

        self.assertEquals(result, None)

    def test_convertField_nonNullableNone_raises(self):
        value = None

        with self.assertRaises(ValueError):
            convert_field(
                value,
                StringFieldSchema(
                    name="string",
                    nullable=False,
                )
            )

    def test_convertField_arrayNoValues_emptyArray(self):
        value = []

        result = convert_field(
            value,
            ArrayFieldSchema(
                name="array",
                nullable=False,
                arraySubtype=StringFieldSchema(
                    nullable=False,
                )
            )
        )

        self.assertEquals(result, [])

    def test_convertField_arrayWithPrimitiveValues_converts(self):
        value = ["test", "test2"]

        result = convert_field(
            value,
            ArrayFieldSchema(
                name="array",
                nullable=False,
                arraySubtype=StringFieldSchema(
                    nullable=False,
                )
            )
        )

        self.assertEquals(result, ["test", "test2"])

    def test_convertField_arrayWithPrimitiveValuesAndNulls_converts(self):
        value = ["test", None]

        result = convert_field(
            value,
            ArrayFieldSchema(
                name="array",
                nullable=False,
                arraySubtype=StringFieldSchema(
                    nullable=True,
                )
            )
        )

        self.assertEquals(result, ["test", None])

    def test_convertField_2dArray_converts(self):
        value = [
            ["test1", "test2"],
            ["test3"]
        ]

        result = convert_field(
            value,
            ArrayFieldSchema(
                name="array",
                nullable=False,
                arraySubtype=ArrayFieldSchema(
                    nullable=False,
                    arraySubtype=StringFieldSchema(
                        nullable=True,
                    )
                )
            )
        )

        self.assertEquals(result, [["test1", "test2"], ["test3"]])

    def test_convertField_booleanStringTrue_converts(self):
        values = ["true", "True", "TRUE", True, 1]

        results = [convert_field(
            value,
            BooleanFieldSchema(
                name="boolean",
                nullable=False,
            )
        ) for value in values]

        self.assertEquals(all(results), True)

    def test_convertField_booleanStringFalse_converts(self):
        values = ["false", "False", "FALSE", False, 0]

        results = [convert_field(
            value,
            BooleanFieldSchema(
                name="boolean",
                nullable=False,
            )
        ) for value in values]

        self.assertEquals(any(results), False)

    def test_convertField_date_converts(self):
        value = "2021-01-23"

        result = convert_field(
            value,
            DateFieldSchema(
                name="date",
                nullable=False,
            )
        )

        self.assertEquals(result, "2021-01-23")

    def test_convertField_dateBC_raises(self):
        value = "2021-01-23 BC"

        with self.assertRaises(ValueError):
            convert_field(
                value,
                DateFieldSchema(
                    name="date",
                    nullable=False,
                )
            )

    def test_convertField_double_converts(self):
        values = [1.0001, "1.0001"]

        results = [convert_field(
            value,
            DoubleFieldSchema(
                name="double",
                nullable=False,
            )
        ) for value in values]

        for result in results:
            self.assertEquals(result, 1.0001)

    def test_convertField_float_converts(self):
        values = [1.0001, "1.0001"]

        results = [convert_field(
            value,
            FloatFieldSchema(
                name="float",
                nullable=False,
            )
        ) for value in values]

        for result in results:
            self.assertEquals(result, 1.0001)

    def test_convertField_integer_converts(self):
        values = [1, "1"]

        results = [convert_field(
            value,
            IntegerFieldSchema(
                name="integer",
                nullable=False,
            )
        ) for value in values]

        for result in results:
            self.assertEquals(result, 1)

    def test_convertField_long_converts(self):
        values = [10000000, "10000000"]

        results = [convert_field(
            value,
            LongFieldSchema(
                name="long",
                nullable=False,
            )
        ) for value in values]

        for result in results:
            self.assertEquals(result, 10000000)

    def test_convertField_string_converts(self):
        values = [1, "1"]

        results = [convert_field(
            value,
            StringFieldSchema(
                name="string",
                nullable=False,
            )
        ) for value in values]

        for result in results:
            self.assertEquals(result, "1")

    def test_convertField_stringNonString_converts(self):
        value = {"test": 1}

        result = convert_field(
            value,
            StringFieldSchema(
                name="string",
                nullable=False,
            )
        )

        self.assertEquals(result, '{"test": 1}')

    def test_convertField_struct_convertsNested(self):
        value = {
            "test": {
                "test2": "test2",
                "test3": None,
                "test4": "2023-01-23"
            }
        }

        result = convert_field(
            value,
            StructFieldSchema(
                name="string",
                nullable=False,
                subSchemas=[
                    StructFieldSchema(
                        name="test",
                        nullable=False,
                        subSchemas=[
                            StringFieldSchema(
                                name="test2",
                                nullable=False
                            ),
                            StringFieldSchema(
                                name="test3",
                                nullable=True
                            ),
                            DateFieldSchema(
                                name="test4",
                                nullable=True
                            )
                        ]
                    )
                ]
            )
        )

        self.assertEquals(result, {
            "test": {
                "test2": "test2",
                "test3": None,
                "test4": "2023-01-23"
            }
        })

    def test_convertValue_timestampWithTimezone_converts(self):
        value = "2022-07-22T16:00:00+0:00"

        result = convert_field(
            value,
            TimestampFieldSchema(
                name="timestamp",
                nullable=False,
            )
        )

        self.assertEquals(result, 1658505600000)

    def test_convertValue_timestampWitTimezone2_converts(self):
        value = "2022-07-22T12:00:00+04:00"

        result = convert_field(
            value,
            TimestampFieldSchema(
                name="timestamp",
                nullable=False,
            )
        )

        self.assertEquals(result, 1658476800000)

    def test_convertValue_timestampWitoutTimezone_converts(self):
        value = "2022-07-22T08:00:00"

        result = convert_field(
            value,
            TimestampFieldSchema(
                name="timestamp",
                nullable=False,
            )
        )

        self.assertEquals(result, 1658476800000)

    def test_convertRecord_(self):
        schema = FoundrySchema(
            fieldSchemaList=[
                StringFieldSchema(name="stringField", nullable=False),
                BooleanFieldSchema(name="booleanField", nullable=False),
                DateFieldSchema(name="dateField", nullable=False),
                TimestampFieldSchema(name="timestampWithoutTimezoneField", nullable=False),
                TimestampFieldSchema(name="timestampWithTimezoneField", nullable=False),
                TimestampFieldSchema(name="timestampWithTimezoneField2", nullable=False),
                StringFieldSchema(name="timeWithoutTimezoneField", nullable=False),
                StringFieldSchema(name="timeWithTimezoneField", nullable=False),
                IntegerFieldSchema(name="integerField", nullable=False),
                IntegerFieldSchema(name="integerFieldWithAirbyte", nullable=False),
                DoubleFieldSchema(name="numberField", nullable=False),
                ArrayFieldSchema(
                    name="stringArrayField",
                    nullable=False,
                    arraySubtype=StringFieldSchema(
                        nullable=False
                    )
                ),
                StructFieldSchema(name="objectField", nullable=False, subSchemas=[
                    StringFieldSchema(name="objStringField", nullable=False),
                    ArrayFieldSchema(
                        name="objIntArrayField",
                        nullable=False,
                        arraySubtype=IntegerFieldSchema(
                            nullable=False
                        )
                    )
                ]),
                StringFieldSchema(name="unionField", nullable=False)
            ],
            dataFrameReaderClass="fakereader",
            customMetadata={}
        )

        record = {
            "stringField": "Hello, OpenAI!",
            "booleanField": False,
            "dateField": "2022-01-01",
            "timestampWithoutTimezoneField": "2022-01-01T12:00:00",
            "timestampWithTimezoneField": "2022-01-01T12:00:00Z",
            "timestampWithTimezoneField2": "2022-01-01T12:00:00+00:00",
            "timeWithoutTimezoneField": "12:00:00",
            "timeWithTimezoneField": "12:00:00+00:00",
            "integerField": 12345,
            "integerFieldWithAirbyte": 67890,
            "numberField": 123.45,
            "stringArrayField": ["item1", "item2", "item3"],
            "objectField": {
                "objStringField": "Nested string",
                "objIntArrayField": [1, 2, 3, 4, 5]
            },
            "unionField": "This can be a string, a number, or a boolean"
        }

        result = convert_ab_record(record, schema)

        self.assertEquals(result, {
            "stringField": "Hello, OpenAI!",
            "booleanField": False,
            "dateField": "2022-01-01",
            "timestampWithoutTimezoneField": 1641038400000,
            "timestampWithTimezoneField": 1641038400000,
            "timestampWithTimezoneField2": 1641038400000,
            "timeWithoutTimezoneField": "12:00:00",
            "timeWithTimezoneField": "12:00:00+00:00",
            "integerField": 12345,
            "integerFieldWithAirbyte": 67890,
            "numberField": 123.45,
            "stringArrayField": ["item1", "item2", "item3"],
            "objectField": {
                "objStringField": "Nested string",
                "objIntArrayField": [1, 2, 3, 4, 5]
            },
            "unionField": "This can be a string, a number, or a boolean"
        })
