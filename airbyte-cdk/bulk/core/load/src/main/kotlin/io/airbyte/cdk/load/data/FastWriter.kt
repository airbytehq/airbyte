package io.airbyte.cdk.load.data

import com.fasterxml.jackson.core.JsonGenerator
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_DATA
import io.airbyte.protocol.protobuf.AirbyteRecordMessage

class FastWriter(
    private val columnTokens: Array<AirbyteValueProxy.FieldAccessor>,
    private val flatten: Boolean
) {
    fun writeMeta(gen: JsonGenerator, r: DestinationRecordRaw) {
        gen.writeStringField(COLUMN_NAME_AB_RAW_ID, r.airbyteRawId.toString())

        gen.writeNumberField(COLUMN_NAME_AB_EXTRACTED_AT, r.rawData.emittedAtMs)

        gen.writeFieldName(COLUMN_NAME_AB_META)
        gen.writeStartObject()
        gen.writeNumberField("sync_id", r.stream.syncId)
        val src = r.rawData
        val changes = src.sourceMeta.changes
        gen.writeFieldName("changes")
        gen.writeStartArray()
        for (c in changes) {
            gen.writeStartObject()
            gen.writeStringField("field", c.field)
            gen.writeStringField("change", c.change.name)
            gen.writeStringField("reason", c.reason.name)
            gen.writeEndObject()
        }
        gen.writeEndArray()
        gen.writeEndObject()

        gen.writeNumberField(COLUMN_NAME_AB_GENERATION_ID, r.stream.generationId)
    }

    fun writePayload(gen: JsonGenerator, src: DestinationRecordProtobufSource) {
        val values = src.source.record.dataList
        if (flatten) {
            columnTokens.forEach {
                if (values[it.index].isNull) {
                    gen.writeNullField(
                        it.name,
                    )
                } else {
                    writeValue(gen, it.name, values[it.index])
                }
            }
        } else {
            gen.writeFieldName(COLUMN_NAME_DATA)
            gen.writeStartObject()
            columnTokens.forEach {
                if (values[it.index].isNull) {
                    gen.writeNullField(
                        it.name,
                    )
                } else {
                    writeValue(gen, it.name, values[it.index])
                }
            }
            gen.writeEndObject()
        }
    }

    private fun writeValue(
        gen: JsonGenerator,
        field: String,
        v: AirbyteRecordMessage.AirbyteValueProtobuf
    ) =
        if (v.valueCase != null) {
            when (v.valueCase!!) {
                AirbyteRecordMessage.AirbyteValueProtobuf.ValueCase.BOOLEAN ->
                    gen.writeBooleanField(
                        field,
                        v.boolean,
                    )
                AirbyteRecordMessage.AirbyteValueProtobuf.ValueCase.STRING ->
                    gen.writeStringField(
                        field,
                        v.string,
                    )
                AirbyteRecordMessage.AirbyteValueProtobuf.ValueCase.INTEGER ->
                    gen.writeNumberField(
                        field,
                        v.integer,
                    )
                AirbyteRecordMessage.AirbyteValueProtobuf.ValueCase.BIG_INTEGER ->
                    gen.writeStringField(
                        field,
                        v.bigInteger,
                    )
                AirbyteRecordMessage.AirbyteValueProtobuf.ValueCase.NUMBER ->
                    gen.writeNumberField(
                        field,
                        v.number,
                    )
                AirbyteRecordMessage.AirbyteValueProtobuf.ValueCase.BIG_DECIMAL ->
                    gen.writeStringField(
                        field,
                        v.bigDecimal,
                    )
                AirbyteRecordMessage.AirbyteValueProtobuf.ValueCase.DATE,
                AirbyteRecordMessage.AirbyteValueProtobuf.ValueCase.TIME_WITH_TIMEZONE,
                AirbyteRecordMessage.AirbyteValueProtobuf.ValueCase.TIME_WITHOUT_TIMEZONE,
                AirbyteRecordMessage.AirbyteValueProtobuf.ValueCase.TIMESTAMP_WITH_TIMEZONE,
                AirbyteRecordMessage.AirbyteValueProtobuf.ValueCase.TIMESTAMP_WITHOUT_TIMEZONE ->
                    gen.writeStringField(
                        field,
                        v.string,
                    )
                AirbyteRecordMessage.AirbyteValueProtobuf.ValueCase.JSON -> {
                    gen.writeFieldName(field)
                    gen.writeRawValue(v.json.toStringUtf8())
                }
                AirbyteRecordMessage.AirbyteValueProtobuf.ValueCase.VALUE_NOT_SET ->
                    gen.writeNullField(
                        field,
                    )
            }
        } else {
            throw RuntimeException("Value case is null")
        }
}
