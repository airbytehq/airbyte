/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.JsonNodeFactory

class AirbyteValueToJson {
    fun convert(value: AirbyteValue): JsonNode {
        return when (value) {
            is ArrayValue ->
                JsonNodeFactory.instance.arrayNode().addAll(value.values.map { convert(it) })
            is BooleanValue -> JsonNodeFactory.instance.booleanNode(value.value)
            is DateValue -> JsonNodeFactory.instance.textNode(value.value)
            is IntegerValue -> JsonNodeFactory.instance.numberNode(value.value)
            is NullValue -> JsonNodeFactory.instance.nullNode()
            is NumberValue -> JsonNodeFactory.instance.numberNode(value.value)
            is ObjectValue -> {
                val objNode = JsonNodeFactory.instance.objectNode()
                value.values.forEach { (name, field) -> objNode.replace(name, convert(field)) }
                objNode
            }
            is StringValue -> JsonNodeFactory.instance.textNode(value.value)
            is TimeValue -> JsonNodeFactory.instance.textNode(value.value)
            is TimestampValue -> JsonNodeFactory.instance.textNode(value.value)
            is UnknownValue -> throw IllegalArgumentException("Unknown value: $value")
        }
    }
}

fun AirbyteValue.toJson(): JsonNode {
    return AirbyteValueToJson().convert(this)
}
