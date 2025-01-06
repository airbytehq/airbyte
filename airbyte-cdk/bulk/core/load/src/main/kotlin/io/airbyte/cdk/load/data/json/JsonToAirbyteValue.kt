/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.json

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.JsonNodeType
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.data.*

/**
 * Naively convert a json node to the equivalent AirbyteValue. Note that this does not match against
 * a declared schema; it simply does the most obvious conversion.
 */
class JsonToAirbyteValue {
    fun convert(json: JsonNode): AirbyteValue {
        return when (json.nodeType!!) {
            JsonNodeType.NULL,
            JsonNodeType.MISSING -> NullValue
            JsonNodeType.BOOLEAN -> BooleanValue(json.booleanValue())
            JsonNodeType.NUMBER -> {
                if (json.isIntegralNumber) {
                    IntegerValue(json.bigIntegerValue())
                } else {
                    NumberValue(json.decimalValue())
                }
            }
            JsonNodeType.STRING -> StringValue(json.textValue())
            JsonNodeType.ARRAY -> ArrayValue(json.map { convert(it) })
            JsonNodeType.OBJECT ->
                ObjectValue(
                    (json as ObjectNode).properties().associateTo(linkedMapOf()) { (k, v) ->
                        k to convert(v)
                    }
                )
            JsonNodeType.POJO,
            JsonNodeType.BINARY ->
                throw NotImplementedError("Unsupported JsonNode type: ${json.nodeType}")
        }
    }
}

fun JsonNode.toAirbyteValue(): AirbyteValue {
    return JsonToAirbyteValue().convert(this)
}
