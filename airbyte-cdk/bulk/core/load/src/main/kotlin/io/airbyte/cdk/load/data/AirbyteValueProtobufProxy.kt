/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import com.fasterxml.jackson.core.io.BigDecimalParser
import com.fasterxml.jackson.core.io.BigIntegerParser
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.data.AirbyteValueProxy.FieldAccessor
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import java.math.BigDecimal
import java.math.BigInteger

/**
 * Protobuf is sent as an ordered list of AirbyteValues. Coherent access depends on the source and
 * destination agreeing on the schema. Currently, this is alphabetical order by field name, as
 * constraints on the socket implementation guarantee that source and destination will always see
 * the same schema. Eventually this order needs to be set by the source with a header message.
 */
class AirbyteValueProtobufProxy(private val data: List<AirbyteValueProtobuf>) : AirbyteValueProxy {
    private inline fun <T> getNullable(field: FieldAccessor, getter: (FieldAccessor) -> T): T? =
        if (data[field.index].isNull) null else getter(field)

    override fun getBoolean(field: FieldAccessor): Boolean? =
        getNullable(field) { data[it.index].boolean }

    override fun getString(field: FieldAccessor): String? =
        getNullable(field) { data[it.index].string }

    override fun getInteger(field: FieldAccessor): BigInteger? =
        getNullable(field) {
            if (data[it.index].hasBigInteger()) {
                BigIntegerParser.parseWithFastParser(data[it.index].bigInteger)
            } else {
                data[it.index].integer.toBigInteger()
            }
        }

    override fun getNumber(field: FieldAccessor): BigDecimal? =
        getNullable(field) {
            if (data[it.index].hasBigDecimal()) {
                BigDecimalParser.parseWithFastParser(data[it.index].bigDecimal)
            } else if (data[it.index].hasNumber()) {
                data[it.index].number.toBigDecimal()
            } else {
                null
            }
        }

    override fun getDate(field: FieldAccessor): String? =
        getNullable(field) { data[field.index].date }

    override fun getTimeWithTimezone(field: FieldAccessor): String? =
        getNullable(field) { data[field.index].timeWithTimezone }

    override fun getTimeWithoutTimezone(field: FieldAccessor): String? =
        getNullable(field) { data[field.index].timeWithoutTimezone }

    override fun getTimestampWithTimezone(field: FieldAccessor): String? =
        getNullable(field) { data[field.index].timestampWithTimezone }

    override fun getTimestampWithoutTimezone(field: FieldAccessor): String? =
        getNullable(field) { data[field.index].timestampWithoutTimezone }

    override fun getJsonBytes(field: FieldAccessor): ByteArray? =
        getNullable(field) { data[field.index].json.toByteArray() }

    override fun getJsonNode(field: FieldAccessor): JsonNode? =
        getJsonBytes(field)?.let { Jsons.readTree(it) }
}
