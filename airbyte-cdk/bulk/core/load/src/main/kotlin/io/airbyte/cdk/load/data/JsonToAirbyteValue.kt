/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import com.fasterxml.jackson.databind.JsonNode
import java.math.BigDecimal

/**
 * Converts from json to airbyte value, performing the minimum validation necessary to marshal to a
 * native type. For example, we enforce that an integer is either integral or something that can be
 * reasonably converted to an integer, but we do not parse dates or timestamps, which can be
 * reasonably left as strings.
 *
 * TODO: In the future, should we be more or less aggressive here? Which keeps parity with existing
 * behavior? Which existing behavior should be preserved?
 */
class JsonToAirbyteValue {
    fun convert(json: JsonNode, schema: AirbyteType): AirbyteValue {
        try {
            return when (schema) {
                is ArrayType -> toArray(json, schema.items.type)
                is ArrayTypeWithoutSchema -> toArrayWithoutSchema(json)
                is BooleanType -> toBoolean(json)
                is DateType -> DateValue(json.asText())
                is IntegerType -> toInteger(json)
                is NullType -> toNull(json)
                is NumberType -> toNumber(json)
                is ObjectType -> toObject(json, schema)
                is ObjectTypeWithoutSchema,
                is ObjectTypeWithEmptySchema -> toObjectWithoutSchema(json)
                is StringType -> StringValue(json.asText())
                is TimeType -> TimeValue(json.asText())
                is TimestampType -> TimestampValue(json.asText())
                is UnionType -> toUnion(json, schema.options)
                is UnknownType -> UnknownValue("From $schema: $json")
            }
        } catch (t: Throwable) {
            return UnknownValue(t.message ?: "Unknown error")
        }
    }

    private fun toArray(json: JsonNode, schema: AirbyteType): ArrayValue {
        if (!json.isArray) {
            throw IllegalArgumentException("Could not convert $json to Array")
        }

        return ArrayValue(json.map { convert(it, schema) })
    }

    private fun toArrayWithoutSchema(json: JsonNode): ArrayValue {
        if (!json.isArray) {
            throw IllegalArgumentException("Could not convert $json to Array")
        }

        return ArrayValue(json.map { fromJson(it) })
    }

    private fun toBoolean(json: JsonNode): BooleanValue {
        val boolVal =
            when {
                json.isBoolean -> json.asBoolean()
                json.isIntegralNumber -> json.asLong() != 0L
                json.isFloatingPointNumber -> json.asDouble() != 0.0
                json.isTextual -> json.asText().toBooleanStrict()
                else -> throw IllegalArgumentException("Could not convert $json to Boolean")
            }
        return BooleanValue(boolVal)
    }

    private fun toInteger(json: JsonNode): IntegerValue {
        val longVal =
            when {
                json.isBoolean -> if (json.asBoolean()) 1L else 0L
                json.isIntegralNumber -> json.asLong()
                json.isFloatingPointNumber -> json.asDouble().toLong()
                json.isTextual -> json.asText().toLong()
                else -> throw IllegalArgumentException("Could not convert $json to Integer")
            }
        return IntegerValue(longVal)
    }

    private fun toNumber(json: JsonNode): NumberValue {
        val numVal =
            when {
                json.isBoolean -> BigDecimal(if (json.asBoolean()) 1.0 else 0.0)
                json.isIntegralNumber -> json.asLong().toBigDecimal()
                json.isFloatingPointNumber -> json.asDouble().toBigDecimal()
                json.isTextual -> json.asText().toBigDecimal()
                else -> throw IllegalArgumentException("Could not convert $json to Number")
            }
        return NumberValue(numVal)
    }

    private fun toObject(json: JsonNode, schema: ObjectType): ObjectValue {
        if (!json.isObject) {
            throw IllegalArgumentException("Could not convert $json to Object")
        }

        return ObjectValue(
            values =
                schema.properties
                    .mapValues { (name, field) -> convert(json.get(name), field.type) }
                    .toMap(LinkedHashMap())
        )
    }

    private fun toObjectWithoutSchema(json: JsonNode): ObjectValue {
        if (!json.isObject) {
            throw IllegalArgumentException("Could not convert $json to Object")
        }

        return ObjectValue(
            values =
                json
                    .fields()
                    .asSequence()
                    .map { (name, value) -> name to fromJson(value) }
                    .toMap(LinkedHashMap())
        )
    }

    private fun toNull(json: JsonNode): NullValue {
        if (!json.isNull) {
            throw IllegalArgumentException("Null types must be null (not $json)")
        }

        return NullValue
    }

    private fun toUnion(json: JsonNode, options: List<AirbyteType>): AirbyteValue {
        val option =
            options.find { matchesStrictly(it, json) }
                ?: options.find { matchesPermissively(it, json) }
                    ?: throw IllegalArgumentException(
                    "No matching union option in $options for $json"
                )
        return convert(json, option)
    }

    private fun fromJson(json: JsonNode): AirbyteValue {
        return when {
            json.isBoolean -> toBoolean(json)
            json.isIntegralNumber -> toInteger(json)
            json.isFloatingPointNumber -> toNumber(json)
            json.isTextual -> StringValue(json.asText())
            json.isArray -> ArrayValue(json.map { fromJson(it) })
            json.isObject ->
                ObjectValue(
                    json
                        .fields()
                        .asSequence()
                        .map { (name, value) -> name to fromJson(value) }
                        .toMap(LinkedHashMap())
                )
            json.isNull -> NullValue
            else -> UnknownValue("From unrecognized json: $json")
        }
    }

    private fun matchesStrictly(schema: AirbyteType, json: JsonNode): Boolean {
        return when (schema) {
            is ArrayType,
            is ArrayTypeWithoutSchema -> json.isArray
            is BooleanType -> json.isBoolean
            is DateType -> json.isTextual
            is IntegerType -> json.isIntegralNumber
            is NullType -> json.isNull
            is NumberType -> json.isNumber
            is ObjectType,
            is ObjectTypeWithoutSchema,
            is ObjectTypeWithEmptySchema -> json.isObject
            is StringType -> json.isTextual
            is TimeType -> json.isTextual
            is TimestampType -> json.isTextual
            is UnionType -> schema.options.any { matchesStrictly(it, json) }
            is UnknownType -> false
        }
    }

    private fun matchesPermissively(schema: AirbyteType, json: JsonNode): Boolean {
        return try {
            convert(json, schema) !is UnknownValue
        } catch (t: Throwable) {
            false
        }
    }
}

fun JsonNode.toAirbyteValue(schema: AirbyteType): AirbyteValue {
    return JsonToAirbyteValue().convert(this, schema)
}
