/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.AvroFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.CSVFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.JsonFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ParquetFormatConfiguration
import io.airbyte.cdk.load.data.avro.AvroMapperPipelineFactory
import io.airbyte.cdk.load.data.avro.toAvroRecord
import io.airbyte.cdk.load.data.avro.toAvroSchema
import io.airbyte.cdk.load.data.csv.toCsvRecord
import io.airbyte.cdk.load.data.dataWithAirbyteMeta
import io.airbyte.cdk.load.data.json.toJson
import io.airbyte.cdk.load.data.parquet.ParquetMapperPipelineFactory
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.file.avro.toAvroWriter
import io.airbyte.cdk.load.file.csv.toCsvPrinterWithHeader
import io.airbyte.cdk.load.file.parquet.toParquetWriter
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.cdk.load.util.write
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.io.Closeable
import java.io.OutputStream

interface ObjectStorageFormattingWriter : Closeable {
    fun accept(record: DestinationRecord)
}

@Singleton
@Secondary
class ObjectStorageFormattingWriterFactory(
    private val formatConfigProvider: ObjectStorageFormatConfigurationProvider,
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
    override fun accept(record: DestinationRecord) {
        outputStream.write(
            record.dataWithAirbyteMeta(stream, rootLevelFlattening).toJson().serializeToString()
        )
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
    private val finalSchema = stream.schema.withAirbyteMeta(rootLevelFlattening)
    private val printer = finalSchema.toCsvPrinterWithHeader(outputStream)
    override fun accept(record: DestinationRecord) {
        printer.printRecord(
            *record.dataWithAirbyteMeta(stream, rootLevelFlattening).toCsvRecord(finalSchema)
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
    private val pipeline = AvroMapperPipelineFactory().create(stream)
    private val avroSchema =
        pipeline.finalSchema.withAirbyteMeta(rootLevelFlattening).toAvroSchema(stream.descriptor)
    private val writer =
        outputStream.toAvroWriter(avroSchema, formatConfig.avroCompressionConfiguration)
    override fun accept(record: DestinationRecord) {
        val dataMapped =
            pipeline
                .map(record.data, record.meta?.changes)
                .withAirbyteMeta(stream, record.emittedAtMs, rootLevelFlattening)
        writer.write(dataMapped.toAvroRecord(avroSchema))
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
    private val pipeline = ParquetMapperPipelineFactory().create(stream)
    private val avroSchema =
        pipeline.finalSchema.withAirbyteMeta(rootLevelFlattening).toAvroSchema(stream.descriptor)
    private val writer =
        outputStream.toParquetWriter(avroSchema, formatConfig.parquetWriterConfiguration)
    override fun accept(record: DestinationRecord) {
        val dataMapped =
            pipeline
                .map(record.data, record.meta?.changes)
                .withAirbyteMeta(stream, record.emittedAtMs, rootLevelFlattening)
        writer.write(dataMapped.toAvroRecord(avroSchema))
    }

    override fun close() {
        writer.close()
    }
}
