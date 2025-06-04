/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.bulk_loader

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.file.csv.toCsvPrinterWithHeader
import io.airbyte.cdk.load.file.object_storage.CSVFormattingWriter
import io.airbyte.cdk.load.file.object_storage.ObjectStorageFormattingWriter
import io.airbyte.cdk.load.file.object_storage.ObjectStorageFormattingWriterFactory
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import jakarta.inject.Singleton
import java.io.OutputStream

class BigQueryObjectStorageFormattingWriter(
    stream: DestinationStream,
    outputStream: OutputStream,
) : ObjectStorageFormattingWriter {
    private val finalSchema = stream.schema.withAirbyteMeta(true)
    private val printer = finalSchema.toCsvPrinterWithHeader(outputStream)
    private val bigQueryRowGenerator = BigQueryCSVRowGenerator()

    override fun accept(record: DestinationRecordRaw) {
        printer.printRecord(bigQueryRowGenerator.generate(record, finalSchema))
    }

    override fun flush() {
        printer.flush()
    }

    override fun close() {
        printer.close()
    }
}

@Singleton
class BigQueryObjectStorageFormattingWriterFactory(private val config: BigqueryConfiguration) :
    ObjectStorageFormattingWriterFactory {
    override fun create(
        stream: DestinationStream,
        outputStream: OutputStream,
    ): ObjectStorageFormattingWriter {
        return if (config.legacyRawTablesOnly) {
            CSVFormattingWriter(
                stream,
                outputStream,
                rootLevelFlattening = false,
                extractedAtAsTimestampWithTimezone = true,
            )
        } else {
            BigQueryObjectStorageFormattingWriter(stream, outputStream)
        }
    }
}
