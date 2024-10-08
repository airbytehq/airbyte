/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import com.fasterxml.jackson.databind.node.ObjectNode

class AirbyteTypeToJsonSchema {
    private fun ofType(typeName: String): ObjectNode {
        return JsonNodeFactory.instance.objectNode().put("type", typeName)
    }

    fun convert(airbyteType: AirbyteType): JsonNode {
        return when (airbyteType) {
            is NullType -> ofType("null")
            is StringType -> ofType("string")
            is BooleanType -> ofType("boolean")
            is IntegerType -> ofType("integer")
            is NumberType -> ofType("number")
            is ArrayType ->
                JsonNodeFactory.instance
                    .objectNode()
                    .put("type", "array")
                    .set("items", fromFieldType(airbyteType.items))
            is ArrayTypeWithoutSchema -> ofType("array")
            is ObjectType -> {
                val objNode = ofType("object")
                val properties = objNode.putObject("properties")
                airbyteType.properties.forEach { (name, field) ->
                    properties.replace(name, fromFieldType(field))
                }
                objNode
            }
            is ObjectTypeWithoutSchema -> ofType("object")
            is ObjectTypeWithEmptySchema -> {
                val objectNode = ofType("object")
                objectNode.putObject("properties")
                objectNode
            }
            is UnionType -> {
                val unionNode = JsonNodeFactory.instance.objectNode()
                val unionOptions = unionNode.putArray("oneOf")
                airbyteType.options.forEach { unionOptions.add(convert(it)) }
                unionNode
            }
            is DateType -> ofType("string").put("format", "date")
            is TimeType -> {
                val timeNode = ofType("string").put("format", "time")
                if (airbyteType.hasTimezone) {
                    timeNode.put("airbyte_type", "time_with_timezone")
                } else {
                    timeNode.put("airbyte_type", "time_without_timezone")
                }
            }
            is TimestampType -> {
                val timestampNode = ofType("string").put("format", "date-time")
                if (airbyteType.hasTimezone) {
                    timestampNode.put("airbyte_type", "timestamp_with_timezone")
                } else {
                    timestampNode.put("airbyte_type", "timestamp_without_timezone")
                }
            }
            else -> throw IllegalArgumentException("Unknown type: $airbyteType")
        }
    }

    private fun fromFieldType(field: FieldType): JsonNode {
        if (field.nullable) {
            if (field.type is UnionType) {
                return convert(UnionType(options = field.type.options + NullType))
            }
            return convert(UnionType(options = listOf(field.type, NullType)))
        }
        return convert(field.type)
    }
}
