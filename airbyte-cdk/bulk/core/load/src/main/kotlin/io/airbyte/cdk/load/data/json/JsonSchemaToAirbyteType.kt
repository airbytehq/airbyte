/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.json

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.data.*

class JsonSchemaToAirbyteType {
    fun convert(schema: JsonNode): AirbyteType = convertInner(schema)!!

    private fun convertInner(schema: JsonNode): AirbyteType? {
        // try {
        if (schema.isObject && schema.has("type")) {
            // Normal json object with {"type": ..., ...}
            val schemaType = (schema as ObjectNode).get("type")
            return if (schemaType.isTextual) {
                // {"type": <string>, ...}
                when (schema.get("type").asText()) {
                    "string" -> fromString(schema)
                    "boolean" -> BooleanType
                    "integer" -> IntegerType
                    "number" -> fromNumber(schema)
                    "array" -> fromArray(schema)
                    "object" -> fromObject(schema)
                    "null" -> null
                    else ->
                        throw IllegalArgumentException(
                            "Unknown type: ${
                                schema.get("type").asText()
                            }"
                        )
                }
            } else if (schemaType.isArray) {
                // {"type": [...], ...}
                unionFromCombinedTypes(schemaType.toList(), schema)
            } else {
                UnknownType("unsupported type for 'type' field: $schemaType")
            }
        } else if (schema.isObject) {
            // {"oneOf": [...], ...} or {"anyOf": [...], ...} or {"allOf": [...], ...}
            val options = schema.get("oneOf") ?: schema.get("anyOf") ?: schema.get("allOf")
            return if (options != null) {
                optionsToUnionOrSingleType(options.mapNotNull { convertInner(it as ObjectNode) })
            } else {
                // Default to object if no type and not a union type
                convertInner((schema as ObjectNode).put("type", "object"))
            }
        } else if (schema.isTextual) {
            // "<typename>"
            val typeSchema = JsonNodeFactory.instance.objectNode().put("type", schema.asText())
            return convertInner(typeSchema)
        } else {
            return UnknownType("Unknown schema type: $schema")
        }
    } // catch (t: Throwable) {
    //  return UnknownType(t.message ?: "Unknown error")
    // }
    // }

    private fun fromString(schema: ObjectNode): AirbyteType =
        when (schema.get("format")?.asText()) {
            "date" -> DateType
            "time" ->
                if (schema.get("airbyte_type")?.asText() == "time_without_timezone") {
                    TimeTypeWithoutTimezone
                } else {
                    TimeTypeWithTimezone
                }
            "date-time" ->
                if (schema.get("airbyte_type")?.asText() == "timestamp_without_timezone") {
                    TimestampTypeWithoutTimezone
                } else {
                    TimestampTypeWithTimezone
                }
            null -> StringType
            else ->
                throw IllegalArgumentException(
                    "Unknown string format: ${
                        schema.get("format").asText()
                    }"
                )
        }

    private fun fromNumber(schema: ObjectNode): AirbyteType =
        if (schema.get("airbyte_type")?.asText() == "integer") {
            IntegerType
        } else {
            NumberType
        }

    private fun fromArray(schema: ObjectNode): AirbyteType {
        val items = schema.get("items") ?: return ArrayTypeWithoutSchema
        if (items.isArray) {
            if (items.isEmpty) {
                return ArrayTypeWithoutSchema
            }
            val itemOptions = UnionType(items.mapNotNull { convertInner(it) })
            val itemType = optionsToUnionOrSingleType(itemOptions.options)
            return ArrayType(FieldType(itemType, true))
        }
        return ArrayType(fieldFromSchema(items as ObjectNode))
    }

    private fun fromObject(schema: ObjectNode): AirbyteType {
        val properties = schema.get("properties") ?: return ObjectTypeWithoutSchema
        if (properties.isEmpty) {
            return ObjectTypeWithEmptySchema
        }
        val propertiesMapped =
            properties
                .fields()
                .asSequence()
                .map { (name, node) -> name to fieldFromSchema(node as ObjectNode) }
                .toMap(LinkedHashMap())
        return ObjectType(propertiesMapped)
    }

    private fun fieldFromSchema(
        fieldSchema: ObjectNode,
    ): FieldType {
        val airbyteType =
            convertInner(fieldSchema) ?: UnknownType("Illegal null type as field type")
        return FieldType(airbyteType, nullable = true)
    }

    private fun unionFromCombinedTypes(
        options: List<JsonNode>,
        parentSchema: ObjectNode
    ): AirbyteType {
        // Denormalize the properties across each type (the converter only checks what matters
        // per type).
        val unionOptions =
            options.mapNotNull {
                if (it.isTextual) {
                    val schema = parentSchema.deepCopy()
                    schema.put("type", it.textValue())
                    convertInner(schema)
                } else {
                    convertInner(it)
                }
            }
        return optionsToUnionOrSingleType(unionOptions)
    }

    private fun optionsToUnionOrSingleType(options: List<AirbyteType>): AirbyteType =
        if (options.isEmpty()) {
            UnionType(listOf(UnknownType("No valid options in union")))
        } else if (options.size == 1) {
            options.first()
        } else {
            UnionType(options)
        }
}
