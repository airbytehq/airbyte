/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.bulk_loader

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.data.csv.toCsvRecord
import io.airbyte.cdk.load.data.dataWithAirbyteMeta
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.file.csv.toCsvPrinterWithHeader
import io.airbyte.cdk.load.file.object_storage.ObjectStorageFormattingWriter
import io.airbyte.cdk.load.file.object_storage.ObjectStorageFormattingWriterFactory
import io.airbyte.cdk.load.message.DestinationRecordRaw
import jakarta.inject.Singleton
import java.io.OutputStream

class BigQueryObjectStorageFormattingWriter(
    private val stream: DestinationStream,
    outputStream: OutputStream,
    private val rootLevelFlattening: Boolean
) : ObjectStorageFormattingWriter {

    private val finalSchema = stream.schema.withAirbyteMeta(rootLevelFlattening)
    private val printer = finalSchema.toCsvPrinterWithHeader(outputStream)

    override fun accept(record: DestinationRecordRaw) {
        record.rawData.record.emittedAt *= 1000

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

@Singleton
class BigQueryObjectStorageFormattingWriterFactory(
    private val formatConfigProvider: ObjectStorageFormatConfigurationProvider,
) : ObjectStorageFormattingWriterFactory {
    override fun create(
        stream: DestinationStream,
        outputStream: OutputStream
    ): ObjectStorageFormattingWriter {
        val flatten = formatConfigProvider.objectStorageFormatConfiguration.rootLevelFlattening
        return BigQueryObjectStorageFormattingWriter(stream, outputStream, flatten)
    }
}
