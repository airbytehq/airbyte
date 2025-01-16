/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import com.fasterxml.jackson.annotation.JsonValue
import com.fasterxml.jackson.core.JsonGenerator
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.JsonSerializer
import com.fasterxml.jackson.databind.SerializerProvider
import com.fasterxml.jackson.databind.annotation.JsonSerialize
import com.fasterxml.jackson.databind.node.NullNode
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime

sealed interface AirbyteValue {
    companion object {
        fun from(value: Any?): AirbyteValue =
            when (value) {
                is AirbyteValue -> value
                null -> NullValue
                is String -> StringValue(value)
                is Boolean -> BooleanValue(value)
                is Int -> IntegerValue(value.toLong())
                is Long -> IntegerValue(value)
                is BigInteger -> IntegerValue(value)
                is Double -> NumberValue(BigDecimal.valueOf(value))
                is BigDecimal -> NumberValue(value)
                is LocalDate -> DateValue(value)
                is OffsetDateTime -> TimestampWithTimezoneValue(value)
                is LocalDateTime -> TimestampWithoutTimezoneValue(value)
                is OffsetTime -> TimeWithTimezoneValue(value)
                is LocalTime -> TimeWithoutTimezoneValue(value)
                is Map<*, *> ->
                    ObjectValue.from(@Suppress("UNCHECKED_CAST") (value as Map<String, Any?>))
                is List<*> -> ArrayValue.from(value)
                else ->
                    throw IllegalArgumentException(
                        "Unrecognized value (${value.javaClass.name}: $value"
                    )
            }
    }
}

// Comparable implementations are intended for use in tests.
// They're not particularly robust, and probably shouldn't be relied on
// for actual sync-time logic.
// (mostly the date/timestamp/time types - everything else is fine)
data object NullValue : AirbyteValue, Comparable<NullValue> {
    override fun compareTo(other: NullValue): Int = 0

    // make sure that we serialize this as a NullNode, rather than an empty object.
    // We can't just return `null`, because jackson treats that as an error
    // and falls back to its normal serialization behavior.
    @JsonValue fun toJson(): NullNode = NullNode.instance
}

@JvmInline
value class StringValue(val value: String) : AirbyteValue, Comparable<StringValue> {
    override fun compareTo(other: StringValue): Int = value.compareTo(other.value)
}

@JvmInline
value class BooleanValue(val value: Boolean) : AirbyteValue, Comparable<BooleanValue> {
    override fun compareTo(other: BooleanValue): Int = value.compareTo(other.value)
}

@JvmInline
value class IntegerValue(val value: BigInteger) : AirbyteValue, Comparable<IntegerValue> {
    constructor(value: Long) : this(BigInteger.valueOf(value))
    override fun compareTo(other: IntegerValue): Int = value.compareTo(other.value)
}

@JvmInline
value class NumberValue(val value: BigDecimal) : AirbyteValue, Comparable<NumberValue> {
    override fun compareTo(other: NumberValue): Int = value.compareTo(other.value)
}

@JvmInline
value class DateValue(val value: LocalDate) : AirbyteValue, Comparable<DateValue> {
    constructor(date: String) : this(LocalDate.parse(date))
    override fun compareTo(other: DateValue): Int = value.compareTo(other.value)
    @JsonValue fun toJson() = value.toString()
}

@JvmInline
value class TimestampWithTimezoneValue(val value: OffsetDateTime) :
    AirbyteValue, Comparable<TimestampWithTimezoneValue> {
    constructor(timestamp: String) : this(OffsetDateTime.parse(timestamp))
    override fun compareTo(other: TimestampWithTimezoneValue): Int = value.compareTo(other.value)
    @JsonValue fun toJson() = value.toString()
}

@JvmInline
value class TimestampWithoutTimezoneValue(val value: LocalDateTime) :
    AirbyteValue, Comparable<TimestampWithoutTimezoneValue> {
    constructor(timestamp: String) : this(LocalDateTime.parse(timestamp))
    override fun compareTo(other: TimestampWithoutTimezoneValue): Int = value.compareTo(other.value)
    @JsonValue fun toJson() = value.toString()
}

@JvmInline
value class TimeWithTimezoneValue(val value: OffsetTime) :
    AirbyteValue, Comparable<TimeWithTimezoneValue> {
    constructor(time: String) : this(OffsetTime.parse(time))
    override fun compareTo(other: TimeWithTimezoneValue): Int = value.compareTo(other.value)
    @JsonValue fun toJson() = value.toString()
}

@JvmInline
value class TimeWithoutTimezoneValue(val value: LocalTime) :
    AirbyteValue, Comparable<TimeWithoutTimezoneValue> {
    constructor(time: String) : this(LocalTime.parse(time))
    override fun compareTo(other: TimeWithoutTimezoneValue): Int = value.compareTo(other.value)
    @JsonValue fun toJson() = value.toString()
}

@JvmInline
value class ArrayValue(val values: List<AirbyteValue>) : AirbyteValue {
    companion object {
        fun from(list: List<Any?>): ArrayValue = ArrayValue(list.map { AirbyteValue.from(it) })
    }
}

// jackson can't figure out how to serialize this class,
// so write a custom serializer that just serializes the map directly.
// For some reason, the more obvious `@JsonValue fun toJson() = values`
// doesn't work either.
@JsonSerialize(using = ObjectValueSerializer::class)
@JvmInline
value class ObjectValue(val values: LinkedHashMap<String, AirbyteValue>) : AirbyteValue {
    @JsonValue fun toJson() = values
    companion object {
        fun from(map: Map<String, Any?>): ObjectValue =
            ObjectValue(map.mapValuesTo(linkedMapOf()) { (_, v) -> AirbyteValue.from(v) })
    }
}

private class ObjectValueSerializer : JsonSerializer<ObjectValue>() {
    override fun serialize(
        value: ObjectValue,
        gen: JsonGenerator,
        serializers: SerializerProvider,
    ) {
        gen.writePOJO(value.values)
    }
}

@JvmInline value class UnknownValue(val value: JsonNode) : AirbyteValue
