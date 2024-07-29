/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.jsonschema

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode

enum class AirbyteJsonSchemaType {
    BOOLEAN,
    INTEGER,
    NUMBER,
    STRING,
    BINARY_DATA,
    DATE,
    TIMESTAMP_WITH_TIMEZONE,
    TIMESTAMP_WITHOUT_TIMEZONE,
    TIME_WITH_TIMEZONE,
    TIME_WITHOUT_TIMEZONE,
    ARRAY_WITHOUT_ITEMS,
    ARRAY_WITH_ITEM,
    ARRAY_WITH_ITEMS,
    OBJECT_WITHOUT_PROPERTIES,
    OBJECT_WITH_PROPERTIES,
    UNION,
    COMBINED;

    fun matchesValue(tree: JsonNode): Boolean {
        return when (this) {
            BOOLEAN -> tree.isBoolean
            INTEGER -> tree.isIntegralNumber || tree.isInt || tree.isBigInteger
            NUMBER ->
                tree.isDouble ||
                    tree.isFloat ||
                    tree.isIntegralNumber ||
                    tree.isInt ||
                    tree.isBigInteger
            STRING -> tree.isTextual
            BINARY_DATA -> tree.isBinary || tree.isTextual
            DATE,
            TIMESTAMP_WITH_TIMEZONE,
            TIMESTAMP_WITHOUT_TIMEZONE,
            TIME_WITH_TIMEZONE,
            TIME_WITHOUT_TIMEZONE -> tree.isTextual
            ARRAY_WITHOUT_ITEMS,
            ARRAY_WITH_ITEM,
            ARRAY_WITH_ITEMS -> tree.isArray
            OBJECT_WITHOUT_PROPERTIES -> tree.isObject
            OBJECT_WITH_PROPERTIES -> tree.isObject
            UNION,
            COMBINED -> throw IllegalStateException("Union type cannot be matched")
        }
    }

    companion object {
        fun fromJsonSchema(schema: ObjectNode): AirbyteJsonSchemaType {
            if (schema.has("oneOf")) {
                return UNION
            }

            val ref = schema["\$ref"]?.asText()
            if (ref != null) {
                return when (ref) {
                    "WellKnownTypes.json#/definitions/Boolean" -> BOOLEAN
                    "WellKnownTypes.json#/definitions/Integer" -> INTEGER
                    "WellKnownTypes.json#/definitions/Number" -> NUMBER
                    "WellKnownTypes.json#/definitions/String" -> STRING
                    "WellKnownTypes.json#/definitions/BinaryData" -> BINARY_DATA
                    "WellKnownTypes.json#/definitions/Date" -> DATE
                    "WellKnownTypes.json#/definitions/TimestampWithTimezone" ->
                        TIMESTAMP_WITH_TIMEZONE
                    "WellKnownTypes.json#/definitions/TimestampWithoutTimezone" ->
                        TIMESTAMP_WITHOUT_TIMEZONE
                    "WellKnownTypes.json#/definitions/TimeWithTimezone" -> TIME_WITH_TIMEZONE
                    "WellKnownTypes.json#/definitions/TimeWithoutTimezone" -> TIME_WITHOUT_TIMEZONE
                    else -> throw IllegalArgumentException("Unsupported reference type: $ref")
                }
            }

            val type = schema["type"]
            if (type != null) {
                if (type.isArray && type.size() > 1) {
                    return COMBINED
                }

                val typeStr =
                    if (type.isArray) {
                        type[0].asText()
                    } else {
                        type.asText()
                    }

                val format = schema["format"]?.asText()
                val airbyteType = schema["airbyte_type"]?.asText()

                return when (typeStr) {
                    "boolean" -> BOOLEAN
                    "integer" -> INTEGER
                    "number" -> {
                        if (airbyteType == "integer") {
                            INTEGER
                        } else {
                            NUMBER
                        }
                    }
                    "string" -> {
                        when (format) {
                            "big_integer" -> INTEGER
                            "float" -> NUMBER
                            "date" -> DATE
                            "time" -> {
                                when (airbyteType) {
                                    null,
                                    "time_with_timezone" -> TIME_WITH_TIMEZONE
                                    "time_without_timezone" -> TIME_WITHOUT_TIMEZONE
                                    else ->
                                        throw IllegalArgumentException(
                                            "Unknown time format: $airbyteType"
                                        )
                                }
                            }
                            "date-time" -> {
                                when (airbyteType) {
                                    null,
                                    "timestamp_with_timezone" -> TIMESTAMP_WITH_TIMEZONE
                                    "timestamp_without_timezone" -> TIMESTAMP_WITHOUT_TIMEZONE
                                    else ->
                                        throw IllegalArgumentException(
                                            "Unknown date-time format: $airbyteType"
                                        )
                                }
                            }
                            else -> STRING
                        }
                    }
                    "array" -> {
                        when {
                            schema.has("items") -> {
                                if (schema["items"].isArray) {
                                    ARRAY_WITH_ITEMS
                                } else {
                                    ARRAY_WITH_ITEM
                                }
                            }
                            else -> ARRAY_WITHOUT_ITEMS
                        }
                    }
                    "object" -> {
                        if (schema.has("properties")) {
                            OBJECT_WITH_PROPERTIES
                        } else {
                            OBJECT_WITHOUT_PROPERTIES
                        }
                    }
                    else -> throw IllegalArgumentException("Unknown schema type: $type")
                }
            } else if (schema.has("properties")) {
                // Usually the root node
                return OBJECT_WITH_PROPERTIES
            } else {
                throw IllegalArgumentException("Unspecified schema type")
            }
        }

        fun getMatchingValueForType(value: JsonNode, options: ArrayNode): ObjectNode {
            return getMatchingValueForType(
                value,
                options.elements().asSequence().map { it as ObjectNode }.toList()
            )
        }

        fun getMatchingValueForType(value: JsonNode, options: Iterable<ObjectNode>): ObjectNode {
            val matching =
                options
                    .filter { option ->
                        val rv = fromJsonSchema(option).matchesValue(value)
                        rv
                    }
                    .toList()
            if (matching.size != 1) {
                throw IllegalArgumentException("Union type does not match exactly one option")
            }
            return matching.first()
        }
    }
}
