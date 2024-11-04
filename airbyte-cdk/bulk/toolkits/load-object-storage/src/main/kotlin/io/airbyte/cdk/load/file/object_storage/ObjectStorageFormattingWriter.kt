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
    private val avroMapperPipelineFactory: AvroMapperPipelineFactory,
    private val parquetMapperPipelineFactory: ParquetMapperPipelineFactory
) {
    fun create(
        stream: DestinationStream,
        outputStream: OutputStream
    ): ObjectStorageFormattingWriter {
        return when (formatConfigProvider.objectStorageFormatConfiguration) {
            is JsonFormatConfiguration -> JsonFormattingWriter(stream, outputStream)
            is AvroFormatConfiguration ->
                AvroFormattingWriter(
                    stream,
                    outputStream,
                    formatConfigProvider.objectStorageFormatConfiguration
                        as AvroFormatConfiguration,
                    avroMapperPipelineFactory
                )
            is ParquetFormatConfiguration ->
                ParquetFormattingWriter(
                    stream,
                    outputStream,
                    formatConfigProvider.objectStorageFormatConfiguration
                        as ParquetFormatConfiguration,
                    parquetMapperPipelineFactory
                )
            is CSVFormatConfiguration -> CSVFormattingWriter(stream, outputStream)
        }
    }
}

class JsonFormattingWriter(
    private val stream: DestinationStream,
    private val outputStream: OutputStream,
) : ObjectStorageFormattingWriter {
    override fun accept(record: DestinationRecord) {
        outputStream.write(record.data.withAirbyteMeta(stream, record).toJson().serializeToString())
        outputStream.write("\n")
    }

    override fun close() {
        outputStream.close()
    }
}

class CSVFormattingWriter(
    val stream: DestinationStream,
    outputStream: OutputStream,
) : ObjectStorageFormattingWriter {
    private val printer = stream.schema.withAirbyteMeta().toCsvPrinterWithHeader(outputStream)
    override fun accept(record: DestinationRecord) {
        printer.printRecord(*record.data.withAirbyteMeta(stream, record).toCsvRecord())
    }
    override fun close() {
        printer.close()
    }
}

class AvroFormattingWriter(
    val stream: DestinationStream,
    outputStream: OutputStream,
    formatConfig: AvroFormatConfiguration,
    mapperPipelineFactory: AvroMapperPipelineFactory
) : ObjectStorageFormattingWriter {
    private val mapperPipeline = mapperPipelineFactory.create(stream)
    private val avroSchema =
        mapperPipeline.finalSchema.withAirbyteMeta().toAvroSchema(stream.descriptor)

    private val writer =
        outputStream.toAvroWriter(avroSchema, formatConfig.avroCompressionConfiguration)

    override fun accept(record: DestinationRecord) {
        val recordMangled = mapperPipeline.map(record)
        writer.write(recordMangled.data.withAirbyteMeta(stream, record).toAvroRecord(avroSchema))
    }

    override fun close() {
        writer.close()
    }
}

class ParquetFormattingWriter(
    val stream: DestinationStream,
    outputStream: OutputStream,
    formatConfig: ParquetFormatConfiguration,
    mapperPipelineFactory: ParquetMapperPipelineFactory
) : ObjectStorageFormattingWriter {
    private val mapperPipeline = mapperPipelineFactory.create(stream)
    private val avroSchema =
        mapperPipeline.finalSchema.withAirbyteMeta().toAvroSchema(stream.descriptor)

    private val writer =
        outputStream.toParquetWriter(avroSchema, formatConfig.parquetWriterConfiguration)
    override fun accept(record: DestinationRecord) {
        val recordMangled = mapperPipeline.map(record)
        writer.write(recordMangled.data.withAirbyteMeta(stream, record).toAvroRecord(avroSchema))
    }

    override fun close() {
        writer.close()
    }
}
