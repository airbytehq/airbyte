/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.json

import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.cdk.load.util.serializeToString
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class AirbyteSchemaTypeToJsonSchemaTest {
    // A json of every supported type
    private val airbyteType =
        ObjectType(
            mapOf(
                    "name" to StringType,
                    "age" to IntegerType,
                    "is_cool" to BooleanType,
                    "height" to NumberType,
                    "alt_integer" to IntegerType,
                    "friends" to ArrayType(FieldType(StringType, true)),
                    "mixed_array" to
                        ArrayType(
                            FieldType(UnionType.of(StringType, IntegerType), nullable = true)
                        ),
                    "address" to
                        ObjectType(
                            linkedMapOf(
                                "street" to FieldType(StringType, true),
                                "city" to FieldType(StringType, true)
                            )
                        ),
                    "combined_denormalized" to
                        ObjectType(linkedMapOf("name" to FieldType(StringType, true))),
                    "union_array" to
                        ArrayType(FieldType(UnionType.of(StringType, IntegerType), true)),
                    "date" to DateType,
                    "time" to TimeTypeWithTimezone,
                    "time_without_timezone" to TimeTypeWithoutTimezone,
                    "timestamp" to TimestampTypeWithTimezone,
                    "timestamp_without_timezone" to TimestampTypeWithoutTimezone
                )
                .map { it.key to FieldType(it.value, nullable = true) }
                .let { linkedMapOf(*it.toTypedArray()) }
        )

    // the json equivalent
    private val json =
        """
        {
          "type": "object",
          "properties": {
            "name": {
              "type": "string"
            },
            "age": {
              "type": "integer"
            },
            "is_cool": {
              "type": "boolean"
            },
            "height": {
              "type": "number"
            },
            "alt_integer": {
                "type": "integer"
            },
            "friends": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "mixed_array": {
                "type": "array",
                "items": {
                    "oneOf": [
                    {
                        "type": "string"
                    },
                    {
                        "type": "integer"
                    }
                    ]
                }
            },
            "address": {
              "type": "object",
              "properties": {
                "street": {
                  "type": "string"
                },
                "city": {
                  "type": "string"
                }
              }
            },
            "combined_denormalized": {
              "type": "object",
              "properties": {
                "name": {
                  "type": "string"
                }
              }
            },
            "union_array": {
              "type": "array",
              "items": {
                "oneOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "integer"
                  }
                ]
              }
            },
            "date": {
              "type": "string",
              "format": "date"
            },
            "time": {
              "type": "string",
              "format": "time",
              "airbyte_type": "time_with_timezone"
            },
            "time_without_timezone": {
              "type": "string",
              "format": "time",
              "airbyte_type": "time_without_timezone"
            },
            "timestamp": {
              "type": "string",
              "format": "date-time",
              "airbyte_type": "timestamp_with_timezone"
            },
            "timestamp_without_timezone": {
              "type": "string",
              "format": "date-time",
              "airbyte_type": "timestamp_without_timezone"
            }
          }
        }
    """.trimIndent()

    @Test
    fun testToJsonSchema() {
        val expected = json.deserializeToNode().serializeToString()
        val actual = AirbyteTypeToJsonSchema().convert(airbyteType).serializeToString()
        Assertions.assertEquals(expected, actual)
    }
}
