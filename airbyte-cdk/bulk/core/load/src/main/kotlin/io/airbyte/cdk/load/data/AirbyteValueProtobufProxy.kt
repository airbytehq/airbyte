/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.data.AirbyteValueProxy.FieldAccessor
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.protocol.AirbyteValueProtobufDecoder
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeFormatterBuilder
import java.time.temporal.ChronoField

/**
 * Protobuf is sent as an ordered list of AirbyteValues. Coherent access depends on the source and
 * destination agreeing on the schema. Currently, this is alphabetical order by field name, as
 * constraints on the socket implementation guarantee that source and destination will always see
 * the same schema. Eventually this order needs to be set by the source with a header message.
 *
 * @deprecated This is inefficient and should not be used. Use
 * [io.airbyte.cdk.load.dataflow.transform.medium.ProtobufConverter] instead.
 * @see io.airbyte.cdk.load.dataflow.transform.medium.ProtobufConverter
 */
@Deprecated("This is inefficient and should not be used. Use ProtobufConverter instead.")
class AirbyteValueProtobufProxy(private val data: List<AirbyteValueProtobuf>) : AirbyteValueProxy {
    private val decoder = AirbyteValueProtobufDecoder()

    companion object {
        // Formatters that preserve full precision including trailing zeros
        private val LOCAL_TIME_FORMATTER =
            DateTimeFormatterBuilder()
                .appendValue(ChronoField.HOUR_OF_DAY, 2)
                .appendLiteral(':')
                .appendValue(ChronoField.MINUTE_OF_HOUR, 2)
                .appendLiteral(':')
                .appendValue(ChronoField.SECOND_OF_MINUTE, 2)
                .appendFraction(ChronoField.NANO_OF_SECOND, 0, 9, true)
                .toFormatter()

        private val OFFSET_TIME_FORMATTER =
            DateTimeFormatterBuilder().append(LOCAL_TIME_FORMATTER).appendOffsetId().toFormatter()

        private val LOCAL_DATE_TIME_FORMATTER =
            DateTimeFormatterBuilder()
                .append(DateTimeFormatter.ISO_LOCAL_DATE)
                .appendLiteral('T')
                .append(LOCAL_TIME_FORMATTER)
                .toFormatter()

        private val OFFSET_DATE_TIME_FORMATTER =
            DateTimeFormatterBuilder()
                .append(DateTimeFormatter.ISO_LOCAL_DATE)
                .appendLiteral('T')
                .append(LOCAL_TIME_FORMATTER)
                .appendOffsetId()
                .toFormatter()
    }

    private inline fun <T> getNullable(field: FieldAccessor, getter: (FieldAccessor) -> T): T? {
        return if (
            data.isEmpty() ||
                data.size < field.index ||
                data[field.index].valueCase == AirbyteValueProtobuf.ValueCase.NULL
        )
            null
        else getter(field)
    }

    override fun getBoolean(field: FieldAccessor): Boolean? =
        getNullable(field) { decoder.decode(data[it.index]) as? Boolean }

    override fun getString(field: FieldAccessor): String? =
        getNullable(field) { decoder.decode(data[it.index]) as? String }

    override fun getInteger(field: FieldAccessor): BigInteger? =
        getNullable(field) { decoder.decode(data[it.index]) as? BigInteger }

    override fun getNumber(field: FieldAccessor): BigDecimal? =
        getNullable(field) { decoder.decode(data[it.index]) as? BigDecimal }

    override fun getDate(field: FieldAccessor): String? =
        getNullable(field) { (decoder.decode(data[it.index]) as? LocalDate)?.toString() }

    override fun getTimeWithTimezone(field: FieldAccessor): String? =
        getNullable(field) {
            (decoder.decode(data[it.index]) as? OffsetTime)?.format(OFFSET_TIME_FORMATTER)
        }

    override fun getTimeWithoutTimezone(field: FieldAccessor): String? =
        getNullable(field) {
            (decoder.decode(data[it.index]) as? java.time.LocalTime)?.format(LOCAL_TIME_FORMATTER)
        }

    override fun getTimestampWithTimezone(field: FieldAccessor): String? =
        getNullable(field) {
            (decoder.decode(data[it.index]) as? OffsetDateTime)?.format(OFFSET_DATE_TIME_FORMATTER)
        }

    override fun getTimestampWithoutTimezone(field: FieldAccessor): String? =
        getNullable(field) {
            (decoder.decode(data[it.index]) as? LocalDateTime)?.format(LOCAL_DATE_TIME_FORMATTER)
        }

    override fun getJsonBytes(field: FieldAccessor): ByteArray? =
        getNullable(field) { data[field.index].json.toByteArray() }

    override fun getJsonNode(field: FieldAccessor): JsonNode? =
        getJsonBytes(field)?.let { Jsons.readTree(it) }
}
