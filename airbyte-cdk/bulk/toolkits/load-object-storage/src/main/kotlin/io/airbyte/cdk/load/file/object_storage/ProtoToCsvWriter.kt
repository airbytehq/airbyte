/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.object_storage

import com.fasterxml.jackson.core.io.JsonStringEncoder
import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.message.*
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneOffset

class ProtoToCsvWriter(
    private val header: Array<String>,
    private val columns: Array<AirbyteValueProxy.FieldAccessor>,
    private val rootLevelFlattening: Boolean,
    private val extractedAtTsTz: Boolean,
) {

    private val idxRawId = header.indexOf(Meta.COLUMN_NAME_AB_RAW_ID)
    private val idxExtractedAt = header.indexOf(Meta.COLUMN_NAME_AB_EXTRACTED_AT)
    private val idxMeta = header.indexOf(Meta.COLUMN_NAME_AB_META)
    private val idxGenerationId = header.indexOf(Meta.COLUMN_NAME_AB_GENERATION_ID)
    private val idxData = header.indexOf(Meta.COLUMN_NAME_DATA)
    private val jsonEscaper = JsonStringEncoder.getInstance()

    private val rowIndex: Map<String, Int> =
        if (rootLevelFlattening) {
            columns.associate { it.name to header.indexOf(it.name) }
        } else {
            emptyMap()
        }

    private val rowBuf: Array<Any?> = arrayOfNulls(header.size)

    fun toCsvRow(
        record: DestinationRecordRaw,
        src: DestinationRecordProtobufSource,
        changes: List<Meta.Change>
    ): Array<Any?> {
        rowBuf[idxRawId] = record.airbyteRawId.toString()

        val emitted = src.emittedAtMs
        rowBuf[idxExtractedAt] =
            if (extractedAtTsTz)
                OffsetDateTime.ofInstant(Instant.ofEpochMilli(emitted), ZoneOffset.UTC).toString()
            else emitted

        rowBuf[idxMeta] = buildMeta(record.stream.syncId, changes)
        rowBuf[idxGenerationId] = record.stream.generationId

        val proxy = src.asAirbyteValueProxy()

        if (rootLevelFlattening) {
            var i = 0
            while (i < columns.size) {
                val column = columns[i]
                val index =
                    rowIndex[column.name]
                        ?: throw IllegalArgumentException(
                            "Column '${column.name}' not found in row index"
                        )
                rowBuf[index] = fetchValue(proxy, column)
                i++
            }
        } else {
            // one big JSON blob under _airbyte_data
            rowBuf[idxData] = buildPayloadJson(proxy)
        }

        return rowBuf
    }

    private fun fetchValue(
        proxy: AirbyteValueProxy,
        field: AirbyteValueProxy.FieldAccessor,
    ): Any {
        return when (field.type) {
            is BooleanType -> proxy.getBoolean(field) ?: ""
            is IntegerType -> proxy.getInteger(field) ?: ""
            is NumberType -> proxy.getNumber(field) ?: ""
            is StringType -> proxy.getString(field) ?: ""
            is DateType -> proxy.getDate(field) ?: ""
            is TimeTypeWithTimezone -> proxy.getTimeWithTimezone(field) ?: ""
            is TimeTypeWithoutTimezone -> proxy.getTimeWithoutTimezone(field) ?: ""
            is TimestampTypeWithTimezone -> proxy.getTimestampWithTimezone(field) ?: ""
            is TimestampTypeWithoutTimezone -> proxy.getTimestampWithoutTimezone(field) ?: ""
            is UnknownType -> ""
            // complex = JSON string
            else -> proxy.getJsonNode(field)?.toString() ?: ""
        }
    }

    private fun buildMeta(syncId: Long, changes: List<Meta.Change>): String =
        buildString(64) {
            append('{')
            append("\"sync_id\":").append(syncId).append(',')
            append("\"changes\":[")
            changes.forEachIndexed { idx, c ->
                append('{')
                append("\"field\":\"").append(escape(c.field)).append("\",")
                append("\"change\":\"").append(c.change.name).append("\",")
                append("\"reason\":\"").append(c.reason.name).append("\"}")
                if (idx != changes.lastIndex) append(',')
            }
            append("]}")
        }

    private fun buildPayloadJson(proxy: AirbyteValueProxy): String =
        buildString(256) {
            append('{')
            var first = true
            for (field in columns) {
                val v = proxyValueAsJson(proxy, field)
                if (!first) append(',')
                append('"').append(escape(field.name)).append("\":").append(v)
                first = false
            }
            append('}')
        }

    private fun proxyValueAsJson(
        proxy: AirbyteValueProxy,
        field: AirbyteValueProxy.FieldAccessor,
    ): String =
        when (field.type) {
            is BooleanType -> proxy.getBoolean(field)?.toString() ?: "null"
            is IntegerType -> proxy.getInteger(field)?.toString() ?: "null"
            is NumberType -> proxy.getNumber(field)?.toString() ?: "null"
            is StringType -> proxy.getString(field)?.let { "\"${escape(it)}\"" } ?: "null"
            is DateType -> proxy.getDate(field)?.let { "\"$it\"" } ?: "null"
            is TimeTypeWithTimezone -> proxy.getTimeWithTimezone(field)?.let { "\"$it\"" } ?: "null"
            is TimeTypeWithoutTimezone -> proxy.getTimeWithoutTimezone(field)?.let { "\"$it\"" }
                    ?: "null"
            is TimestampTypeWithTimezone -> proxy.getTimestampWithTimezone(field)?.let { "\"$it\"" }
                    ?: "null"
            is TimestampTypeWithoutTimezone ->
                proxy.getTimestampWithoutTimezone(field)?.let { "\"$it\"" } ?: "null"
            is UnknownType -> "null"
            else -> proxy.getJsonNode(field)?.toString() ?: "null"
        }

    private fun escape(s: String): String = String(jsonEscaper.quoteAsString(s))
}
