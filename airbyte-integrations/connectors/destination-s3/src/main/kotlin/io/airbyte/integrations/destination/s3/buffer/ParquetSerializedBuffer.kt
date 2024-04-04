package io.airbyte.integrations.destination.s3.buffer

import io.airbyte.cdk.integrations.destination.record_buffer.FileBuffer
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.cdk.integrations.destination.s3.avro.AvroConstants
import io.airbyte.cdk.integrations.destination.s3.avro.AvroRecordFactory
import io.airbyte.cdk.integrations.destination.s3.parquet.ParquetSerializedBuffer
import io.airbyte.cdk.integrations.destination.s3.parquet.S3ParquetConstants
import io.airbyte.integrations.destination.s3.config.properties.S3ConnectorOutputFormat
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import org.apache.avro.Schema
import org.apache.avro.generic.GenericData
import org.apache.commons.io.FileUtils
import org.apache.hadoop.conf.Configuration
import org.apache.parquet.avro.AvroParquetWriter
import org.apache.parquet.avro.AvroWriteSupport
import org.apache.parquet.hadoop.ParquetWriter
import org.apache.parquet.hadoop.metadata.CompressionCodecName
import org.apache.parquet.hadoop.util.HadoopOutputFile
import java.io.File
import java.io.FileInputStream
import java.io.IOException
import java.io.InputStream
import java.nio.file.Files
import java.nio.file.Path
import java.util.UUID

private val logger = KotlinLogging.logger {}

class ParquetSerializedBuffer: SerializableBuffer {

    private var avroRecordFactory: AvroRecordFactory? = null
    private var parquetWriter: ParquetWriter<GenericData.Record>? = null
    private var bufferFile: Path? = null
    private var inputStream: InputStream? = null
    private var lastByteCount: Long? = null
    private var isClosed = false

    @Throws(IOException::class)
    constructor(
        formatConfig: S3ConnectorOutputFormat,
        schema: Schema
    ) {
        bufferFile = Files.createTempFile(UUID.randomUUID().toString(), ".parquet")
        Files.deleteIfExists(bufferFile)
        avroRecordFactory = AvroRecordFactory(schema, AvroConstants.JSON_CONVERTER)
        val avroConfig = Configuration()

        val blockSizeMb = formatConfig.blockSizeMb ?: S3ParquetConstants.DEFAULT_BLOCK_SIZE_MB
        val compressionCodec = formatConfig.compressionCodec?.codec ?: S3ParquetConstants.DEFAULT_COMPRESSION_CODEC.name
        val maxPaddingSize = formatConfig.maxPaddingSizeMb ?: S3ParquetConstants.DEFAULT_MAX_PADDING_SIZE_MB
        val pageSize = formatConfig.pageSizeKb ?: S3ParquetConstants.DEFAULT_PAGE_SIZE_KB
        val dictionaryPageSize = formatConfig.dictionaryPageSizeKb ?: S3ParquetConstants.DEFAULT_DICTIONARY_PAGE_SIZE_KB
        val isDictionaryEncoding = formatConfig.dictionaryEncoding ?: S3ParquetConstants.DEFAULT_DICTIONARY_ENCODING

        avroConfig.setBoolean(AvroWriteSupport.WRITE_OLD_LIST_STRUCTURE, false)
        parquetWriter = AvroParquetWriter.builder<GenericData.Record>(
            HadoopOutputFile
                .fromPath(org.apache.hadoop.fs.Path(bufferFile?.toUri()), avroConfig)
        )
            .withConf(avroConfig) // yes, this should be here despite the fact we pass this config above in path
            .withSchema(schema)
            .withCompressionCodec(CompressionCodecName.valueOf(compressionCodec))
            .withRowGroupSize(blockSizeMb)
            .withMaxPaddingSize(maxPaddingSize)
            .withPageSize(pageSize)
            .withDictionaryPageSize(dictionaryPageSize)
            .withDictionaryEncoding(isDictionaryEncoding)
            .build()
        inputStream = null
        isClosed = false
        lastByteCount = 0L
    }

    @Throws(Exception::class)
    override fun accept(record: AirbyteRecordMessage?): Long {
        if (inputStream == null && !isClosed) {
            val startCount = byteCount
            parquetWriter!!.write(avroRecordFactory!!.getAvroRecord(UUID.randomUUID(), record))
            return byteCount - startCount
        } else {
            throw IllegalCallerException("Buffer is already closed, it cannot accept more messages")
        }
    }

    @Throws(Exception::class)
    override fun accept(recordString: String?, emittedAt: Long): Long {
        throw UnsupportedOperationException("This method is not supported for ParquetSerializedBuffer")
    }

    @Throws(Exception::class)
    override fun flush() {
        if (inputStream == null && !isClosed) {
            byteCount
            parquetWriter!!.close()
            inputStream = FileInputStream(bufferFile!!.toFile())
            logger.info { "Finished writing data to $filename (${FileUtils.byteCountToDisplaySize(byteCount)})" }
        }
    }

    override fun getByteCount(): Long {
        if (inputStream != null) {
            // once the parquetWriter is closed, we can't query how many bytes are in it, so we cache the last
            // count
            return lastByteCount!!
        }
        lastByteCount = parquetWriter!!.dataSize
        return lastByteCount!!
    }

    @Throws(IOException::class)
    override fun getFilename(): String {
        return bufferFile!!.fileName.toString()
    }

    @Throws(IOException::class)
    override fun getFile(): File {
        return bufferFile!!.toFile()
    }

    override fun getInputStream(): InputStream? {
        return inputStream
    }

    override fun getMaxTotalBufferSizeInBytes(): Long {
        return FileBuffer.MAX_TOTAL_BUFFER_SIZE_BYTES
    }

    override fun getMaxPerStreamBufferSizeInBytes(): Long {
        return FileBuffer.MAX_PER_STREAM_BUFFER_SIZE_BYTES
    }

    override fun getMaxConcurrentStreamsInBuffer(): Int {
        return FileBuffer.DEFAULT_MAX_CONCURRENT_STREAM_IN_BUFFER
    }

    @Throws(Exception::class)
    override fun close() {
        if (!isClosed) {
            inputStream?.close()
            bufferFile?.let { Files.deleteIfExists(it) }
            isClosed = true
        }
    }
}