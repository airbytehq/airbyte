/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.jsonschema

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.commons.jackson.MoreMappers

enum class AirbyteJsonSchemaType {
    NULL,
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
    COMBINED,
    UNKNOWN;

    fun matchesValue(tree: JsonNode): Boolean {
        return when (this) {
            NULL -> tree.isNull
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
            COMBINED -> throw IllegalArgumentException("Union type cannot be matched")
            UNKNOWN -> true
        }
    }

    companion object {
        fun fromJsonSchema(schema: ObjectNode): AirbyteJsonSchemaType {
            if (schema.has("oneOf") || schema.has("anyOf") || schema.has("allOf")) {
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
                val typeArray =
                    if (type.isArray) {
                        type.elements().asSequence().filter { it.asText() != "null" }.toList()
                    } else {
                        listOf(type)
                    }

                if (typeArray.size > 1) {
                    return COMBINED
                }

                val typeStr =
                    if (typeArray.isEmpty()) {
                        "null"
                    } else {
                        typeArray[0].asText()
                    }

                val format = schema["format"]?.asText()
                val airbyteType = schema["airbyte_type"]?.asText()

                return when (typeStr) {
                    "null" -> NULL
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
                        if (
                            schema.has("properties") &&
                                !schema["properties"].isNull &&
                                !schema["properties"].isEmpty
                        ) {
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
                return UNKNOWN
            }
        }

        fun getOptions(schema: ObjectNode): List<ObjectNode> {
            return when (fromJsonSchema(schema)) {
                UNION -> {
                    schema["oneOf"].elements().asSequence().map { it as ObjectNode }.toList()
                }
                COMBINED -> {
                    schema["type"]
                        .elements()
                        .asSequence()
                        .map {
                            val objNode = MoreMappers.initMapper().createObjectNode()
                            objNode.put("type", it.asText())
                        }
                        .toList()
                }
                else -> {
                    listOf(schema)
                }
            }
        }

        fun getMatchingValueForType(value: JsonNode, options: ArrayNode): ObjectNode {
            return getMatchingValueForType(
                value,
                options.elements().asSequence().map { it as ObjectNode }.toList()
            )
        }

        fun getMatchingValueForType(value: JsonNode, options: Iterable<ObjectNode>): ObjectNode {
            val optionsAsList = options.toList()
            val matching =
                optionsAsList
                    .filter { option ->
                        when (val schemaType = fromJsonSchema(option)) {
                            UNION -> {
                                option["oneOf"]
                                    .elements()
                                    .asSequence()
                                    .filter { fromJsonSchema(it as ObjectNode).matchesValue(value) }
                                    .toList()
                                    .isNotEmpty()
                            }
                            COMBINED -> {
                                option["type"]
                                    .elements()
                                    .asSequence()
                                    .map {
                                        val objNode = MoreMappers.initMapper().createObjectNode()
                                        objNode.put("type", it.asText())
                                    }
                                    .filter { fromJsonSchema(it).matchesValue(value) }
                                    .toList()
                                    .isNotEmpty()
                            }
                            else -> {
                                schemaType.matchesValue(value)
                            }
                        }
                    }
                    .toList()
            if (matching.isEmpty()) {
                throw IllegalArgumentException(
                    "Union type ${value::class}(value redacted) does not match any options: $optionsAsList"
                )
            }
            return matching.first()
        }
    }
}
