/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.load.file.object_storage

import com.fasterxml.jackson.core.JsonGenerator
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_DATA
import io.airbyte.cdk.util.Jsons
import java.math.BigDecimal
import java.math.BigInteger

class ProtoToJsonWriter(
    private val columns: Array<AirbyteValueProxy.FieldAccessor>,
    private val flatten: Boolean,
    private val stringifyObjects: Boolean = false,
) {

    fun writeMeta(gen: JsonGenerator, record: DestinationRecordRaw, changes: List<Meta.Change>) =
        with(gen) {
            writeStringField(COLUMN_NAME_AB_RAW_ID, record.airbyteRawId.toString())
            writeNumberField(COLUMN_NAME_AB_EXTRACTED_AT, record.rawData.emittedAtMs)

            // _airbyte_meta
            if (stringifyObjects) {
                writeStringField(COLUMN_NAME_AB_META, buildMetaJson(record, changes))
            } else {
                writeFieldName(COLUMN_NAME_AB_META)
                writeStartObject()
                writeNumberField("sync_id", record.stream.syncId)

                writeFieldName("changes")
                writeStartArray()
                for (c in changes) {
                    writeStartObject()
                    writeStringField("field", c.field)
                    writeStringField("change", c.change.name)
                    writeStringField("reason", c.reason.name)
                    writeEndObject()
                }
                writeEndArray()
                writeEndObject() // _airbyte_meta
            }

            writeNumberField(COLUMN_NAME_AB_GENERATION_ID, record.stream.generationId)
        }

    fun writePayload(gen: JsonGenerator, src: DestinationRecordProtobufSource) {
        val proxy = src.asAirbyteValueProxy()

        if (!flatten) {
            gen.writeFieldName(COLUMN_NAME_DATA)
            if (stringifyObjects) {
                gen.writeString(buildDataObject(proxy).toString())
                return
            }
            gen.writeStartObject()
        }

        for (column in columns) writeValue(gen, column, proxy, stringifyObjects && flatten)

        if (!flatten) gen.writeEndObject()
    }

    private fun buildMetaJson(record: DestinationRecordRaw, changes: List<Meta.Change>): String {
        val meta = Jsons.objectNode()
        meta.put("sync_id", record.stream.syncId)
        val changesArray = meta.putArray("changes")
        for (c in changes) {
            val changeNode = changesArray.addObject()
            changeNode.put("field", c.field)
            changeNode.put("change", c.change.name)
            changeNode.put("reason", c.reason.name)
        }
        return meta.toString()
    }

    private fun buildDataObject(proxy: AirbyteValueProxy): ObjectNode {
        val data = Jsons.objectNode()
        for (column in columns) {
            putValue(data, column, proxy)
        }
        return data
    }

    private fun putValue(
        node: ObjectNode,
        field: AirbyteValueProxy.FieldAccessor,
        proxy: AirbyteValueProxy
    ) {
        when (field.type) {
            is ArrayType,
            is ArrayTypeWithoutSchema,
            is UnionType,
            is ObjectType,
            is ObjectTypeWithEmptySchema,
            is ObjectTypeWithoutSchema -> {
                val json = proxy.getJsonNode(field)
                if (json == null) node.putNull(field.name) else node.set(field.name, json)
            }
            is BooleanType -> {
                val value = proxy.getBoolean(field)
                if (value == null) node.putNull(field.name) else node.put(field.name, value)
            }
            is IntegerType -> {
                val value = proxy.getInteger(field)
                if (value == null) node.putNull(field.name) else node.put(field.name, value)
            }
            is NumberType -> {
                val value = proxy.getNumber(field)
                if (value == null) node.putNull(field.name) else node.put(field.name, value)
            }
            is DateType -> {
                val value = proxy.getDate(field)
                if (value == null) node.putNull(field.name) else node.put(field.name, value)
            }
            is StringType -> {
                val value = proxy.getString(field)
                if (value == null) node.putNull(field.name) else node.put(field.name, value)
            }
            is TimeTypeWithTimezone -> {
                val value = proxy.getTimeWithTimezone(field)
                if (value == null) node.putNull(field.name) else node.put(field.name, value)
            }
            is TimeTypeWithoutTimezone -> {
                val value = proxy.getTimeWithoutTimezone(field)
                if (value == null) node.putNull(field.name) else node.put(field.name, value)
            }
            is TimestampTypeWithTimezone -> {
                val value = proxy.getTimestampWithTimezone(field)
                if (value == null) node.putNull(field.name) else node.put(field.name, value)
            }
            is TimestampTypeWithoutTimezone -> {
                val value = proxy.getTimestampWithoutTimezone(field)
                if (value == null) node.putNull(field.name) else node.put(field.name, value)
            }
            is UnknownType -> node.putNull(field.name)
        }
    }

    private fun writeValue(
        gen: JsonGenerator,
        field: AirbyteValueProxy.FieldAccessor,
        proxy: AirbyteValueProxy,
        stringifyObjects: Boolean,
    ) =
        when (field.type) {
            is ArrayType,
            is ArrayTypeWithoutSchema,
            is UnionType,
            is ObjectType,
            is ObjectTypeWithEmptySchema,
            is ObjectTypeWithoutSchema ->
                gen.writeTreeOrNull(field, proxy.getJsonNode(field), stringifyObjects)
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
        node: com.fasterxml.jackson.databind.JsonNode?,
        stringifyObjects: Boolean,
    ) {
        if (node == null) writeNullField(field.name)
        else {
            writeFieldName(field.name)
            // Only stringify JSON objects; leave arrays as arrays (matches issue scope).
            if (stringifyObjects && node.isObject) writeString(node.toString())
            else writeTree(node) // requires codec: generator created from ObjectMapper
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
