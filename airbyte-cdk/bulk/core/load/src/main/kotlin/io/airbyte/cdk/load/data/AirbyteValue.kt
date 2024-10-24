/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import java.math.BigDecimal
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneOffset

sealed interface AirbyteValue {
    companion object {
        fun from(value: Any?): AirbyteValue =
            when (value) {
                null -> NullValue
                is String -> StringValue(value)
                is Boolean -> BooleanValue(value)
                is Int -> IntegerValue(value.toLong())
                is Long -> IntegerValue(value)
                is Double -> NumberValue(BigDecimal.valueOf(value))
                is BigDecimal -> NumberValue(value)
                is LocalDate -> DateValue(value.toString())
                is OffsetDateTime,
                is LocalDateTime -> TimestampValue(value.toString())
                is OffsetTime,
                is LocalTime -> TimeValue(value.toString())
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
value class IntegerValue(val value: Long) : AirbyteValue, Comparable<IntegerValue> {
    override fun compareTo(other: IntegerValue): Int = value.compareTo(other.value)
}

@JvmInline
value class NumberValue(val value: BigDecimal) : AirbyteValue, Comparable<NumberValue> {
    override fun compareTo(other: NumberValue): Int = value.compareTo(other.value)
}

@JvmInline
value class DateValue(val value: String) : AirbyteValue, Comparable<DateValue> {
    override fun compareTo(other: DateValue): Int {
        val thisDate =
            try {
                LocalDate.parse(value)
            } catch (e: Exception) {
                LocalDate.MIN
            }
        val otherDate =
            try {
                LocalDate.parse(other.value)
            } catch (e: Exception) {
                LocalDate.MIN
            }
        return thisDate.compareTo(otherDate)
    }
}

@JvmInline
value class TimestampValue(val value: String) : AirbyteValue, Comparable<TimestampValue> {
    override fun compareTo(other: TimestampValue): Int {
        // Do all comparisons using OffsetDateTime for convenience.
        // First, try directly parsing as OffsetDateTime.
        // If that fails, try parsing as LocalDateTime and assume UTC.
        // We could maybe have separate value classes for these cases,
        // but that comes with its own set of problems
        // (mostly around sources declaring bad schemas).
        val thisTimestamp =
            try {
                OffsetDateTime.parse(value)
            } catch (e: Exception) {
                LocalDateTime.parse(value).atOffset(ZoneOffset.UTC)
            } catch (e: Exception) {
                LocalDateTime.MIN.atOffset(ZoneOffset.UTC)
            }
        val otherTimestamp =
            try {
                OffsetDateTime.parse(other.value)
            } catch (e: Exception) {
                LocalDateTime.parse(other.value).atOffset(ZoneOffset.UTC)
            } catch (e: Exception) {
                LocalDateTime.MIN.atOffset(ZoneOffset.UTC)
            }
        return thisTimestamp.compareTo(otherTimestamp)
    }
}

@JvmInline
value class TimeValue(val value: String) : AirbyteValue, Comparable<TimeValue> {
    override fun compareTo(other: TimeValue): Int {
        // Similar to TimestampValue, try parsing with/without timezone,
        // and do all comparisons using OffsetTime.
        val thisTime =
            try {
                OffsetTime.parse(value)
            } catch (e: Exception) {
                LocalTime.parse(value).atOffset(ZoneOffset.UTC)
            } catch (e: Exception) {
                LocalTime.MIN.atOffset(ZoneOffset.UTC)
            }
        val otherTime =
            try {
                OffsetTime.parse(other.value)
            } catch (e: Exception) {
                LocalTime.parse(other.value).atOffset(ZoneOffset.UTC)
            } catch (e: Exception) {
                LocalTime.MIN.atOffset(ZoneOffset.UTC)
            }
        return thisTime.compareTo(otherTime)
    }
}

@JvmInline
value class ArrayValue(val values: List<AirbyteValue>) : AirbyteValue {
    companion object {
        fun from(list: List<Any?>): ArrayValue = ArrayValue(list.map { it as AirbyteValue })
    }
}

@JvmInline
value class ObjectValue(val values: LinkedHashMap<String, AirbyteValue>) : AirbyteValue {
    companion object {
        fun from(map: Map<String, Any?>): ObjectValue =
            ObjectValue(map.mapValuesTo(linkedMapOf()) { (_, v) -> AirbyteValue.from(v) })
    }
}

@JvmInline value class UnknownValue(val what: String) : AirbyteValue
