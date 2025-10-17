/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.protocol

import com.fasterxml.jackson.core.io.BigDecimalParser
import com.fasterxml.jackson.core.io.BigIntegerParser
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import java.nio.charset.StandardCharsets
import java.time.Instant
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneOffset

class AirbyteValueProtobufDecoder {

    /**
     * Decodes a protobuf value into its corresponding Java type. Returns null if the value is
     * marked as null.
     */
    fun decode(value: AirbyteValueProtobuf): Any? {
        return when (value.valueCase) {
            AirbyteValueProtobuf.ValueCase.BOOLEAN -> value.boolean
            AirbyteValueProtobuf.ValueCase.STRING -> value.string
            AirbyteValueProtobuf.ValueCase.INTEGER -> value.integer.toBigInteger()
            AirbyteValueProtobuf.ValueCase.BIG_INTEGER ->
                BigIntegerParser.parseWithFastParser(value.bigInteger)
            AirbyteValueProtobuf.ValueCase.NUMBER -> value.number.toBigDecimal()
            AirbyteValueProtobuf.ValueCase.BIG_DECIMAL ->
                BigDecimalParser.parseWithFastParser(value.bigDecimal)
            AirbyteValueProtobuf.ValueCase.DATE -> LocalDate.ofEpochDay(value.date)
            AirbyteValueProtobuf.ValueCase.TIME_WITHOUT_TIMEZONE ->
                LocalTime.ofNanoOfDay(value.timeWithoutTimezone)
            AirbyteValueProtobuf.ValueCase.TIME_WITH_TIMEZONE -> {
                val offsetTimeMsg = value.timeWithTimezone
                val localTime = LocalTime.ofNanoOfDay(offsetTimeMsg.nanosOfDay)
                val offset = ZoneOffset.ofTotalSeconds(offsetTimeMsg.offsetSeconds)
                OffsetTime.of(localTime, offset)
            }
            AirbyteValueProtobuf.ValueCase.TIMESTAMP_WITHOUT_TIMEZONE -> {
                val localDateTimeMsg = value.timestampWithoutTimezone
                val localDate = LocalDate.ofEpochDay(localDateTimeMsg.dateDaysSinceEpoch)
                val localTime = LocalTime.ofNanoOfDay(localDateTimeMsg.nanosOfDay)
                LocalDateTime.of(localDate, localTime)
            }
            AirbyteValueProtobuf.ValueCase.TIMESTAMP_WITH_TIMEZONE -> {
                val offsetDateTimeMsg = value.timestampWithTimezone
                val instant =
                    Instant.ofEpochSecond(
                        offsetDateTimeMsg.epochSecond,
                        offsetDateTimeMsg.nano.toLong()
                    )
                val offset = ZoneOffset.ofTotalSeconds(offsetDateTimeMsg.offsetSeconds)
                OffsetDateTime.ofInstant(instant, offset)
            }
            AirbyteValueProtobuf.ValueCase.JSON -> value.json.toString(StandardCharsets.UTF_8)
            AirbyteValueProtobuf.ValueCase.NULL,
            AirbyteValueProtobuf.ValueCase.VALUE_NOT_SET,
            null -> null
        }
    }
}
