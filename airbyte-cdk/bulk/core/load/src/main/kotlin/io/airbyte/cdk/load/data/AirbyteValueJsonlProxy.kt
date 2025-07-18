/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.data.AirbyteValueProxy.FieldAccessor
import io.airbyte.cdk.load.util.serializeToJsonBytes
import java.math.BigDecimal
import java.math.BigInteger

class AirbyteValueJsonlProxy(private val data: ObjectNode) : AirbyteValueProxy {
    private inline fun <T> getNullable(field: FieldAccessor, getter: (FieldAccessor) -> T): T? =
        data.get(field.name)?.let { if (it.isNull) null else getter(field) }

    override fun getBoolean(field: FieldAccessor): Boolean? =
        getNullable(field) { data.get(it.name).booleanValue() }

    override fun getString(field: FieldAccessor): String? =
        getNullable(field) { data.get(it.name).asText() }

    override fun getInteger(field: FieldAccessor): BigInteger? =
        getNullable(field) { data.get(it.name).bigIntegerValue() }

    override fun getNumber(field: FieldAccessor): BigDecimal? =
        getNullable(field) { data.get(it.name).decimalValue() }

    override fun getDate(field: FieldAccessor): String? =
        getNullable(field) { data.get(it.name).asText() }

    override fun getTimeWithTimezone(field: FieldAccessor): String? =
        getNullable(field) { data.get(it.name).asText() }

    override fun getTimeWithoutTimezone(field: FieldAccessor): String? =
        getNullable(field) { data.get(it.name).asText() }

    override fun getTimestampWithTimezone(field: FieldAccessor): String? =
        getNullable(field) { data.get(it.name).asText() }

    override fun getTimestampWithoutTimezone(field: FieldAccessor): String? =
        getNullable(field) { data.get(it.name).asText() }

    override fun getJsonBytes(field: FieldAccessor): ByteArray? =
        getNullable(field) { data.get(it.name).serializeToJsonBytes() }

    override fun getJsonNode(field: FieldAccessor): JsonNode? =
        getNullable(field) { data.get(it.name) }
}
