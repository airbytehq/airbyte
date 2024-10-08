/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import com.fasterxml.jackson.databind.node.ObjectNode

class JsonSchemaToAirbyteType {
    fun convert(schema: JsonNode): AirbyteType {
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
                    "null" -> NullType
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
                UnknownType("unspported type for 'type' field: $schemaType")
            }
        } else if (schema.isObject) {
            // {"oneOf": [...], ...} or {"anyOf": [...], ...} or {"allOf": [...], ...}
            val options = schema.get("oneOf") ?: schema.get("anyOf") ?: schema.get("allOf")
            return if (options != null) {
                UnionType(options.map { convert(it as ObjectNode) })
            } else {
                // Default to object if no type and not a union type
                convert((schema as ObjectNode).put("type", "object"))
            }
        } else if (schema.isTextual) {
            // "<typename>"
            val typeSchema = JsonNodeFactory.instance.objectNode().put("type", schema.asText())
            return convert(typeSchema)
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
                TimeType(
                    hasTimezone = schema.get("airbyte_type")?.asText() != "time_without_timezone"
                )
            "date-time" ->
                TimestampType(
                    hasTimezone =
                        schema.get("airbyte_type")?.asText() != "timestamp_without_timezone"
                )
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
            val itemOptions = UnionType(items.map { convert(it) })
            return ArrayType(fieldFromUnion(itemOptions))
        }
        return ArrayType(fieldFromSchema(items as ObjectNode))
    }

    private fun fromObject(schema: ObjectNode): AirbyteType {
        val properties = schema.get("properties") ?: return ObjectTypeWithoutSchema
        if (properties.isEmpty) {
            return ObjectTypeWithEmptySchema
        }
        val requiredFields = schema.get("required")?.map { it.asText() } ?: emptyList()
        return objectFromProperties(properties as ObjectNode, requiredFields)
    }

    private fun fieldFromSchema(
        fieldSchema: ObjectNode,
        onRequiredList: Boolean = false
    ): FieldType {
        val markedRequired = fieldSchema.get("required")?.asBoolean() ?: false
        val nullable = !(onRequiredList || markedRequired)
        val airbyteType = convert(fieldSchema)
        if (airbyteType is UnionType) {
            return fieldFromUnion(airbyteType, nullable)
        } else {
            return FieldType(airbyteType, nullable)
        }
    }

    private fun fieldFromUnion(unionType: UnionType, nullable: Boolean = false): FieldType {
        if (unionType.options.contains(NullType)) {
            val filtered = unionType.options.filter { it != NullType }
            return FieldType(UnionType(filtered), nullable = true)
        }
        return FieldType(unionType, nullable = nullable)
    }

    private fun objectFromProperties(schema: ObjectNode, requiredFields: List<String>): ObjectType {
        val properties =
            schema
                .fields()
                .asSequence()
                .map { (name, node) ->
                    name to fieldFromSchema(node as ObjectNode, requiredFields.contains(name))
                }
                .toMap(LinkedHashMap())
        return ObjectType(properties)
    }

    private fun unionFromCombinedTypes(
        options: List<JsonNode>,
        parentSchema: ObjectNode
    ): UnionType {
        // Denormalize the properties across each type (the converter only checks what matters
        // per type).
        val unionOptions =
            options.map {
                if (it.isTextual) {
                    val schema = parentSchema.deepCopy()
                    schema.put("type", it.textValue())
                    convert(schema)
                } else {
                    convert(it)
                }
            }
        return UnionType(unionOptions)
    }
}
