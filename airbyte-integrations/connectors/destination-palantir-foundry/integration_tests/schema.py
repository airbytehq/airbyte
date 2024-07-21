JSON_SCHEMA_ALL_DATA_TYPES = {
    "type": "object",
    "properties": {
        "stringField": {
            "type": "string"
        },
        "booleanField": {
            "type": "boolean"
        },
        "dateField": {
            "type": "string",
            "format": "date"
        },
        "timestampWithoutTimezoneField": {
            "type": "string",
            "format": "date-time",
            "airbyte_type": "timestamp_without_timezone"
        },
        "timestampWithTimezoneField": {
            "type": "string",
            "format": "date-time",
            "airbyte_type": "timestamp_with_timezone"
        },
        "timestampWithTimezoneField2": {
            "type": "string",
            "format": "date-time",
        },
        "timeWithoutTimezoneField": {
            "type": "string",
            "format": "time",
            "airbyte_type": "time_without_timezone"
        },
        "timeWithTimezoneField": {
            "type": "string",
            "format": "time",
            "airbyte_type": "time_with_timezone"
        },
        "integerField": {
            "type": "integer"
        },
        "integerFieldWithAirbyte": {
            "type": "number",
            "airbyte_type": "integer"
        },
        "numberField": {
            "type": "number"
        },
        "stringArrayField": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "objectField": {
            "type": "object",
            "properties": {
                "objStringField": {
                    "type": "string"
                },
                "objIntArrayField": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    }
                },
            }
        },
        "unionField": {
            "oneOf": [
                {"type": "string"},
                {"type": "number"},
                {"type": "boolean"}
            ]
        }
    }
}

SAMPLE_RECORDS = [
    {
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
    },
    {
        "stringField": "Hello, World!",
        "booleanField": False,
        "dateField": "2022-02-02",
        "timestampWithoutTimezoneField": "2022-02-02T13:00:00",
        "timestampWithTimezoneField": "2022-02-02T13:00:00Z",
        "timestampWithTimezoneField2": "2022-02-02T13:00:00+00:00",
        "timeWithoutTimezoneField": "13:00:00",
        "timeWithTimezoneField": "13:00:00+00:00",
        "integerField": 22345,
        "integerFieldWithAirbyte": 67891,
        "numberField": 223.45,
        "stringArrayField": ["item4", "item5", "item6"],
        "objectField": {
            "objStringField": "Nested string 2",
            "objIntArrayField": [6, 7, 8, 9, 10]
        },
        "unionField": 1.25
    },
    {
        "stringField": "Hello, Universe!",
        "booleanField": True,
        "dateField": "2022-03-03",
        "timestampWithoutTimezoneField": "2022-03-03T14:00:00",
        "timestampWithTimezoneField": "2022-03-03T14:00:00Z",
        "timestampWithTimezoneField2": "2022-03-03T14:00:00+00:00",
        "timeWithoutTimezoneField": "14:00:00",
        "timeWithTimezoneField": "14:00:00+00:00",
        "integerField": 32345,
        "integerFieldWithAirbyte": 67892,
        "numberField": 323.45,
        "stringArrayField": ["item7", "item8", "item9"],
        "objectField": {
            "objStringField": "Nested string 3",
            "objIntArrayField": [11, 12, 13, 14, 15]
        },
        "unionField": False
    },
    {
        "stringField": "Hello, Multiverse!",
        "booleanField": True,
        "dateField": "2022-04-04",
        "timestampWithoutTimezoneField": "2022-04-04T15:00:00",
        "timestampWithTimezoneField": "2022-04-04T15:00:00Z",
        "timestampWithTimezoneField2": "2022-04-04T15:00:00+00:00",
        "timeWithoutTimezoneField": "15:00:00",
        "timeWithTimezoneField": "15:00:00+00:00",
        "integerField": 42345,
        "integerFieldWithAirbyte": 67893,
        "numberField": 423.45,
        "stringArrayField": ["item10", "item11", "item12"],
        "objectField": {
            "objStringField": "Nested string 4",
            "objIntArrayField": [16, 17, 18, 19, 20]
        },
        "unionField": "This can be a string, a number, or a boolean"
    },
    {
        "stringField": "Hello, Everything!",
        "booleanField": True,
        "dateField": "2022-05-05",
        "timestampWithoutTimezoneField": "2022-05-05T16:00:00",
        "timestampWithTimezoneField": "2022-05-05T16:00:00Z",
        "timestampWithTimezoneField2": "2022-05-05T16:00:00+00:00",
        "timeWithoutTimezoneField": "16:00:00",
        "timeWithTimezoneField": "16:00:00+00:00",
        "integerField": 52345,
        "integerFieldWithAirbyte": 67894,
        "numberField": 523.45,
        "stringArrayField": ["item13", "item14", "item15"],
        "objectField": {
            "objStringField": "Nested string 5",
            "objIntArrayField": [21, 22, 23, 24, 25]
        },
        "unionField": 2.5
    }
]
