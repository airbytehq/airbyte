/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.object_storage

import com.fasterxml.jackson.core.util.MinimalPrettyPrinter
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.SequenceWriter
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.AvroFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.CSVFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.JsonFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ParquetFormatConfiguration
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.avro.toAvroRecord
import io.airbyte.cdk.load.data.avro.toAvroSchema
import io.airbyte.cdk.load.data.csv.toCsvRecord
import io.airbyte.cdk.load.data.dataWithAirbyteMeta
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.file.StreamProcessor
import io.airbyte.cdk.load.file.avro.toAvroWriter
import io.airbyte.cdk.load.file.csv.toCsvPrinterWithHeader
import io.airbyte.cdk.load.file.parquet.ParquetWriter
import io.airbyte.cdk.load.file.parquet.toParquetWriter
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.pipeline.ProtoDataType
import io.airbyte.cdk.load.pipeline.ProtoMapper
import io.airbyte.cdk.load.util.FastUUIDGenerator
import io.airbyte.cdk.load.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream
import java.io.Closeable
import java.io.OutputStream
import java.io.UnsupportedEncodingException
import java.util.*
import java.util.concurrent.atomic.AtomicLong
import org.apache.avro.Schema

interface ObjectStorageFormattingWriter : Closeable {
    fun accept(record: DestinationRecordRaw)
    fun flush()
}

interface ObjectStorageFormattingWriterFactory {
    fun create(stream: DestinationStream, outputStream: OutputStream): ObjectStorageFormattingWriter
}

@Singleton
@Secondary
class DefaultObjectStorageFormattingWriterFactory(
    private val formatConfigProvider: ObjectStorageFormatConfigurationProvider,
    private val protoMapper: ProtoMapper,
    private val config: DestinationConfiguration,
) : ObjectStorageFormattingWriterFactory {
    override fun create(
        stream: DestinationStream,
        outputStream: OutputStream
    ): ObjectStorageFormattingWriter {
        val flatten = formatConfigProvider.objectStorageFormatConfiguration.rootLevelFlattening
        // TODO: FileWriter

        return when (formatConfigProvider.objectStorageFormatConfiguration) {
            is JsonFormatConfiguration -> JsonFormattingWriter(
                stream,
                outputStream,
                flatten,
                protoMapper,
                disableUUID = config.disableUUID,
            )
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
    private val protoMapper: ProtoMapper,
    private val disableUUID: Boolean,
) : ObjectStorageFormattingWriter {
    private val generator =
        Jsons.createGenerator(outputStream)
    private val writer =
        Jsons.writerFor(JsonNode::class.java)
            .with(MinimalPrettyPrinter(System.lineSeparator()))
            .writeValues(outputStream)

    val oneVerySecureUUID = UUID.randomUUID().toString()
    val fastUUIDGenerator = FastUUIDGenerator()

    override fun accept(record: DestinationRecordRaw) {
        if (record.protoData.isEmpty()) {
            throw UnsupportedEncodingException("We done temporarily disabled everything but proto y'all")
        }

        generator.writeStartObject()
        generator.writeFieldName(Meta.COLUMN_NAME_AB_RAW_ID)
        if (disableUUID) {
            generator.writeString(oneVerySecureUUID)
        } else {
            generator.writeString(fastUUIDGenerator.insecureUUID())
        }
        generator.writeFieldName(Meta.COLUMN_NAME_AB_EXTRACTED_AT)
        generator.writeNumber(record.emittedAtMs)
        generator.writeFieldName(Meta.COLUMN_NAME_AB_GENERATION_ID)
        generator.writeNumber(stream.generationId)
        generator.writeFieldName(Meta.COLUMN_NAME_DATA)
        generator.writeStartObject()
        val schema = protoMapper.finalSchema
        for (i in schema.indices) {
            generator.writeFieldName(schema[i].first)
            when (schema[i].second) {
                ProtoDataType.STRING -> generator.writeString(record.protoData[i].string)
                ProtoDataType.BOOLEAN -> generator.writeBoolean(record.protoData[i].boolean)
                ProtoDataType.INTEGER -> generator.writeNumber(record.protoData[i].integer)
                ProtoDataType.NUMBER -> generator.writeNumber(record.protoData[i].number)
                ProtoDataType.BINARY -> generator.writeBinary(
                    record.protoData[i].binary.asReadOnlyByteBuffer().array()
                )
            }
        }
        generator.writeEndObject()
        generator.writeEndObject()
        generator.writeRaw(System.lineSeparator())
    }

    override fun flush() {
        outputStream.flush()
    }

    override fun close() {
        writer.close()
        outputStream.close()
    }
}

class CSVFormattingWriter(
    private val stream: DestinationStream,
    outputStream: OutputStream,
    private val rootLevelFlattening: Boolean
) : ObjectStorageFormattingWriter {

    private val finalSchema = stream.schema.withAirbyteMeta(rootLevelFlattening)
    private val printer = finalSchema.toCsvPrinterWithHeader(outputStream)
    override fun accept(record: DestinationRecordRaw) {
        printer.printRecord(
            record
                .asDestinationRecordAirbyteValue()
                .dataWithAirbyteMeta(stream, rootLevelFlattening)
                .toCsvRecord(finalSchema)
        )
    }

    override fun flush() {
        printer.flush()
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

    @Suppress("DEPRECATION")
    private val pipeline = io.airbyte.cdk.load.data.avro.AvroMapperPipelineFactory().create(stream)
    private val mappedSchema = pipeline.finalSchema.withAirbyteMeta(rootLevelFlattening)
    private val avroSchema = mappedSchema.toAvroSchema(stream.descriptor)
    private val writer =
        outputStream.toAvroWriter(avroSchema, formatConfig.avroCompressionConfiguration)

    init {
        log.info { "Generated avro schema: $avroSchema" }
    }

    override fun accept(record: DestinationRecordRaw) {
        val marshalledRecord = record.asDestinationRecordAirbyteValue()
        val dataMapped = pipeline.map(marshalledRecord.data, marshalledRecord.meta?.changes)
        val withMeta =
            dataMapped.withAirbyteMeta(stream, marshalledRecord.emittedAtMs, rootLevelFlattening)
        writer.write(withMeta.toAvroRecord(mappedSchema, avroSchema))
    }

    override fun flush() {
        writer.flush()
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

    @Suppress("DEPRECATION")
    private val pipeline =
        io.airbyte.cdk.load.data.parquet.ParquetMapperPipelineTest().create(stream)
    private val mappedSchema: ObjectType = pipeline.finalSchema.withAirbyteMeta(rootLevelFlattening)
    private val avroSchema: Schema = mappedSchema.toAvroSchema(stream.descriptor)
    private val writer: ParquetWriter =
        outputStream.toParquetWriter(avroSchema, formatConfig.parquetWriterConfiguration)

    init {
        log.info { "Generated avro schema: $avroSchema" }
    }

    override fun accept(record: DestinationRecordRaw) {
        val marshalledRecord = record.asDestinationRecordAirbyteValue()
        val dataMapped = pipeline.map(marshalledRecord.data, marshalledRecord.meta?.changes)
        val withMeta =
            dataMapped.withAirbyteMeta(stream, marshalledRecord.emittedAtMs, rootLevelFlattening)
        writer.write(withMeta.toAvroRecord(mappedSchema, avroSchema))
    }

    override fun flush() {
        // Parquet writer does not support flushing
    }

    override fun close() {
        writer.close()
    }
}

@Singleton
@Secondary
class BufferedFormattingWriterFactory<T : OutputStream>(
    private val writerFactory: ObjectStorageFormattingWriterFactory,
    private val compressionConfigurationProvider: ObjectStorageCompressionConfigurationProvider<T>,
) {
    fun create(stream: DestinationStream): BufferedFormattingWriter<T> {
        val outputStream = ByteArrayOutputStream()
        val processor =
            compressionConfigurationProvider.objectStorageCompressionConfiguration.compressor
        val wrappingBuffer = processor.wrapper.invoke(outputStream)
        val writer = writerFactory.create(stream, wrappingBuffer)
        return BufferedFormattingWriter(writer, outputStream, processor, wrappingBuffer)
    }
}

class BufferedFormattingWriter<T : OutputStream>(
    private val writer: ObjectStorageFormattingWriter,
    private val buffer: ByteArrayOutputStream,
    private val streamProcessor: StreamProcessor<T>,
    private val wrappingBuffer: T
) : ObjectStorageFormattingWriter {
    // An empty buffer is not a guarantee of a non-empty
    // file, some writers (parquet) start with a
    // header. Avoid writing empty files by requiring
    // both 0 bytes AND 0 rows.
    private val rowsAdded = AtomicLong(0)
    val bufferSize: Int
        get() =
            if (rowsAdded.get() == 0L) {
                0
            } else buffer.size()

    override fun accept(record: DestinationRecordRaw) {
        writer.accept(record)
        rowsAdded.incrementAndGet()
    }

    fun takeBytes(): ByteArray? {
        wrappingBuffer.flush()
        if (bufferSize == 0) {
            return null
        }

        val bytes = buffer.toByteArray()
        buffer.reset()
        return bytes
    }

    fun finish(): ByteArray? {
        writer.flush()
        writer.close()
        streamProcessor.partFinisher.invoke(wrappingBuffer)
        return if (bufferSize > 0) {
            buffer.toByteArray()
        } else {
            null
        }
    }

    override fun flush() {
        writer.flush()
        wrappingBuffer.flush()
    }

    override fun close() {
        writer.close()
    }
}
