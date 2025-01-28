/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.json

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.data.*

class AirbyteTypeToJsonSchema {
    private fun ofType(typeName: String): ObjectNode {
        return JsonNodeFactory.instance.objectNode().put("type", typeName)
    }

    fun convert(airbyteType: AirbyteType): JsonNode {
        return when (airbyteType) {
            is StringType -> ofType("string")
            is BooleanType -> ofType("boolean")
            is IntegerType -> ofType("integer")
            is NumberType -> ofType("number")
            is ArrayType ->
                JsonNodeFactory.instance
                    .objectNode()
                    .put("type", "array")
                    .set("items", convert(airbyteType.items.type))
            is ArrayTypeWithoutSchema -> ofType("array")
            is ObjectType -> {
                val objNode = ofType("object")
                val properties = objNode.putObject("properties")
                airbyteType.properties.forEach { (name, field) ->
                    properties.replace(name, convert(field.type))
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
            is TimeTypeWithTimezone -> {
                val timeNode = ofType("string").put("format", "time")
                timeNode.put("airbyte_type", "time_with_timezone")
            }
            is TimeTypeWithoutTimezone -> {
                val timeNode = ofType("string").put("format", "time")
                timeNode.put("airbyte_type", "time_without_timezone")
            }
            is TimestampTypeWithTimezone -> {
                val timestampNode = ofType("string").put("format", "date-time")
                timestampNode.put("airbyte_type", "timestamp_with_timezone")
            }
            is TimestampTypeWithoutTimezone -> {
                val timestampNode = ofType("string").put("format", "date-time")
                timestampNode.put("airbyte_type", "timestamp_without_timezone")
            }
            // In case of unknown type, just return {} (i.e. the accept-all JsonSchema)
            is UnknownType -> JsonNodeFactory.instance.objectNode()
        }
    }
}
