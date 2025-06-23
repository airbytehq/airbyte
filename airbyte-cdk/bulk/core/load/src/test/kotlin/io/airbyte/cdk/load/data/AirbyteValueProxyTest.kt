/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class AirbyteValueProxyTest {
    // One of each type of field x unset x nullable
    val testJsonPopulated =
        """
        {
            "booleanField": true,
            "stringField": "string",
            "integerField": 1234567890123456789,
            "numberField": 1234567890123456789.123456789,
            "dateField": "2023-10-01",
            "timeWithTimezoneField": "12:34:56+00:00",
            "timeWithoutTimezoneField": "12:34:56",
            "timestampWithTimezoneField": "2023-10-01T12:34:56+00:00",
            "timestampWithoutTimezoneField": "2023-10-01T12:34:56",
            "objectField": {"key": "value"},
            "arrayField": [1, 2, 3],
            "unionFieldStringOrInt": "union string"
        }
    """.trimIndent()
    val testJsonNull =
        """
        {
            "booleanField": null,
            "stringField": null,
            "integerField": null,
            "numberField": null,
            "dateField": null,
            "timeWithTimezoneField": null,
            "timeWithoutTimezoneField": null,
            "timestampWithTimezoneField": null,
            "timestampWithoutTimezoneField": null,
            "objectField": null,
            "arrayField": null,
            "unionFieldStringOrInt": null
        }
    """.trimIndent()
    val testJsonEmpty = "{}"

    companion object {
        val ALL_TYPES_SCHEMA =
            ObjectType(
                linkedMapOf(
                    "booleanField" to FieldType(BooleanType, nullable = true),
                    "stringField" to FieldType(StringType, nullable = true),
                    "integerField" to FieldType(IntegerType, nullable = true),
                    "numberField" to FieldType(NumberType, nullable = true),
                    "dateField" to FieldType(DateType, nullable = true),
                    "timeWithTimezoneField" to FieldType(TimeTypeWithTimezone, nullable = true),
                    "timeWithoutTimezoneField" to
                        FieldType(TimeTypeWithoutTimezone, nullable = true),
                    "timestampWithTimezoneField" to
                        FieldType(TimestampTypeWithTimezone, nullable = true),
                    "timestampWithoutTimezoneField" to
                        FieldType(TimestampTypeWithoutTimezone, nullable = true),
                    "objectField" to
                        FieldType(
                            ObjectType(linkedMapOf("key" to FieldType(StringType, true))),
                            nullable = true
                        ),
                    "arrayField" to
                        FieldType(ArrayType(FieldType(IntegerType, true)), nullable = true),
                    "unionFieldStringOrInt" to
                        FieldType(UnionType.of(StringType, IntegerType), nullable = true)
                )
            )
    }

    val stream: DestinationStream =
        DestinationStream(
            unmappedNamespace = "namespace",
            unmappedName = "name",
            importType = Append,
            generationId = 1,
            minimumGenerationId = 0,
            syncId = 1,
            includeFiles = false,
            schema = ALL_TYPES_SCHEMA,
            namespaceMapper = NamespaceMapper()
        )

    private fun ifNull(value: JsonNode?): JsonNode? {
        return if (value == null || value.isNull) null else value
    }

    private fun validate(expected: ObjectNode, actual: AirbyteValueProxy) {
        val proxyFields = stream.airbyteValueProxyFieldAccessors
        val objectTreeFromProxy = actual.asJson(proxyFields)
        ALL_TYPES_SCHEMA.properties.forEach { (name, _) ->
            Assertions.assertEquals(
                ifNull(expected.get(name))?.toString(),
                objectTreeFromProxy.get(name)?.toString(),
                "comparing $name in ${expected.serializeToString()}",
            )
        }
    }

    @Test
    fun `jsonl proxy identical to its source`() {
        listOf(testJsonPopulated, testJsonEmpty, testJsonNull).forEach { testJson ->
            val objectTree = testJson.deserializeToNode() as ObjectNode
            val proxy = AirbyteValueJsonlProxy(objectTree)
            validate(objectTree, proxy)
        }
    }

    @Test
    fun `protobuf proxy identical to its source`() {
        listOf(testJsonPopulated, testJsonEmpty, testJsonNull).forEach { testJson ->
            val objectTree = testJson.deserializeToNode() as ObjectNode
            val airbyteValues = objectTree.toAirbyteValue() as ObjectValue
            val proxyFields = stream.airbyteValueProxyFieldAccessors

            // Build the protobuf data array
            val data = mutableListOf<AirbyteValueProtobuf>()
            proxyFields.forEach { field ->
                val protoField =
                    AirbyteValueToProtobuf()
                        .toProtobuf(airbyteValues.values[field.name] ?: NullValue, field.type)
                data.add(protoField)
            }

            val proxy = AirbyteValueProtobufProxy(data)
            validate(objectTree, proxy)
        }
    }
}
