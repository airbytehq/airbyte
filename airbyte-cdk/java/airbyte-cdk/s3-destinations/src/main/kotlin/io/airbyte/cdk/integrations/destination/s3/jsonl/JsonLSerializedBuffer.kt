/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.jsonl

import com.fasterxml.jackson.core.type.TypeReference
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.record_buffer.BaseSerializedBuffer
import io.airbyte.cdk.integrations.destination.record_buffer.BufferCreateFunction
import io.airbyte.cdk.integrations.destination.record_buffer.BufferStorage
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConstants
import io.airbyte.cdk.integrations.destination.s3.util.CompressionType
import io.airbyte.cdk.integrations.destination.s3.util.Flattening
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import java.io.OutputStream
import java.io.PrintWriter
import java.nio.charset.StandardCharsets
import java.util.UUID
import java.util.concurrent.Callable

class JsonLSerializedBuffer(
    bufferStorage: BufferStorage,
    gzipCompression: Boolean,
    private val flattenData: Boolean = false,
    private val useV2FieldNames: Boolean = false,
) : BaseSerializedBuffer(bufferStorage) {

    private lateinit var printWriter: PrintWriter

    init {
        withCompression(gzipCompression)
    }

    override fun initWriter(outputStream: OutputStream) {
        printWriter = PrintWriter(outputStream, true, StandardCharsets.UTF_8)
    }

    private fun addV2Fields(
        json: ObjectNode,
        record: AirbyteRecordMessage,
        generationId: Long,
        syncId: Long
    ) {
        json.put(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID, UUID.randomUUID().toString())
        json.put(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT, record.emittedAt)
        json.put(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID, generationId)
        val meta = MAPPER.valueToTree<ObjectNode>(record.meta)
        meta.put("sync_id", syncId)
        json.replace(JavaBaseConstants.COLUMN_NAME_AB_META, meta)
    }

    private fun addV1Fields(json: ObjectNode, record: AirbyteRecordMessage) {
        json.put(JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID().toString())
        json.put(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, record.emittedAt)
    }

    @Deprecated("Deprecated in Java")
    override fun writeRecord(record: AirbyteRecordMessage, generationId: Long, syncId: Long) {
        val json = MAPPER.createObjectNode()
        if (useV2FieldNames) {
            addV2Fields(json, record, generationId, syncId)
        } else {
            addV1Fields(json, record)
        }

        if (flattenData) {
            val data: Map<String, JsonNode> =
                MAPPER.convertValue(
                    record.data,
                    object : TypeReference<Map<String, JsonNode>>() {},
                )
            json.setAll<JsonNode>(data)
        } else {
            json.set<JsonNode>(JavaBaseConstants.COLUMN_NAME_DATA, record.data)
        }

        printWriter.println(Jsons.serialize(json))
    }

    @Suppress("DEPRECATION")
    override fun writeRecord(
        recordString: String,
        airbyteMetaString: String,
        generationId: Long,
        emittedAt: Long
    ) {
        // TODO Remove this double deserialization when S3 Destinations moves to Async.
        writeRecord(
            Jsons.deserialize(
                    recordString,
                    AirbyteRecordMessage::class.java,
                )
                .withEmittedAt(emittedAt),
        )
    }

    override fun flushWriter() {
        printWriter.flush()
    }

    override fun closeWriter() {
        printWriter.close()
    }

    companion object {
        private val MAPPER: ObjectMapper = MoreMappers.initMapper()

        @JvmStatic
        fun createBufferFunction(
            config: UploadJsonlFormatConfig?,
            createStorageFunction: Callable<BufferStorage>,
            useV2FieldNames: Boolean = false,
        ): BufferCreateFunction {
            return BufferCreateFunction {
                _: AirbyteStreamNameNamespacePair?,
                _: ConfiguredAirbyteCatalog ->
                val compressionType =
                    if (config == null) S3DestinationConstants.DEFAULT_COMPRESSION_TYPE
                    else config.compressionType
                val flattening = if (config == null) Flattening.NO else config.flatteningType
                JsonLSerializedBuffer(
                    createStorageFunction.call(),
                    compressionType != CompressionType.NO_COMPRESSION,
                    flattening != Flattening.NO,
                    useV2FieldNames,
                )
            }
        }
    }
}
