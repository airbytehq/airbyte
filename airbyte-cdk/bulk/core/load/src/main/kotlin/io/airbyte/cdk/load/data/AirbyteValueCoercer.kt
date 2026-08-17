/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import com.ethlo.time.ITU
import com.ethlo.time.ParseConfig
import io.airbyte.cdk.load.data.TemporalFormatters.DATE_TIME_FORMATTER
import io.airbyte.cdk.load.data.json.JsonToAirbyteValue
import io.airbyte.cdk.load.util.serializeToString
import jakarta.inject.Singleton
import java.math.BigDecimal
import java.math.BigInteger
import java.text.ParsePosition
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.time.temporal.TemporalQueries

/**
 * Utility class to coerce AirbyteValue to specific types. Does **not** support recursive coercion.
 *
 * More specifically: This class coerces the output of [JsonToAirbyteValue] to strongly-typed
 * [AirbyteValue]. In particular, this class will parse temporal types, and performs some
 * common-sense conversions among numeric types, as well as upcasting any value to StringValue.
 *
 * Timestamp parsing uses ethlo/itu for fast ISO-8601 parsing with a JDK TemporalQueries fallback
 * for exotic formats. Time parsing uses a single parse + TemporalQueries check. Both avoid
 * exception-as-control-flow.
 */
@Singleton
class AirbyteValueCoercer {
    fun coerce(
        value: AirbyteValue,
        type: AirbyteType,
        respectLegacyUnions: Boolean = false
    ): AirbyteValue? {
        // Don't modify nulls.
        if (value == NullValue) {
            return NullValue
        }
        return try {
            when (type) {
                BooleanType -> coerceBoolean(value)
                DateType -> coerceDate(value)
                IntegerType -> coerceInt(value)
                NumberType -> coerceNumber(value)
                StringType -> coerceString(value)
                TimeTypeWithTimezone -> coerceTimeTz(value)
                TimeTypeWithoutTimezone -> coerceTimeNtz(value)
                TimestampTypeWithTimezone -> coerceTimestampTz(value)
                TimestampTypeWithoutTimezone -> coerceTimestampNtz(value)
                is ArrayType,
                ArrayTypeWithoutSchema -> coerceArray(value)
                is ObjectType,
                ObjectTypeWithEmptySchema,
                ObjectTypeWithoutSchema -> coerceObject(value)
                is UnionType -> {
                    if (respectLegacyUnions && type.isLegacyUnion) {
                        // If we care about legacy unions, and this is a legacy union,
                        // do the legacy union thing.
                        coerce(value, type.chooseType(), respectLegacyUnions = true)
                    } else {
                        // Don't touch non-legacy unions, just pass it through
                        value
                    }
                }
                // Similarly, if we don't know what type it's supposed to be,
                // leave it unchanged.
                is UnknownType -> value
            }
        } catch (_: Exception) {
            null
        }
    }

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
                is TimestampWithoutTimezoneValue ->
                    throw IllegalArgumentException(
                        "Invalid value type ${value.javaClass.canonicalName}"
                    )
            }
        return StringValue(stringified)
    }

    fun coerceDate(value: AirbyteValue): DateValue? =
        when (value) {
            is DateValue -> value
            else ->
                requireType<StringValue, DateValue>(value) {
                    DateValue(LocalDate.parse(it.value, TemporalFormatters.DATE_TIME_FORMATTER))
                }
        }

    fun coerceTimeTz(value: AirbyteValue): TimeWithTimezoneValue? =
        when (value) {
            is TimeWithTimezoneValue -> value
            else ->
                requireType<StringValue, TimeWithTimezoneValue>(value) {
                    // Single parse + temporal query to detect timezone, avoiding the old
                    // try-OffsetTime.parse/catch-fallback-to-LocalTime pattern.
                    val parsed = TemporalFormatters.TIME_FORMATTER.parse(it.value)
                    val offset = parsed.query(TemporalQueries.offset())
                    val ot =
                        if (offset != null) {
                            // Has timezone offset (e.g. "12:00:00+01:00") — use it directly
                            OffsetTime.from(parsed)
                        } else {
                            // No timezone (e.g. "12:00:00") — assume UTC
                            LocalTime.from(parsed).atOffset(ZoneOffset.UTC)
                        }
                    TimeWithTimezoneValue(ot)
                }
        }

    fun coerceTimeNtz(value: AirbyteValue): TimeWithoutTimezoneValue? =
        when (value) {
            is TimeWithoutTimezoneValue -> value
            else ->
                requireType<StringValue, TimeWithoutTimezoneValue>(value) {
                    TimeWithoutTimezoneValue(
                        LocalTime.parse(it.value, TemporalFormatters.TIME_FORMATTER)
                    )
                }
        }

    fun coerceTimestampTz(value: AirbyteValue): TimestampWithTimezoneValue? =
        when (value) {
            is TimestampWithTimezoneValue -> value
            else ->
                requireType<StringValue, TimestampWithTimezoneValue>(value) {
                    TimestampWithTimezoneValue(offsetDateTime(it))
                }
        }

    fun coerceTimestampNtz(value: AirbyteValue): TimestampWithoutTimezoneValue? =
        when (value) {
            is TimestampWithoutTimezoneValue -> value
            else ->
                requireType<StringValue, TimestampWithoutTimezoneValue>(value) {
                    TimestampWithoutTimezoneValue(offsetDateTime(it).toLocalDateTime())
                }
        }

    /**
     * Parses a timestamp string into an OffsetDateTime. Uses ethlo/itu for ISO-8601 formats (~25x
     * faster than JDK), with a JDK TemporalQueries fallback for non-ISO formats.
     */
    private fun offsetDateTime(it: StringValue): OffsetDateTime {
        val s = it.value
        if (looksLikeIso8601(s)) {
            // Fast path: ITU handles ISO-8601/RFC-3339 ~25x faster than JDK DateTimeFormatter,
            // and determines with/without timezone via position-based parsing (no exceptions).
            val pos = ParsePosition(0)
            val parsed =
                try {
                    ITU.parseLenient(s, ParseConfig.DEFAULT, pos)
                } catch (_: Exception) {
                    // ITU can throw on some edge cases that pass looksLikeIso8601 (e.g.
                    // "2021-01-01 01:01:01 +0000" has dashes but a space-separated compact offset).
                    null
                }
            // Only use the ITU result if it successfully consumed the entire input string.
            // Partial parses (e.g. ITU parsed the date but stopped at a named timezone like
            // "GMT+08:00") must fall through to the JDK formatter which handles those.
            if (parsed != null && pos.index == s.length) {
                return if (parsed.offset.isPresent) {
                    // Timestamp included timezone info (Z, +05:30, etc.) — use it directly
                    parsed.toOffsetDatetime()
                } else {
                    // No timezone info — assume UTC
                    parsed.toLocalDatetime().atOffset(ZoneOffset.UTC)
                }
            }
        }
        // Non-ISO format (slashes, dots, abbreviated months) or ITU couldn't fully parse
        return offsetDateTimeJdk(s)
    }

    /**
     * JDK fallback for non-ISO formats. Uses a single parse + temporal query to determine whether
     * timezone info is present, avoiding the old try-ZonedDateTime/catch pattern.
     */
    private fun offsetDateTimeJdk(s: String): OffsetDateTime {
        val parsed = DATE_TIME_FORMATTER.parse(s)
        // Check for explicit offset (+05:30, Z) first, then named zone (UTC, PST, GMT+08:00).
        // Named zones like "GMT+08:00" are parsed as a ZoneId, not an offset, so we need both
        // checks.
        val offset = parsed.query(TemporalQueries.offset())
        val zone = parsed.query(TemporalQueries.zone())
        return if (offset != null || zone != null) {
            // Has timezone — construct ZonedDateTime to resolve the zone to an offset
            ZonedDateTime.from(parsed).toOffsetDateTime()
        } else {
            // No timezone — assume UTC
            LocalDateTime.from(parsed).atOffset(ZoneOffset.UTC)
        }
    }

    /**
     * Quick check for ISO-8601-ish format. ITU expects dashes as date separators (e.g.
     * "2024-01-15T..."). Non-ISO formats like "2024/01/15", "2024.01.15", or "2024 Jan 15" are
     * routed directly to the JDK fallback.
     */
    private fun looksLikeIso8601(s: String): Boolean {
        // Minimum: "yyyy-MM-dd" = 10 chars
        return s.length >= 10 && s[4] == '-' && s[7] == '-'
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
}
