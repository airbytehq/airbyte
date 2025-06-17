/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.load.file.object_storage

import com.fasterxml.jackson.core.JsonGenerator
import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_DATA
import java.math.BigDecimal
import java.math.BigInteger

class ProtoToJsonWriter(
    private val columns: Array<AirbyteValueProxy.FieldAccessor>,
    private val flatten: Boolean
) {

    fun writeMeta(gen: JsonGenerator, record: DestinationRecordRaw) =
        with(gen) {
            writeStringField(COLUMN_NAME_AB_RAW_ID, record.airbyteRawId.toString())
            writeNumberField(COLUMN_NAME_AB_EXTRACTED_AT, record.rawData.emittedAtMs)

            // _airbyte_meta
            writeFieldName(COLUMN_NAME_AB_META)
            writeStartObject()
            writeNumberField("sync_id", record.stream.syncId)

            writeFieldName("changes")
            writeStartArray()
            for (c in record.rawData.sourceMeta.changes) {
                writeStartObject()
                writeStringField("field", c.field)
                writeStringField("change", c.change.name)
                writeStringField("reason", c.reason.name)
                writeEndObject()
            }
            writeEndArray()
            writeEndObject() // _airbyte_meta

            writeNumberField(COLUMN_NAME_AB_GENERATION_ID, record.stream.generationId)
        }

    fun writePayload(gen: JsonGenerator, src: DestinationRecordProtobufSource) {
        val proxy = src.asAirbyteValueProxy()

        if (!flatten) {
            gen.writeFieldName(COLUMN_NAME_DATA)
            gen.writeStartObject()
        }

        for (column in columns) writeValue(gen, column, proxy)

        if (!flatten) gen.writeEndObject()
    }

    private fun writeValue(
        gen: JsonGenerator,
        field: AirbyteValueProxy.FieldAccessor,
        proxy: AirbyteValueProxy
    ) =
        when (field.type) {
            is ArrayType,
            is ArrayTypeWithoutSchema,
            is UnionType,
            is ObjectType,
            is ObjectTypeWithEmptySchema,
            is ObjectTypeWithoutSchema -> gen.writeTreeOrNull(field, proxy.getJsonNode(field))
            is BooleanType -> gen.writeBooleanOrNull(field, proxy.getBoolean(field))
            is IntegerType -> gen.writeNumberOrNull(field, proxy.getInteger(field))
            is NumberType -> gen.writeNumberOrNull(field, proxy.getNumber(field))
            is DateType -> gen.writeStringOrNull(field, proxy.getDate(field))
            is StringType -> gen.writeStringOrNull(field, proxy.getString(field))
            is TimeTypeWithTimezone ->
                gen.writeStringOrNull(field, proxy.getTimeWithTimezone(field))
            is TimeTypeWithoutTimezone ->
                gen.writeStringOrNull(
                    field,
                    proxy.getTimeWithoutTimezone(field),
                )
            is TimestampTypeWithTimezone ->
                gen.writeStringOrNull(
                    field,
                    proxy.getTimestampWithTimezone(field),
                )
            is TimestampTypeWithoutTimezone ->
                gen.writeStringOrNull(
                    field,
                    proxy.getTimestampWithoutTimezone(field),
                )
            is UnknownType -> gen.writeNullField(field.name)
        }

    private fun JsonGenerator.writeTreeOrNull(
        field: AirbyteValueProxy.FieldAccessor,
        node: com.fasterxml.jackson.databind.JsonNode?
    ) {
        if (node == null) writeNullField(field.name)
        else {
            writeFieldName(field.name)
            writeTree(node) // requires codec: generator created from ObjectMapper
        }
    }

    private fun JsonGenerator.writeBooleanOrNull(
        field: AirbyteValueProxy.FieldAccessor,
        value: Boolean?
    ) = value?.let { writeBooleanField(field.name, it) } ?: writeNullField(field.name)

    private fun JsonGenerator.writeNumberOrNull(
        field: AirbyteValueProxy.FieldAccessor,
        value: BigDecimal?
    ) = value?.let { writeNumberField(field.name, it) } ?: writeNullField(field.name)

    private fun JsonGenerator.writeNumberOrNull(
        field: AirbyteValueProxy.FieldAccessor,
        value: BigInteger?
    ) = value?.let { writeNumberField(field.name, it) } ?: writeNullField(field.name)

    private fun JsonGenerator.writeStringOrNull(
        field: AirbyteValueProxy.FieldAccessor,
        value: String?
    ) = value?.let { writeStringField(field.name, it) } ?: writeNullField(field.name)
}
