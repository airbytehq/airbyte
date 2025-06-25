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
              "type": ["null", "string"]
            },
            "age": {
              "type": ["null", "integer"]
            },
            "is_cool": {
              "type": ["null", "boolean"]
            },
            "height": {
              "type": ["null", "number"]
            },
            "alt_integer": {
                "type": ["null", "integer"]
            },
            "friends": {
              "type": ["null", "array"],
              "items": {
                "type": ["null", "string"]
              }
            },
            "mixed_array": {
                "type": ["null", "array"],
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
              "type": ["null", "object"],
              "properties": {
                "street": {
                  "type": ["null", "string"]
                },
                "city": {
                  "type": ["null", "string"]
                }
              },
              "additionalProperties": true
            },
            "combined_denormalized": {
              "type": ["null", "object"],
              "properties": {
                "name": {
                  "type": ["null", "string"]
                }
              },
              "additionalProperties": true
            },
            "union_array": {
              "type": ["null", "array"],
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
              "type": ["null", "string"],
              "format": "date"
            },
            "time": {
              "type": ["null", "string"],
              "format": "time",
              "airbyte_type": "time_with_timezone"
            },
            "time_without_timezone": {
              "type": ["null", "string"],
              "format": "time",
              "airbyte_type": "time_without_timezone"
            },
            "timestamp": {
              "type": ["null", "string"],
              "format": "date-time",
              "airbyte_type": "timestamp_with_timezone"
            },
            "timestamp_without_timezone": {
              "type": ["null", "string"],
              "format": "date-time",
              "airbyte_type": "timestamp_without_timezone"
            }
          },
          "additionalProperties": true
        }
    """.trimIndent()

    @Test
    fun testToJsonSchema() {
        val expected = json.deserializeToNode().serializeToString()
        val actual = AirbyteTypeToJsonSchema().convert(airbyteType).serializeToString()
        Assertions.assertEquals(expected, actual)
    }

    @Test
    internal fun `test given additional properties when serialize then set additional properties`() {
        val airbyteType = ObjectType(linkedMapOf<String, FieldType>(), true)
        val node = AirbyteTypeToJsonSchema().convert(airbyteType)
        Assertions.assertTrue(node.get("additionalProperties").asBoolean())
    }

    @Test
    internal fun `test given additional properties is not defined when serialize then do not specify`() {
        val airbyteType = ObjectType(linkedMapOf<String, FieldType>())
        val node = AirbyteTypeToJsonSchema().convert(airbyteType)
        Assertions.assertTrue(node.get("additionalProperties").booleanValue())
    }

    @Test
    internal fun `test given required has elements when serialize then set required`() {
        val required = listOf("requiredProperty")
        val airbyteType =
            ObjectType(properties = linkedMapOf<String, FieldType>(), required = required)

        val node = AirbyteTypeToJsonSchema().convert(airbyteType)

        Assertions.assertEquals(
            required,
            node.get("required").asIterable().map { it.asText() }.toList(),
        )
    }

    @Test
    internal fun `test given required is empty list when serialize then do not specify`() {
        val airbyteType =
            ObjectType(properties = linkedMapOf<String, FieldType>(), required = emptyList())
        val node = AirbyteTypeToJsonSchema().convert(airbyteType)
        Assertions.assertNull(node.get("required"))
    }

    @Test
    internal fun `test given nullable when serialize then set type as nullable`() {
        val airbyteType =
            ObjectType(
                properties = linkedMapOf<String, FieldType>("aField" to FieldType(StringType, true))
            )
        val node = AirbyteTypeToJsonSchema().convert(airbyteType)
        Assertions.assertEquals(
            listOf<String>("null", "string"),
            node
                .get("properties")
                .asIterable()
                .toList()[0]
                .get("type")
                .asIterable()
                .map { it.asText() }
                .toList()
        )
    }
}
