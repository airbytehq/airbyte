/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.bulk_loader

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.file.object_storage.CSVFormattingWriter
import io.airbyte.cdk.load.file.object_storage.ObjectStorageFormattingWriter
import io.airbyte.cdk.load.file.object_storage.ObjectStorageFormattingWriterFactory
import io.airbyte.cdk.load.message.DestinationRecordRaw
import jakarta.inject.Singleton
import java.io.OutputStream

class BigQueryObjectStorageFormattingWriter(
    private val csvFormattingWriter: CSVFormattingWriter,
) : ObjectStorageFormattingWriter by csvFormattingWriter {

    override fun accept(record: DestinationRecordRaw) {
        csvFormattingWriter.accept(record)
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
        return BigQueryObjectStorageFormattingWriter(
            CSVFormattingWriter(
                stream,
                outputStream,
                rootLevelFlattening = flatten,
                extractedAtAsTimestampWithTimezone = true,
            ),
        )
    }
}
