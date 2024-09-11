package io.airbyte.cdk.message

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode

sealed class AirbyteType {
    companion object {
        fun fromAirbyteJsonSchema(jsonSchema: ObjectNode): ObjectType {
            val airbyteSchema = fromJsonSchema(jsonSchema)
            if (airbyteSchema !is ObjectType) {
                throw IllegalArgumentException("Top-level schema must be an object (got $airbyteSchema)")
            }
            return airbyteSchema
        }

        fun fromJsonSchema(schema: ObjectNode): AirbyteType {
            if (schema.has("type")) {
                val schemaType = schema.get("type")
                if (schemaType.isTextual) {
                    return when (schema.get("type").asText()) {
                        "string" -> StringType.fromJsonSchema(schema)
                        "boolean" -> BooleanType
                        "integer" -> IntegerType
                        "number" -> NumberType.fromJsonSchema(schema)
                        "array" -> ArrayType.fromJsonSchema(schema)
                        "object" -> ObjectType.fromJsonSchema(schema)
                        "null" -> NullType
                        else -> throw IllegalArgumentException(
                            "Unknown type: ${
                                schema.get("type").asText()
                            }"
                        )
                    }
                } else if (schemaType.isArray) {
                    return UnionType.fromJsonSchemaTypeArray(schemaType as ArrayNode, schema)
                }
            } else {
                val options = schema.get("oneOf") ?: schema.get("anyOf") ?: schema.get("allOf")
                if (options != null) {
                    return UnionType.fromUnionOptions(
                        options.map { fromJsonSchema(it as ObjectNode) }
                    )
                }
            }

            throw IllegalArgumentException("Unknown schema type: $schema")
        }
    }
}

data object NullType: AirbyteType()
data object StringType: AirbyteType() {
    fun fromJsonSchema(schema: ObjectNode): AirbyteType =
        when (schema.get("format")?.asText()) {
            "date" -> DateType
            "time" -> TimeType(
                hasTimezone = schema.get("airbyte_type")?.asText() != "time_without_timezone"
            )

            "date-time" -> TimestampType(
                hasTimezone = schema.get("airbyte_type")
                    ?.asText() != "timestamp_without_timezone"
            )

            null -> StringType
            else -> throw IllegalArgumentException(
                "Unknown string format: ${
                    schema.get("format").asText()
                }"
            )
        }
}
data object BooleanType: AirbyteType()
data object IntegerType: AirbyteType()
data object NumberType: AirbyteType() {
    fun fromJsonSchema(schema: ObjectNode): AirbyteType =
        if (schema.get("airbyte_type")?.asText() == "integer") {
            IntegerType
        } else {
            NumberType
        }
}
data object DateType: AirbyteType()
data class TimestampType(val hasTimezone: Boolean): AirbyteType()
data class TimeType(val hasTimezone: Boolean): AirbyteType()
data class ArrayType(val items: AirbyteType): AirbyteType() {
    constructor(itemsSchema: ObjectNode): this(
        items = fromJsonSchema(itemsSchema)
    )

    companion object {
        fun fromJsonSchema(schema: ObjectNode): AirbyteType {
            val items = schema.get("items") ?: return ArrayTypeWithoutSchema
            if (items.isArray) {
                if (items.isEmpty) {
                    return ArrayTypeWithoutSchema
                }
                val itemOptions = UnionType.fromUnionOptions(
                    items.map { fromJsonSchema(it as ObjectNode) }
                )
                return ArrayType(itemOptions)
            }
            return ArrayType(items as ObjectNode)
        }
    }
}
data object ArrayTypeWithoutSchema: AirbyteType()
data class ObjectType(val properties: LinkedHashMap<String, FieldType>): AirbyteType() {
    constructor(jsonSchema: ObjectNode): this(
        properties = jsonSchema.fields().asSequence().map { (name, node) ->
            name to FieldType(node as ObjectNode)
        }.toMap(LinkedHashMap())
    )

    companion object {
        fun fromJsonSchema(schema: ObjectNode): AirbyteType {
            val properties = schema.get("properties") ?: return ObjectTypeWithoutSchema
            return ObjectType(properties as ObjectNode)
        }
    }
}
data object ObjectTypeWithoutSchema: AirbyteType()
data class UnionType(val options: List<AirbyteType>): AirbyteType() {
    companion object {
        fun fromJsonSchemaTypeArray(options: ArrayNode, parentSchema: ObjectNode): FieldType {
            val unionOptions = options.map {
                val type = it.textValue()
                val schema = parentSchema.deepCopy()
                schema.put("type", type)
                fromJsonSchema(schema)
            }
            return fromUnionOptions(unionOptions)
        }

        fun fromUnionOptions(options: List<AirbyteType>): FieldType {
            if (options.size == 1) {
                return FieldType(options.first(), nullable = false)
            } else if (options.contains(NullType)) {
                val field = fromUnionOptions(options.filter { it != NullType })
                return FieldType(field.type, nullable = true)
            } else {
                // TODO: Merge object schemas
                return FieldType(UnionType(options), nullable = false)
            }
        }
    }
}

data class FieldType(val type: AirbyteType, val nullable: Boolean): AirbyteType() {
    constructor(jsonSchema: ObjectNode): this(
        type = fromJsonSchema(jsonSchema),
        nullable = !(jsonSchema.get("required")?.asBoolean() ?: false)
    )
}


