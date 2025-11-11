/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.destination.record_buffer.BaseSerializedBuffer
import io.airbyte.cdk.integrations.destination.record_buffer.BufferCreateFunction
import io.airbyte.cdk.integrations.destination.record_buffer.BufferStorage
import io.airbyte.cdk.integrations.destination.s3.jsonschema.JsonSchemaUnionMerger
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import java.io.IOException
import java.io.OutputStream
import java.util.UUID
import java.util.concurrent.Callable
import org.apache.avro.Schema
import org.apache.avro.file.CodecFactory
import org.apache.avro.file.DataFileWriter
import org.apache.avro.generic.GenericData
import org.apache.avro.generic.GenericDatumWriter
import org.apache.commons.lang3.StringUtils

class AvroSerializedBuffer(
    bufferStorage: BufferStorage,
    codecFactory: CodecFactory,
    schema: Schema,
    recordPreprocessor: ((JsonNode) -> JsonNode?) = { it },
    private val useV2FieldNames: Boolean = false,
) : BaseSerializedBuffer(bufferStorage) {
    private val codecFactory: CodecFactory
    private val schema: Schema
    private val avroRecordFactory: AvroRecordFactory
    private var dataFileWriter: DataFileWriter<GenericData.Record>?

    init {
        // disable compression stream as it is already handled by codecFactory
        withCompression(false)
        this.codecFactory = codecFactory
        this.schema = schema
        val converter =
            if (useV2FieldNames) AvroRecordFactory.createV2JsonToAvroConverter()
            else AvroRecordFactory.createV1JsonToAvroConverter()
        avroRecordFactory = AvroRecordFactory(schema, converter, recordPreprocessor)
        dataFileWriter = null
    }

    @Throws(IOException::class)
    override fun initWriter(outputStream: OutputStream) {
        dataFileWriter =
            DataFileWriter(GenericDatumWriter<GenericData.Record>())
                .setCodec(codecFactory)
                .create(schema, outputStream)
    }

    @Deprecated("Deprecated in Java")
    @Throws(IOException::class)
    override fun writeRecord(record: AirbyteRecordMessage, generationId: Long, syncId: Long) {
        if (this.useV2FieldNames) {
            dataFileWriter!!.append(
                avroRecordFactory.getAvroRecordV2(UUID.randomUUID(), generationId, syncId, record)
            )
        } else {
            dataFileWriter!!.append(avroRecordFactory.getAvroRecord(UUID.randomUUID(), record))
        }
    }

    @Throws(IOException::class)
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
            generationId
        )
    }

    @Throws(IOException::class)
    override fun flushWriter() {
        dataFileWriter!!.flush()
    }

    @Throws(IOException::class)
    override fun closeWriter() {
        dataFileWriter!!.close()
    }

    companion object {
        const val DEFAULT_SUFFIX: String = ".avro"

        fun createFunction(
            config: UploadAvroFormatConfig,
            createStorageFunction: Callable<BufferStorage>,
            useV2FeatureSet: Boolean = false
        ): BufferCreateFunction {
            val codecFactory = config.codecFactory
            return BufferCreateFunction {
                // Build avro schema
                stream: AirbyteStreamNameNamespacePair,
                catalog: ConfiguredAirbyteCatalog ->
                val jsonSchema =
                    catalog.streams
                        .filter { s: ConfiguredAirbyteStream ->
                            s.stream.name == stream.name &&
                                StringUtils.equals(
                                    s.stream.namespace,
                                    stream.namespace,
                                )
                        }
                        .firstOrNull()
                        ?.stream
                        ?.jsonSchema
                        ?: throw RuntimeException(
                            "No such stream ${stream.namespace}.${stream.name}"
                        )
                val mergedSchema = JsonSchemaUnionMerger().mapSchema(jsonSchema as ObjectNode)
                val preprocessedJsonSchema =
                    if (useV2FeatureSet) {
                        JsonSchemaAvroPreprocessor().mapSchema(mergedSchema)
                    } else jsonSchema
                val avroSchema =
                    JsonToAvroSchemaConverter()
                        .getAvroSchema(
                            preprocessedJsonSchema,
                            stream.name,
                            stream.namespace,
                            useV2FieldNames = useV2FeatureSet,
                            addStringToLogicalTypes = !useV2FeatureSet,
                            appendExtraProps = !useV2FeatureSet
                        )

                // Build record processor
                val recordPreprocessor =
                    if (useV2FeatureSet)
                        { record: JsonNode ->
                            JsonRecordAvroPreprocessor().mapRecordWithSchema(record, mergedSchema)
                        }
                    else { record: JsonNode -> record }

                // Assemble writable buffer
                AvroSerializedBuffer(
                    createStorageFunction.call(),
                    codecFactory,
                    avroSchema,
                    recordPreprocessor = recordPreprocessor,
                    useV2FieldNames = useV2FeatureSet,
                )
            }
        }
    }
}
