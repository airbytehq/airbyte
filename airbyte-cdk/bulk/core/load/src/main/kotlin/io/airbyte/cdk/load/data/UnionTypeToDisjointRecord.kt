/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

class UnionTypeToDisjointRecord : AirbyteSchemaIdentityMapper {
    override fun mapUnion(schema: UnionType): AirbyteType {
        if (schema.options.size < 2) {
            return schema
        }
        /* Create a schema of { "type": "string", "<typename(option1)>": <type(option1)>, etc... } */
        val properties = linkedMapOf("type" to FieldType(StringType, nullable = false))
        schema.options.forEach { unmappedType ->
            /* Necessary because the type might contain a nested union that needs mapping to a disjoint record. */
            val mappedType = map(unmappedType)
            val name = typeName(mappedType)
            if (name in properties) {
                throw IllegalArgumentException("Union of types with same name: $name")
            }
            properties[typeName(mappedType)] = FieldType(mappedType, nullable = true)
        }
        return ObjectType(properties)
    }

    companion object {
        fun typeName(type: AirbyteType): String =
            when (type) {
                is StringType -> "string"
                is BooleanType -> "boolean"
                is IntegerType -> "integer"
                is NumberType -> "number"
                is DateType -> "date"
                is TimestampTypeWithTimezone -> "timestamp_with_timezone"
                is TimestampTypeWithoutTimezone -> "timestamp_without_timezone"
                is TimeTypeWithTimezone -> "time_with_timezone"
                is TimeTypeWithoutTimezone -> "time_without_timezone"
                is ArrayType -> "array"
                is ObjectType -> "object"
                is ArrayTypeWithoutSchema,
                is ObjectTypeWithoutSchema,
                is ObjectTypeWithEmptySchema -> "object"
                is UnionType -> "union"
                is UnknownType -> "unknown"
            }
    }
}

class UnionValueToDisjointRecord : AirbyteValueIdentityMapper() {
    override fun mapUnion(
        value: AirbyteValue,
        schema: UnionType,
        context: Context
    ): Pair<AirbyteValue, Context> {
        val type =
            schema.options.find { matches(it, value) }
                ?: throw IllegalArgumentException("No matching union option in $schema for $value")
        val (valueMapped, contextMapped) = mapInner(value, type, context)
        return ObjectValue(
            values =
                linkedMapOf(
                    "type" to StringValue(UnionTypeToDisjointRecord.typeName(type)),
                    UnionTypeToDisjointRecord.typeName(type) to valueMapped
                )
        ) to contextMapped
    }

    private fun matches(schema: AirbyteType, value: AirbyteValue): Boolean {
        return when (schema) {
            is StringType -> value is StringValue
            is BooleanType -> value is BooleanValue
            is IntegerType -> value is IntegerValue
            is NumberType -> value is NumberValue
            is ArrayType -> value is ArrayValue
            is ObjectType -> value is ObjectValue
            is ArrayTypeWithoutSchema,
            is ObjectTypeWithoutSchema,
            is ObjectTypeWithEmptySchema -> value is StringValue
            is DateType,
            is TimeTypeWithTimezone,
            is TimeTypeWithoutTimezone,
            is TimestampTypeWithTimezone,
            is TimestampTypeWithoutTimezone -> value is IntegerValue
            is UnionType -> schema.options.any { matches(it, value) }
            is UnknownType -> false
        }
    }
}
