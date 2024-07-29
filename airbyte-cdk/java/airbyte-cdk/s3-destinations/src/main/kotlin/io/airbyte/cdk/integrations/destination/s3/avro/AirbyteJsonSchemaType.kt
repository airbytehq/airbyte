package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode

enum class AirbyteJsonSchemaType {
    BOOLEAN,
    INTEGER,
    NUMBER,
    STRING,

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

    UNION;

    fun matchesValue(tree: JsonNode): Boolean {
        return when (this) {
            BOOLEAN -> tree.isBoolean
            INTEGER -> tree.isInt
            NUMBER -> tree.isDouble
            STRING -> tree.isTextual

            DATE -> tree.isTextual
            TIMESTAMP_WITH_TIMEZONE -> tree.isLong
            TIMESTAMP_WITHOUT_TIMEZONE -> tree.isLong
            TIME_WITH_TIMEZONE -> tree.isTextual
            TIME_WITHOUT_TIMEZONE -> tree.isLong

            ARRAY_WITHOUT_ITEMS -> tree.isArray && tree.isEmpty
            ARRAY_WITH_ITEM -> tree.isArray && tree.size() == 1
            ARRAY_WITH_ITEMS -> tree.isArray

            OBJECT_WITHOUT_PROPERTIES -> tree.isObject
            OBJECT_WITH_PROPERTIES -> tree.isObject

            UNION -> throw IllegalStateException("Union type cannot be matched")
        }
    }

    companion object {
        fun fromJsonSchema(schema: ObjectNode): AirbyteJsonSchemaType {
            if (schema.has("oneOf")) {
                return UNION
            }

            val type = schema["type"].asText()
            val format = schema["format"]?.asText()
            val airbyteType = schema["airbyte_type"]?.asText()

            return when (type) {
                "boolean" -> BOOLEAN
                "integer" -> INTEGER
                "number" -> {
                    if (airbyteType == "integer") {
                        INTEGER
                    } else {
                        NUMBER
                    }
                }
                "string" -> STRING
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
                    when {
                        schema.has("properties") -> OBJECT_WITH_PROPERTIES
                        else -> OBJECT_WITHOUT_PROPERTIES
                    }
                }
                else -> {
                    when (format) {
                        "date" -> DATE
                        "time" -> {
                            when (airbyteType) {
                                null,
                                "time_with_timezone" -> TIME_WITH_TIMEZONE
                                "time_without_timezone" -> TIME_WITHOUT_TIMEZONE
                                else -> throw IllegalArgumentException("Unknown time format: $airbyteType")
                            }
                        }
                        "date-time" -> {
                            when (airbyteType) {
                                null,
                                "timestamp_with_timezone" -> TIMESTAMP_WITH_TIMEZONE
                                "timestamp_without_timezone" -> TIMESTAMP_WITHOUT_TIMEZONE
                                else -> throw IllegalArgumentException("Unknown date-time format: $airbyteType")
                            }
                        }
                        else -> throw IllegalArgumentException("Unknown type: $type")
                    }
                }
            }
        }
    }
}
