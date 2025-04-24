/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.parquet

import java.io.Closeable
import java.io.OutputStream
import org.apache.avro.Schema
import org.apache.avro.generic.GenericRecord
import org.apache.hadoop.conf.Configuration
import org.apache.parquet.avro.AvroParquetWriter
import org.apache.parquet.avro.AvroWriteSupport.WRITE_OLD_LIST_STRUCTURE
import org.apache.parquet.hadoop.ParquetWriter as ApacheParquetWriter
import org.apache.parquet.hadoop.metadata.CompressionCodecName
import org.apache.parquet.io.OutputFile
import org.apache.parquet.io.PositionOutputStream

class ParquetWriter(private val writer: ApacheParquetWriter<GenericRecord>) : Closeable {
    fun write(record: GenericRecord) = writer.write(record)
    override fun close() = writer.close()
}

fun OutputStream.toParquetWriter(
    avroSchema: Schema,
    config: ParquetWriterConfiguration
): ParquetWriter {
    // Custom OutputFile implementation wrapping the OutputStream
    val outputFile =
        object : OutputFile {
            var position: Long = 0
            override fun create(blockSizeHint: Long) =
                object : PositionOutputStream() {
                    override fun write(b: Int) {
                        position += 1
                        this@toParquetWriter.write(b)
                    }
                    override fun write(bytes: ByteArray, off: Int, len: Int) {
                        position += len
                        this@toParquetWriter.write(bytes, off, len)
                    }
                    override fun flush() = this@toParquetWriter.flush()
                    override fun close() = this@toParquetWriter.close()
                    override fun getPos() = position
                }

            override fun createOrOverwrite(blockSizeHint: Long) = create(blockSizeHint)
            override fun supportsBlockSize() = true
            override fun defaultBlockSize() = 0L
        }

    // Initialize AvroParquetWriter with the custom OutputFile
    val writer =
        AvroParquetWriter.builder<GenericRecord>(outputFile)
            .withSchema(avroSchema)
            // needed so that we can have arrays containing null elements
            .withConf(Configuration().apply { setBoolean(WRITE_OLD_LIST_STRUCTURE, false) })
            .withCompressionCodec(config.compressionCodec)
            .withRowGroupSize(config.blockSizeMb * 1024 * 1024L)
            .withPageSize(config.pageSizeKb * 1024)
            .withDictionaryPageSize(config.dictionaryPageSizeKb * 1024)
            .withDictionaryEncoding(config.dictionaryEncoding)
            .withMaxPaddingSize(config.maxPaddingSizeMb * 1024 * 1024)
            .withRowGroupSize(5 * 1024L * 1024L)
            .build()

    return ParquetWriter(writer)
}

data class ParquetWriterConfiguration(
    val compressionCodecName: String,
    val blockSizeMb: Int,
    val maxPaddingSizeMb: Int,
    val pageSizeKb: Int,
    val dictionaryPageSizeKb: Int,
    val dictionaryEncoding: Boolean
) {
    val compressionCodec
        get() = CompressionCodecName.valueOf(compressionCodecName)
}

interface ParquetWriterConfigurationProvider {
    val parquetWriterConfiguration: ParquetWriterConfiguration
}
