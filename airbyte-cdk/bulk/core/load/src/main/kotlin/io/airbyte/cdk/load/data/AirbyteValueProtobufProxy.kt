/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.data.AirbyteValueProxy.FieldAccessor
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.protocol.ProtobufTypeBasedDecoder
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.OffsetTime

/**
 * Protobuf is sent as an ordered list of AirbyteValues. Coherent access depends on the source and
 * destination agreeing on the schema. Currently, this is alphabetical order by field name, as
 * constraints on the socket implementation guarantee that source and destination will always see
 * the same schema. Eventually this order needs to be set by the source with a header message.
 */
class AirbyteValueProtobufProxy(private val data: List<AirbyteValueProtobuf>) : AirbyteValueProxy {
    private val decoder = ProtobufTypeBasedDecoder()

    private inline fun <T> getNullable(field: FieldAccessor, getter: (FieldAccessor) -> T): T? {
        return if (data.isEmpty() || data.size < field.index || data[field.index].isNull) null
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
        getNullable(field) {
            (decoder.decode(data[it.index]) as? LocalDate)?.toString()
        }

    override fun getTimeWithTimezone(field: FieldAccessor): String? =
        getNullable(field) {
            (decoder.decode(data[it.index]) as? OffsetTime)?.toString()
        }

    override fun getTimeWithoutTimezone(field: FieldAccessor): String? =
        getNullable(field) {
            (decoder.decode(data[it.index]) as? java.time.LocalTime)?.toString()
        }

    override fun getTimestampWithTimezone(field: FieldAccessor): String? =
        getNullable(field) {
            (decoder.decode(data[it.index]) as? OffsetDateTime)?.toString()
        }

    override fun getTimestampWithoutTimezone(field: FieldAccessor): String? =
        getNullable(field) {
            (decoder.decode(data[it.index]) as? LocalDateTime)?.toString()
        }

    override fun getJsonBytes(field: FieldAccessor): ByteArray? =
        getNullable(field) { data[field.index].json.toByteArray() }

    override fun getJsonNode(field: FieldAccessor): JsonNode? =
        getJsonBytes(field)?.let { Jsons.readTree(it) }
}
