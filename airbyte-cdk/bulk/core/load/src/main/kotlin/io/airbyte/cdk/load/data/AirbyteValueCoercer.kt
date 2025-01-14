/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.data.json.JsonToAirbyteValue
import io.airbyte.cdk.load.util.serializeToString
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter

/**
 * Utility class to coerce AirbyteValue to specific types. Does **not** support recursive coercion.
 *
 * More specifically: This class coerces the output of [JsonToAirbyteValue] to strongly-typed
 * [AirbyteValue]. In particular, this class will parse temporal types, and performs some
 * common-sense conversions among numeric types, as well as upcasting any value to StringValue.
 */
object AirbyteValueCoercer {
    fun coerceBoolean(value: AirbyteValue): BooleanValue? = requireType<BooleanValue>(value)

    fun coerceInt(value: AirbyteValue): IntegerValue? =
        when (value) {
            // Maybe we should truncate non-int values?
            // But to match existing behavior, let's just null for now.
            is NumberValue -> IntegerValue(value.value.toBigIntegerExact())
            is IntegerValue -> value
            is StringValue -> IntegerValue(BigInteger(value.value))
            else -> null
        }

    fun coerceNumber(value: AirbyteValue): NumberValue? =
        when (value) {
            is NumberValue -> value
            is IntegerValue -> NumberValue(value.value.toBigDecimal())
            is StringValue -> NumberValue(BigDecimal(value.value))
            else -> null
        }

    fun coerceString(value: AirbyteValue): StringValue {
        val stringified =
            when (value) {
                // this should never happen, because we handle `value is NullValue`
                // in the top-level if statement
                NullValue -> throw IllegalStateException("Unexpected NullValue")
                is StringValue -> value.value
                is NumberValue -> value.value.toString()
                is IntegerValue -> value.value.toString()
                is BooleanValue -> value.value.toString()
                is ArrayValue,
                is ObjectValue -> value.serializeToString()
                // JsonToAirbyteValue never outputs these values, so don't handle them.
                is DateValue,
                is TimeWithTimezoneValue,
                is TimeWithoutTimezoneValue,
                is TimestampWithTimezoneValue,
                is TimestampWithoutTimezoneValue,
                is UnknownValue ->
                    throw IllegalArgumentException(
                        "Invalid value type ${value.javaClass.canonicalName}"
                    )
            }
        return StringValue(stringified)
    }

    fun coerceDate(value: AirbyteValue): DateValue? =
        requireType<StringValue, DateValue>(value) {
            DateValue(LocalDate.parse(it.value, DATE_TIME_FORMATTER))
        }

    fun coerceTimeTz(value: AirbyteValue): TimeWithTimezoneValue? =
        requireType<StringValue, TimeWithTimezoneValue>(value) {
            val ot =
                try {
                    OffsetTime.parse(it.value, TIME_FORMATTER)
                } catch (e: Exception) {
                    LocalTime.parse(it.value, TIME_FORMATTER).atOffset(ZoneOffset.UTC)
                }
            TimeWithTimezoneValue(ot)
        }

    fun coerceTimeNtz(value: AirbyteValue): TimeWithoutTimezoneValue? =
        requireType<StringValue, TimeWithoutTimezoneValue>(value) {
            TimeWithoutTimezoneValue(LocalTime.parse(it.value, TIME_FORMATTER))
        }

    fun coerceTimestampTz(value: AirbyteValue): TimestampWithTimezoneValue? =
        requireType<StringValue, TimestampWithTimezoneValue>(value) {
            TimestampWithTimezoneValue(offsetDateTime(it))
        }

    fun coerceTimestampNtz(value: AirbyteValue): TimestampWithoutTimezoneValue? =
        requireType<StringValue, TimestampWithoutTimezoneValue>(value) {
            TimestampWithoutTimezoneValue(offsetDateTime(it).toLocalDateTime())
        }

    private fun offsetDateTime(it: StringValue): OffsetDateTime {
        val odt =
            try {
                ZonedDateTime.parse(it.value, AirbyteValueDeepCoercingMapper.DATE_TIME_FORMATTER)
                    .toOffsetDateTime()
            } catch (e: Exception) {
                LocalDateTime.parse(it.value, AirbyteValueDeepCoercingMapper.DATE_TIME_FORMATTER)
                    .atOffset(ZoneOffset.UTC)
            }
        return odt
    }

    // In theory, we could e.g. Jsons.readTree((value as StringValue).value).
    // But for now, just require that the source emits an actual ObjectNode.
    fun coerceObject(value: AirbyteValue): ObjectValue? = requireType<ObjectValue>(value)

    fun coerceArray(value: AirbyteValue): ArrayValue? = requireType<ArrayValue>(value)

    private inline fun <reified T : AirbyteValue> requireType(
        value: AirbyteValue,
    ): T? = requireType<T, T>(value) { it }

    private inline fun <reified InputType : AirbyteValue, OutputType : AirbyteValue> requireType(
        value: AirbyteValue,
        convertToOutputType: (InputType) -> OutputType,
    ): OutputType? {
        return if (value is InputType) {
            convertToOutputType(value)
        } else {
            null
        }
    }

    val DATE_TIME_FORMATTER: DateTimeFormatter =
        DateTimeFormatter.ofPattern(
            "[yyyy][yy]['-']['/']['.'][' '][MMM][MM][M]['-']['/']['.'][' '][dd][d][[' '][G]][[' ']['T']HH:mm[':'ss[.][SSSSSS][SSSSS][SSSS][SSS][' '][z][zzz][Z][O][x][XXX][XX][X][[' '][G]]]]"
        )
    val TIME_FORMATTER: DateTimeFormatter =
        DateTimeFormatter.ofPattern(
            "HH:mm[':'ss[.][SSSSSS][SSSSS][SSSS][SSS][' '][z][zzz][Z][O][x][XXX][XX][X]]"
        )
}
