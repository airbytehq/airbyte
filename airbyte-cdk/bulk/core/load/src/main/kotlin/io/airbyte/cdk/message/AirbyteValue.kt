package io.airbyte.cdk.message

import com.fasterxml.jackson.databind.JsonNode

sealed class AirbyteValue {
    companion object {
        fun fromAirbyteJson(json: JsonNode, schema: ObjectType): ObjectValue {
            val data = fromJson(json, schema)
            if (data !is ObjectValue) {
                throw IllegalArgumentException("Top-level data must be an object (got $data)")
            }
            return data
        }

        // Schema-aware mapping from json to airbyte values
        fun fromJson(json: JsonNode, schema: AirbyteType): AirbyteValue {
            return when (schema) {
                is ArrayType,
                is ArrayTypeWithoutSchema -> ArrayValue(
                    json.map { fromJson(it, (schema as ArrayType).items) }
                )

                is BooleanType -> BooleanValue(json.asBoolean())
                is DateType -> DateValue(json.asText())
                is FieldType -> fromJson(json, schema.type)
                is IntegerType -> IntegerValue(json.asLong())
                is NullType -> NullValue
                is NumberType -> NumberValue(json.asDouble())
                is ObjectType -> ObjectValue(
                    values = schema.properties.mapValues { (name, field) ->
                        fromJson(json.get(name), field.type)
                    }.toMap(LinkedHashMap())
                )
                is ObjectTypeWithoutSchema -> ObjectValue(
                    values = json.fields().asSequence().map { (name, value) ->
                        name to fromAny(value)
                    }.toMap(LinkedHashMap()))
                is StringType -> StringValue(json.asText())
                is TimeType -> TimeValue(json.asText())
                is TimestampType -> TimestampValue(json.asText())
                is UnionType -> {
                    val option = schema.options.find {
                        try {
                            fromJson(json, it)
                            true
                        } catch (e: IllegalArgumentException) {
                            false
                        }
                    } ?: throw IllegalArgumentException("No matching union option")
                    fromJson(json, option)
                }
            }
        }

        fun fromAny(value: Any?): AirbyteValue {
            return when (value) {
                is String -> StringValue(value)
                is Boolean -> BooleanValue(value)
                is Int -> IntegerValue(value.toLong())
                is Long -> IntegerValue(value)
                is Float -> NumberValue(value.toDouble())
                is Double -> NumberValue(value)
                is Map<*, *> -> ObjectValue(
                    value.map { (key, value) ->
                        key as String to fromAny(value)
                    }.toMap(LinkedHashMap())
                )
                is List<*> -> ArrayValue(
                    value.map { fromAny(it!!) }
                )
                null -> NullValue
                else -> throw IllegalArgumentException("Unsupported value type: ${value::class}")
            }
        }
    }
}
data object NullValue: AirbyteValue()
data class StringValue(val value: String): AirbyteValue()
data class BooleanValue(val value: Boolean): AirbyteValue()
data class IntegerValue(val value: Long): AirbyteValue()
data class NumberValue(val value: Double): AirbyteValue()
data class DateValue(val value: String): AirbyteValue()
data class TimestampValue(val value: String): AirbyteValue()
data class TimeValue(val value: String): AirbyteValue()
data class ArrayValue(val values: List<AirbyteValue>): AirbyteValue()
data class ObjectValue(val values: LinkedHashMap<String, AirbyteValue>): AirbyteValue() {
    constructor(vararg values: Pair<String, AirbyteValue>): this(
        values = values.toMap(LinkedHashMap())
    )
}
