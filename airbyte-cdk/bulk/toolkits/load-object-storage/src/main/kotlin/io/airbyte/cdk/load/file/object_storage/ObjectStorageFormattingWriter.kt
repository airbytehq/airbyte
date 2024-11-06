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
import io.airbyte.cdk.load.data.avro.toAvroRecord
import io.airbyte.cdk.load.data.avro.toAvroSchema
import io.airbyte.cdk.load.data.csv.toCsvRecord
import io.airbyte.cdk.load.data.dataWithAirbyteMeta
import io.airbyte.cdk.load.data.json.toJson
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
        return when (formatConfigProvider.objectStorageFormatConfiguration) {
            is JsonFormatConfiguration -> JsonFormattingWriter(stream, outputStream)
            is AvroFormatConfiguration ->
                AvroFormattingWriter(
                    stream,
                    outputStream,
                    formatConfigProvider.objectStorageFormatConfiguration
                        as AvroFormatConfiguration,
                )
            is ParquetFormatConfiguration ->
                ParquetFormattingWriter(
                    stream,
                    outputStream,
                    formatConfigProvider.objectStorageFormatConfiguration
                        as ParquetFormatConfiguration,
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
        outputStream.write(record.dataWithAirbyteMeta(stream).toJson().serializeToString())
        outputStream.write("\n")
    }

    override fun close() {
        outputStream.close()
    }
}

class CSVFormattingWriter(
    private val stream: DestinationStream,
    outputStream: OutputStream,
) : ObjectStorageFormattingWriter {
    private val printer = stream.schema.withAirbyteMeta().toCsvPrinterWithHeader(outputStream)
    override fun accept(record: DestinationRecord) {
        printer.printRecord(*record.dataWithAirbyteMeta(stream).toCsvRecord())
    }
    override fun close() {
        printer.close()
    }
}

class AvroFormattingWriter(
    private val stream: DestinationStream,
    outputStream: OutputStream,
    formatConfig: AvroFormatConfiguration,
) : ObjectStorageFormattingWriter {
    private val avroSchema = stream.schema.withAirbyteMeta().toAvroSchema(stream.descriptor)
    private val writer =
        outputStream.toAvroWriter(avroSchema, formatConfig.avroCompressionConfiguration)
    override fun accept(record: DestinationRecord) {
        writer.write(record.dataWithAirbyteMeta(stream).toAvroRecord(avroSchema))
    }

    override fun close() {
        writer.close()
    }
}

class ParquetFormattingWriter(
    private val stream: DestinationStream,
    outputStream: OutputStream,
    formatConfig: ParquetFormatConfiguration,
) : ObjectStorageFormattingWriter {
    private val avroSchema = stream.schema.withAirbyteMeta().toAvroSchema(stream.descriptor)
    private val writer =
        outputStream.toParquetWriter(avroSchema, formatConfig.parquetWriterConfiguration)
    override fun accept(record: DestinationRecord) {
        writer.write(record.dataWithAirbyteMeta(stream).toAvroRecord(avroSchema))
    }

    override fun close() {
        writer.close()
    }
}
