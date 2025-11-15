/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.protocol

import com.google.protobuf.ByteString
import com.google.protobuf.NullValue
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import java.math.BigDecimal
import java.math.BigInteger
import java.nio.ByteBuffer
import java.nio.charset.StandardCharsets
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneOffset
import java.util.Base64

/**
 * Type-based encoder for protobuf values. Sources use this to encode values based on the
 * AirbyteSchemaType from field discovery.
 *
 * You can provide an existing [AirbyteValueProtobuf.Builder] to avoid repeated allocations. When
 * provided, the builder is cleared before use.
 */
class AirbyteValueProtobufEncoder {

    /**
     * Encodes a value into protobuf format based on its AirbyteSchemaType. Returns a protobuf
     * representing a null value if [value] is null.
     *
     * @param builder Optional builder to reuse. If provided, it will be cleared at the start.
     */
    fun encode(
        value: Any?,
        airbyteSchemaType: AirbyteSchemaType,
        builder: AirbyteValueProtobuf.Builder? = null
    ): AirbyteValueProtobuf.Builder {
        val b = (builder ?: AirbyteValueProtobuf.newBuilder()).clear()

        if (value == null) {
            return buildNull(b)
        }

        return when (airbyteSchemaType) {
            LeafAirbyteSchemaType.BOOLEAN -> encodeBoolean(value, b)
            LeafAirbyteSchemaType.STRING -> encodeString(value, b)
            LeafAirbyteSchemaType.INTEGER -> encodeInteger(value, b)
            LeafAirbyteSchemaType.NUMBER -> encodeNumber(value, b)
            LeafAirbyteSchemaType.DATE -> encodeDate(value, b)
            LeafAirbyteSchemaType.TIME_WITH_TIMEZONE -> encodeTimeWithTimezone(value, b)
            LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE -> encodeTimeWithoutTimezone(value, b)
            LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE -> encodeTimestampWithTimezone(value, b)
            LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE ->
                encodeTimestampWithoutTimezone(value, b)
            LeafAirbyteSchemaType.NULL -> buildNull(b)
            LeafAirbyteSchemaType.JSONB -> encodeJson(value, b)
            LeafAirbyteSchemaType.BINARY -> encodeBinary(value, b)
            is ArrayAirbyteSchemaType -> encodeJson(value, b)
        }
    }

    private fun buildNull(b: AirbyteValueProtobuf.Builder): AirbyteValueProtobuf.Builder {
        return b.setNull(NullValue.NULL_VALUE)
    }

    private fun encodeBoolean(
        value: Any,
        b: AirbyteValueProtobuf.Builder
    ): AirbyteValueProtobuf.Builder {
        require(value is Boolean) { "Expected Boolean, got ${value::class.simpleName}" }
        return b.setBoolean(value)
    }

    private fun encodeString(
        value: Any,
        b: AirbyteValueProtobuf.Builder
    ): AirbyteValueProtobuf.Builder {
        require(value is String) { "Expected String, got ${value::class.simpleName}" }
        return b.setString(value)
    }

    private fun encodeInteger(
        value: Any,
        b: AirbyteValueProtobuf.Builder
    ): AirbyteValueProtobuf.Builder {
        return when (value) {
            is BigInteger -> {
                if (value.bitLength() < 63) {
                    b.setInteger(value.longValueExact())
                } else {
                    b.setBigInteger(value.toString())
                }
            }
            is Long -> b.setInteger(value)
            is Int -> b.setInteger(value.toLong())
            is Short -> b.setInteger(value.toLong())
            else -> error("Expected BigInteger, Long, or Int, got ${value::class.simpleName}")
        }
    }

    private fun encodeNumber(
        value: Any,
        b: AirbyteValueProtobuf.Builder
    ): AirbyteValueProtobuf.Builder {
        return when (value) {
            is BigDecimal -> b.setBigDecimal(value.toPlainString())
            is Double -> b.setNumber(value)
            is Float -> b.setNumber(value.toDouble())
            else -> error("Expected BigDecimal, Double, or Float, got ${value::class.simpleName}")
        }
    }

    private fun encodeDate(
        value: Any,
        b: AirbyteValueProtobuf.Builder
    ): AirbyteValueProtobuf.Builder {
        val localDate =
            when (value) {
                is LocalDate -> value
                is java.sql.Date -> value.toLocalDate()
                else -> error("Expected LocalDate or java.sql.Date, got ${value::class.simpleName}")
            }
        return b.setDate(localDate.toEpochDay())
    }

    private fun encodeTimeWithTimezone(
        value: Any,
        b: AirbyteValueProtobuf.Builder
    ): AirbyteValueProtobuf.Builder {
        require(value is OffsetTime) { "Expected OffsetTime, got ${value::class.simpleName}" }
        val offsetTimeMsg =
            io.airbyte.protocol.protobuf.AirbyteRecordMessage.OffsetTime.newBuilder()
                .setNanosOfDay(value.toLocalTime().toNanoOfDay())
                .setOffsetSeconds(value.offset.totalSeconds)
                .build()
        return b.setTimeWithTimezone(offsetTimeMsg)
    }

    private fun encodeTimeWithoutTimezone(
        value: Any,
        b: AirbyteValueProtobuf.Builder
    ): AirbyteValueProtobuf.Builder {
        val localTime =
            when (value) {
                is LocalTime -> value
                is java.sql.Time -> value.toLocalTime()
                else -> error("Expected LocalTime or java.sql.Time, got ${value::class.simpleName}")
            }
        return b.setTimeWithoutTimezone(localTime.toNanoOfDay())
    }

    private fun encodeTimestampWithTimezone(
        value: Any,
        b: AirbyteValueProtobuf.Builder
    ): AirbyteValueProtobuf.Builder {
        val offsetDateTime =
            when (value) {
                is OffsetDateTime -> value
                is java.sql.Timestamp -> OffsetDateTime.ofInstant(value.toInstant(), ZoneOffset.UTC)
                else ->
                    error(
                        "Expected OffsetDateTime or java.sql.Timestamp, got ${value::class.simpleName}"
                    )
            }
        val instant = offsetDateTime.toInstant()
        val offsetDateTimeMsg =
            io.airbyte.protocol.protobuf.AirbyteRecordMessage.OffsetDateTime.newBuilder()
                .setEpochSecond(instant.epochSecond)
                .setNano(instant.nano)
                .setOffsetSeconds(offsetDateTime.offset.totalSeconds)
                .build()
        return b.setTimestampWithTimezone(offsetDateTimeMsg)
    }

    private fun encodeTimestampWithoutTimezone(
        value: Any,
        b: AirbyteValueProtobuf.Builder
    ): AirbyteValueProtobuf.Builder {
        val localDateTime =
            when (value) {
                is LocalDateTime -> value
                is java.sql.Timestamp -> value.toLocalDateTime()
                else ->
                    error(
                        "Expected LocalDateTime or java.sql.Timestamp, got ${value::class.simpleName}"
                    )
            }
        val localDateTimeMsg =
            io.airbyte.protocol.protobuf.AirbyteRecordMessage.LocalDateTime.newBuilder()
                .setDateDaysSinceEpoch(localDateTime.toLocalDate().toEpochDay())
                .setNanosOfDay(localDateTime.toLocalTime().toNanoOfDay())
                .build()
        return b.setTimestampWithoutTimezone(localDateTimeMsg)
    }

    private fun encodeJson(
        value: Any,
        b: AirbyteValueProtobuf.Builder
    ): AirbyteValueProtobuf.Builder {
        val jsonBytes =
            when (value) {
                is String -> value.toByteArray(StandardCharsets.UTF_8)
                is ByteArray -> value
                is ByteBuffer -> value.array()
                else ->
                    error("Expected String or ByteArray for JSON, got ${value::class.simpleName}")
            }
        return b.setJson(ByteString.copyFrom(jsonBytes))
    }

    private fun encodeBinary(
        value: Any,
        b: AirbyteValueProtobuf.Builder
    ): AirbyteValueProtobuf.Builder {
        val base64String =
            when (value) {
                is ByteArray -> Base64.getEncoder().encodeToString(value)
                is ByteBuffer -> Base64.getEncoder().encodeToString(value.array())
                else ->
                    error(
                        "Expected ByteArray or ByteBuffer for Binary, got ${value::class.simpleName}"
                    )
            }
        return b.setString(base64String)
    }
}
