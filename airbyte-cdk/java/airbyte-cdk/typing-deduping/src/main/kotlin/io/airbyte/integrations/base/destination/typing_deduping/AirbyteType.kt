/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.fasterxml.jackson.databind.node.TextNode
import org.slf4j.Logger
import org.slf4j.LoggerFactory

interface AirbyteType {
    val typeName: String

    companion object {
        /**
         * The most common call pattern is probably to use this method on the stream schema, verify
         * that it's an [Struct] schema, and then call [Struct.properties] to get the columns.
         *
         * If the top-level schema is not an object, then we can't really do anything with it, and
         * should probably fail the sync. (but see also [Union.asColumns]).
         */
        @JvmStatic
        fun fromJsonSchema(schema: JsonNode): AirbyteType {
            try {
                val topLevelType = schema["type"]
                if (topLevelType != null) {
                    if (topLevelType.isTextual) {
                        if (nodeMatches(topLevelType, "object")) {
                            return getStruct(schema)
                        } else if (nodeMatches(topLevelType, "array")) {
                            return getArray(schema)
                        }
                    } else if (topLevelType.isArray) {
                        return fromArrayJsonSchema(schema, topLevelType)
                    }
                } else if (schema.hasNonNull("oneOf")) {
                    val options: MutableList<AirbyteType> = ArrayList()
                    schema["oneOf"].elements().forEachRemaining { element: JsonNode ->
                        options.add(fromJsonSchema(element))
                    }
                    return UnsupportedOneOf(options)
                } else if (schema.hasNonNull("properties")) {
                    // The schema has neither type nor oneof, but it does have properties. Assume
                    // we're looking at a
                    // struct.
                    // This is for backwards-compatibility with legacy normalization.
                    return getStruct(schema)
                }
                return AirbyteProtocolType.Companion.fromJson(schema)
            } catch (e: Exception) {
                LOGGER.error("Exception parsing JSON schema {}: {}; returning UNKNOWN.", schema, e)
                return AirbyteProtocolType.UNKNOWN
            }
        }

        fun nodeMatches(node: JsonNode?, value: String?): Boolean {
            if (node == null || !node.isTextual) {
                return false
            }
            return node == TextNode.valueOf(value)
        }

        private fun getStruct(schema: JsonNode): Struct {
            val propertiesMap = LinkedHashMap<String, AirbyteType>()
            val properties = schema["properties"]
            properties?.fields()?.forEachRemaining { property: Map.Entry<String, JsonNode> ->
                val key = property.key
                val value = property.value
                propertiesMap[key] = fromJsonSchema(value)
            }
            return Struct(propertiesMap)
        }

        private fun getArray(schema: JsonNode): Array {
            val items = schema["items"]
            return if (items == null) {
                Array(AirbyteProtocolType.UNKNOWN)
            } else {
                Array(fromJsonSchema(items))
            }
        }

        private fun fromArrayJsonSchema(schema: JsonNode, array: JsonNode): AirbyteType {
            val typeOptions: MutableList<String> = ArrayList()
            array.elements().forEachRemaining { element: JsonNode ->
                // ignore "null" type and remove duplicates
                val type = element.asText("")
                if ("null" != type && !typeOptions.contains(type)) {
                    typeOptions.add(element.asText())
                }
            }

            // we encounter an array of types that actually represents a single type rather than a
            // Union
            if (typeOptions.size == 1) {
                return if (typeOptions[0] == "object") {
                    getStruct(schema)
                } else if (typeOptions[0] == "array") {
                    getArray(schema)
                } else {
                    AirbyteProtocolType.Companion.fromJson(
                        getTrimmedJsonSchema(schema, typeOptions[0])
                    )
                }
            }

            // Recurse into a schema that forces a specific one of each option
            val options =
                typeOptions.map { typeOption: String ->
                    fromJsonSchema(getTrimmedJsonSchema(schema, typeOption))
                }

            return Union(options)
        }

        // Duplicates the JSON schema but keeps only one type
        private fun getTrimmedJsonSchema(schema: JsonNode, type: String): JsonNode {
            val schemaClone = schema.deepCopy<JsonNode>()
            // schema is guaranteed to be an object here, because we know it has a `type` key
            (schemaClone as ObjectNode).put("type", type)
            return schemaClone
        }

        val LOGGER: Logger = LoggerFactory.getLogger(AirbyteType::class.java)
    }
}
