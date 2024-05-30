/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.avro

import io.airbyte.cdk.integrations.destination.record_buffer.BaseSerializedBuffer
import io.airbyte.cdk.integrations.destination.record_buffer.BufferCreateFunction
import io.airbyte.cdk.integrations.destination.record_buffer.BufferStorage
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
    schema: Schema
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
        avroRecordFactory = AvroRecordFactory(schema, AvroConstants.JSON_CONVERTER)
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
    override fun writeRecord(record: AirbyteRecordMessage) {
        dataFileWriter!!.append(avroRecordFactory.getAvroRecord(UUID.randomUUID(), record))
    }

    @Throws(IOException::class)
    @Suppress("DEPRECATION")
    override fun writeRecord(recordString: String, airbyteMetaString: String, emittedAt: Long) {
        // TODO Remove this double deserialization when S3 Destinations moves to Async.
        writeRecord(
            Jsons.deserialize(
                    recordString,
                    AirbyteRecordMessage::class.java,
                )
                .withEmittedAt(emittedAt),
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
            createStorageFunction: Callable<BufferStorage>
        ): BufferCreateFunction {
            val codecFactory = config.codecFactory
            return BufferCreateFunction {
                stream: AirbyteStreamNameNamespacePair,
                catalog: ConfiguredAirbyteCatalog ->
                val schemaConverter = JsonToAvroSchemaConverter()
                val schema =
                    schemaConverter.getAvroSchema(
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
                            ),
                        stream.name,
                        stream.namespace,
                    )
                AvroSerializedBuffer(createStorageFunction.call(), codecFactory, schema)
            }
        }
    }
}
