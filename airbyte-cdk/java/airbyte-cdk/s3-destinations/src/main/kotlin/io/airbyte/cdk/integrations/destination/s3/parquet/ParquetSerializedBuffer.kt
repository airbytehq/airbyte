/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.parquet

import io.airbyte.cdk.integrations.destination.record_buffer.BufferCreateFunction
import io.airbyte.cdk.integrations.destination.record_buffer.FileBuffer
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.UploadFormatConfig
import io.airbyte.cdk.integrations.destination.s3.avro.AvroConstants
import io.airbyte.cdk.integrations.destination.s3.avro.AvroRecordFactory
import io.airbyte.cdk.integrations.destination.s3.avro.JsonToAvroSchemaConverter
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.io.FileInputStream
import java.io.IOException
import java.io.InputStream
import java.nio.file.Files
import java.nio.file.Path
import java.util.UUID
import org.apache.avro.Schema
import org.apache.avro.generic.GenericData
import org.apache.commons.io.FileUtils
import org.apache.commons.lang3.StringUtils
import org.apache.hadoop.conf.Configuration
import org.apache.parquet.avro.AvroParquetWriter
import org.apache.parquet.avro.AvroWriteSupport
import org.apache.parquet.hadoop.ParquetWriter
import org.apache.parquet.hadoop.util.HadoopOutputFile

private val logger = KotlinLogging.logger {}

/**
 * The [io.airbyte.cdk.integrations.destination.record_buffer.BaseSerializedBuffer] class abstracts
 * the [io.airbyte.cdk.integrations.destination.record_buffer.BufferStorage] from the details of the
 * format the data is going to be stored in.
 *
 * Unfortunately, the Parquet library doesn't allow us to manipulate the output stream and forces us
 * to go through [HadoopOutputFile] instead. So we can't benefit from the abstraction described
 * above. Therefore, we re-implement the necessary methods to be used as [SerializableBuffer], while
 * data will be buffered in such a hadoop file.
 */
class ParquetSerializedBuffer(
    uploadFormatConfig: UploadFormatConfig,
    stream: AirbyteStreamNameNamespacePair,
    catalog: ConfiguredAirbyteCatalog
) : SerializableBuffer {
    private val avroRecordFactory: AvroRecordFactory
    private val parquetWriter: ParquetWriter<GenericData.Record>
    private val bufferFile: Path
    override var inputStream: InputStream? = null
    private var lastByteCount: Long
    private var isClosed: Boolean

    init {
        val schemaConverter = JsonToAvroSchemaConverter()
        val schema: Schema =
            schemaConverter.getAvroSchema(
                catalog.streams
                    .firstOrNull { s: ConfiguredAirbyteStream ->
                        (s.stream.name == stream.name) &&
                            StringUtils.equals(
                                s.stream.namespace,
                                stream.namespace,
                            )
                    }
                    ?.stream
                    ?.jsonSchema
                    ?: throw RuntimeException("No such stream ${stream.namespace}.${stream.name}"),
                stream.name,
                stream.namespace,
            )
        bufferFile = Files.createTempFile(UUID.randomUUID().toString(), ".parquet")
        Files.deleteIfExists(bufferFile)
        avroRecordFactory = AvroRecordFactory(schema, AvroConstants.JSON_CONVERTER)
        val uploadParquetFormatConfig: UploadParquetFormatConfig =
            uploadFormatConfig as UploadParquetFormatConfig
        val avroConfig = Configuration()
        avroConfig.setBoolean(AvroWriteSupport.WRITE_OLD_LIST_STRUCTURE, false)
        parquetWriter =
            AvroParquetWriter.builder<GenericData.Record>(
                    HadoopOutputFile.fromPath(
                        org.apache.hadoop.fs.Path(bufferFile.toUri()),
                        avroConfig
                    ),
                )
                .withConf(
                    avroConfig
                ) // yes, this should be here despite the fact we pass this config above in path
                .withSchema(schema)
                .withCompressionCodec(uploadParquetFormatConfig.compressionCodec)
                .withRowGroupSize(uploadParquetFormatConfig.blockSize.toLong())
                .withMaxPaddingSize(uploadParquetFormatConfig.maxPaddingSize)
                .withPageSize(uploadParquetFormatConfig.pageSize)
                .withDictionaryPageSize(uploadParquetFormatConfig.dictionaryPageSize)
                .withDictionaryEncoding(uploadParquetFormatConfig.isDictionaryEncoding)
                .build()
        isClosed = false
        lastByteCount = 0L
    }

    @Deprecated("Deprecated in Java")
    @Throws(Exception::class)
    override fun accept(record: AirbyteRecordMessage): Long {
        if (inputStream == null && !isClosed) {
            val startCount: Long = byteCount
            parquetWriter.write(avroRecordFactory.getAvroRecord(UUID.randomUUID(), record))
            return byteCount - startCount
        } else {
            throw IllegalCallerException("Buffer is already closed, it cannot accept more messages")
        }
    }

    @Throws(Exception::class)
    override fun accept(
        recordString: String,
        airbyteMetaString: String,
        generationId: Long,
        emittedAt: Long
    ): Long {
        throw UnsupportedOperationException(
            "This method is not supported for ParquetSerializedBuffer"
        )
    }

    @Throws(Exception::class)
    override fun flush() {
        if (inputStream == null && !isClosed) {
            byteCount
            parquetWriter.close()
            inputStream = FileInputStream(bufferFile.toFile())
            logger.info {
                "Finished writing data to ${filename} (${FileUtils.byteCountToDisplaySize(byteCount)})"
            }
        }
    }

    override val byteCount: Long
        get() {
            if (inputStream != null) {
                // once the parquetWriter is closed, we can't query how many bytes are in it, so we
                // cache the last
                // count
                return lastByteCount
            }
            lastByteCount = parquetWriter.dataSize
            return lastByteCount
        }

    override val filename: String
        @Throws(IOException::class)
        get() {
            return bufferFile.fileName.toString()
        }

    override val file: File
        @Throws(IOException::class)
        get() {
            return bufferFile.toFile()
        }

    override val maxTotalBufferSizeInBytes: Long = FileBuffer.MAX_TOTAL_BUFFER_SIZE_BYTES

    override val maxPerStreamBufferSizeInBytes: Long = FileBuffer.MAX_PER_STREAM_BUFFER_SIZE_BYTES

    override val maxConcurrentStreamsInBuffer: Int =
        FileBuffer.DEFAULT_MAX_CONCURRENT_STREAM_IN_BUFFER

    @Throws(Exception::class)
    override fun close() {
        if (!isClosed) {
            inputStream?.close()
            Files.deleteIfExists(bufferFile)
            isClosed = true
        }
    }

    companion object {
        @JvmStatic
        fun createFunction(s3DestinationConfig: S3DestinationConfig): BufferCreateFunction {
            return BufferCreateFunction {
                stream: AirbyteStreamNameNamespacePair,
                catalog: ConfiguredAirbyteCatalog ->
                ParquetSerializedBuffer(
                    s3DestinationConfig.formatConfig!!,
                    stream,
                    catalog,
                )
            }
        }
    }
}
