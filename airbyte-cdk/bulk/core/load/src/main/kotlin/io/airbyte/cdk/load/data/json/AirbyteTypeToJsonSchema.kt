/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.json

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.data.*

class AirbyteTypeToJsonSchema {
    private fun ofType(typeName: String, nullable: Boolean): ObjectNode {
        val objectNode = JsonNodeFactory.instance.objectNode()
        if (nullable) {
            objectNode.putArray("type").add("null").add(typeName)
        } else {
            objectNode.put("type", typeName)
        }
        return objectNode
    }

    fun convert(airbyteType: AirbyteType): JsonNode {
        return convertInner(airbyteType, false)
    }

    private fun convertInner(airbyteType: AirbyteType, nullable: Boolean = false): JsonNode {
        return when (airbyteType) {
            is StringType -> ofType("string", nullable)
            is BooleanType -> ofType("boolean", nullable)
            is IntegerType -> ofType("integer", nullable)
            is NumberType -> ofType("number", nullable)
            is ArrayType ->
                ofType("array", nullable)
                    .set("items", convertInner(airbyteType.items.type, airbyteType.items.nullable))
            is ArrayTypeWithoutSchema -> ofType("array", nullable)
            is ObjectType -> {
                val objNode = ofType("object", nullable)
                val properties = objNode.putObject("properties")
                airbyteType.properties.forEach { (name, field) ->
                    properties.replace(name, convertInner(field.type, field.nullable))
                }
                if (!airbyteType.required.isEmpty()) {
                    val required = objNode.putArray("required")
                    airbyteType.required.forEach { required.add(it) }
                }
                objNode.put("additionalProperties", airbyteType.additionalProperties)
                objNode
            }
            is ObjectTypeWithoutSchema -> ofType("object", nullable)
            is ObjectTypeWithEmptySchema -> {
                val objectNode = ofType("object", nullable)
                objectNode.putObject("properties")
                objectNode
            }
            is UnionType -> {
                val unionNode = JsonNodeFactory.instance.objectNode()
                val unionOptions = unionNode.putArray("oneOf")
                airbyteType.options.forEach { unionOptions.add(convert(it)) }
                unionNode
            }
            is DateType -> ofType("string", nullable).put("format", "date")
            is TimeTypeWithTimezone -> {
                val timeNode = ofType("string", nullable).put("format", "time")
                timeNode.put("airbyte_type", "time_with_timezone")
            }
            is TimeTypeWithoutTimezone -> {
                val timeNode = ofType("string", nullable).put("format", "time")
                timeNode.put("airbyte_type", "time_without_timezone")
            }
            is TimestampTypeWithTimezone -> {
                val timestampNode = ofType("string", nullable).put("format", "date-time")
                timestampNode.put("airbyte_type", "timestamp_with_timezone")
            }
            is TimestampTypeWithoutTimezone -> {
                val timestampNode = ofType("string", nullable).put("format", "date-time")
                timestampNode.put("airbyte_type", "timestamp_without_timezone")
            }
            is UnknownType -> airbyteType.schema
        }
    }
}
