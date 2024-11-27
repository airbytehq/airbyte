/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.AvroFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.CSVFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.JsonFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ParquetFormatConfiguration
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.avro.AvroMapperPipelineFactory
import io.airbyte.cdk.load.data.avro.toAvroRecord
import io.airbyte.cdk.load.data.avro.toAvroSchema
import io.airbyte.cdk.load.data.csv.toCsvRecord
import io.airbyte.cdk.load.data.dataWithAirbyteMeta
import io.airbyte.cdk.load.data.json.toJson
import io.airbyte.cdk.load.data.parquet.ParquetMapperPipelineFactory
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.file.StreamProcessor
import io.airbyte.cdk.load.file.avro.toAvroWriter
import io.airbyte.cdk.load.file.csv.toCsvPrinterWithHeader
import io.airbyte.cdk.load.file.parquet.ParquetWriter
import io.airbyte.cdk.load.file.parquet.toParquetWriter
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.cdk.load.util.write
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream
import java.io.Closeable
import java.io.OutputStream
import java.util.concurrent.atomic.AtomicLong
import org.apache.avro.Schema

interface ObjectStorageFormattingWriter : Closeable {
    val numCapturedChanges: AtomicLong

    fun accept(record: DestinationRecord)
}

@Singleton
@Secondary
class ObjectStorageFormattingWriterFactory(
    private val formatConfigProvider: ObjectStorageFormatConfigurationProvider,
    private val compressionConfigurationProvider: ObjectStorageCompressionConfigurationProvider<*>,
    private val uploadConfigProvider: ObjectStorageUploadConfigurationProvider
) {
    fun create(
        stream: DestinationStream,
        outputStream: OutputStream
    ): ObjectStorageFormattingWriter {
        val flatten = formatConfigProvider.objectStorageFormatConfiguration.rootLevelFlattening
        return when (formatConfigProvider.objectStorageFormatConfiguration) {
            is JsonFormatConfiguration -> JsonFormattingWriter(stream, outputStream, flatten)
            is AvroFormatConfiguration ->
                AvroFormattingWriter(
                    stream,
                    outputStream,
                    formatConfigProvider.objectStorageFormatConfiguration
                        as AvroFormatConfiguration,
                    flatten
                )
            is ParquetFormatConfiguration ->
                ParquetFormattingWriter(
                    stream,
                    outputStream,
                    formatConfigProvider.objectStorageFormatConfiguration
                        as ParquetFormatConfiguration,
                    flatten
                )
            is CSVFormatConfiguration -> CSVFormattingWriter(stream, outputStream, flatten)
        }
    }
}

class JsonFormattingWriter(
    private val stream: DestinationStream,
    private val outputStream: OutputStream,
    private val rootLevelFlattening: Boolean,
) : ObjectStorageFormattingWriter {
    override val numCapturedChanges: AtomicLong = AtomicLong(0)

    override fun accept(record: DestinationRecord) {
        val data =
            record.dataWithAirbyteMeta(stream, rootLevelFlattening).toJson().serializeToString()
        outputStream.write(data)
        outputStream.write("\n")
    }

    override fun close() {
        outputStream.close()
    }
}

class CSVFormattingWriter(
    private val stream: DestinationStream,
    outputStream: OutputStream,
    private val rootLevelFlattening: Boolean
) : ObjectStorageFormattingWriter {
    override val numCapturedChanges: AtomicLong = AtomicLong(0)

    private val finalSchema = stream.schema.withAirbyteMeta(rootLevelFlattening)
    private val printer = finalSchema.toCsvPrinterWithHeader(outputStream)
    override fun accept(record: DestinationRecord) {
        printer.printRecord(
            record.dataWithAirbyteMeta(stream, rootLevelFlattening).toCsvRecord(finalSchema)
        )
    }

    override fun close() {
        printer.close()
    }
}

class AvroFormattingWriter(
    private val stream: DestinationStream,
    outputStream: OutputStream,
    formatConfig: AvroFormatConfiguration,
    private val rootLevelFlattening: Boolean,
) : ObjectStorageFormattingWriter {
    val log = KotlinLogging.logger {}
    override val numCapturedChanges: AtomicLong = AtomicLong(0)

    private val pipeline = AvroMapperPipelineFactory().create(stream)
    private val mappedSchema = pipeline.finalSchema.withAirbyteMeta(rootLevelFlattening)
    private val avroSchema = mappedSchema.toAvroSchema(stream.descriptor)
    private val writer =
        outputStream.toAvroWriter(avroSchema, formatConfig.avroCompressionConfiguration)

    init {
        log.info { "Generated avro schema: $avroSchema" }
    }

    override fun accept(record: DestinationRecord) {
        val dataMapped = pipeline.map(record.data, record.meta?.changes)
        numCapturedChanges.addAndGet(dataMapped.second.size.toLong())
        val withMeta = dataMapped.withAirbyteMeta(stream, record.emittedAtMs, rootLevelFlattening)
        writer.write(withMeta.toAvroRecord(mappedSchema, avroSchema))
    }

    override fun close() {
        writer.close()
    }
}

class ParquetFormattingWriter(
    private val stream: DestinationStream,
    outputStream: OutputStream,
    formatConfig: ParquetFormatConfiguration,
    private val rootLevelFlattening: Boolean,
) : ObjectStorageFormattingWriter {
    private val log = KotlinLogging.logger {}
    override val numCapturedChanges: AtomicLong = AtomicLong(0)

    private val pipeline = ParquetMapperPipelineFactory().create(stream)
    private val mappedSchema: ObjectType = pipeline.finalSchema.withAirbyteMeta(rootLevelFlattening)
    private val avroSchema: Schema = mappedSchema.toAvroSchema(stream.descriptor)
    private val writer: ParquetWriter =
        outputStream.toParquetWriter(avroSchema, formatConfig.parquetWriterConfiguration)

    init {
        log.info { "Generated avro schema: $avroSchema" }
    }

    override fun accept(record: DestinationRecord) {
        val dataMapped = pipeline.map(record.data, record.meta?.changes)
        numCapturedChanges.addAndGet(dataMapped.second.size.toLong())
        val withMeta = dataMapped.withAirbyteMeta(stream, record.emittedAtMs, rootLevelFlattening)
        writer.write(withMeta.toAvroRecord(mappedSchema, avroSchema))
    }

    override fun close() {
        writer.close()
    }
}

@Singleton
@Secondary
class BufferedFormattingWriterFactory<T : OutputStream>(
    private val writerFactory: ObjectStorageFormattingWriterFactory,
    private val formatConfigProvider: ObjectStorageFormatConfigurationProvider,
    private val compressionConfigurationProvider: ObjectStorageCompressionConfigurationProvider<T>,
    private val uploadConfigProvider: ObjectStorageUploadConfigurationProvider
) {
    fun create(stream: DestinationStream): BufferedFormattingWriter<T> {
        val outputStream = ByteArrayOutputStream()
        val processor =
            compressionConfigurationProvider.objectStorageCompressionConfiguration.compressor
        val wrappingBuffer = processor.wrapper.invoke(outputStream)
        val writer = writerFactory.create(stream, wrappingBuffer)
        return BufferedFormattingWriter(
            writer,
            uploadConfigProvider.objectStorageUploadConfiguration.streamingUploadPartSize,
            outputStream,
            processor,
            wrappingBuffer
        )
    }
}

class BufferedFormattingWriter<T : OutputStream>(
    private val writer: ObjectStorageFormattingWriter,
    private val partSize: Long,
    private val buffer: ByteArrayOutputStream,
    private val streamProcessor: StreamProcessor<T>,
    private val wrappingBuffer: T
) : ObjectStorageFormattingWriter {
    override val numCapturedChanges: AtomicLong = writer.numCapturedChanges

    override fun accept(record: DestinationRecord) {
        writer.accept(record)
    }

    fun isDataSufficient(): Boolean {
        return buffer.size() >= partSize
    }

    fun takeBytes(): ByteArray {
        wrappingBuffer.flush()
        val bytes = buffer.toByteArray()
        buffer.reset()
        return bytes
    }

    fun finish(): ByteArray? {
        writer.close()
        streamProcessor.partFinisher.invoke(wrappingBuffer)
        return if (buffer.size() > 0) {
            buffer.toByteArray()
        } else {
            null
        }
    }

    override fun close() {
        writer.close()
    }
}
