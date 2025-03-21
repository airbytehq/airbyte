/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.csv.toCsvRecord
import io.airbyte.cdk.load.data.dataWithAirbyteMeta
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.file.csv.toCsvPrinterWithHeader
import io.airbyte.cdk.load.file.object_storage.ObjectStorageFormattingWriter
import io.airbyte.cdk.load.file.object_storage.ObjectStorageFormattingWriterFactory
import io.airbyte.cdk.load.message.DestinationRecordRaw
import java.io.OutputStream
import javax.inject.Singleton

class MSSQLCSVFormattingWriter(
    private val stream: DestinationStream,
    outputStream: OutputStream,
    validateValuesPreLoad: Boolean,
) : ObjectStorageFormattingWriter {
    private val finalSchema = stream.schema.withAirbyteMeta(true)
    private val printer = finalSchema.toCsvPrinterWithHeader(outputStream)
    private val mssqlRowGenerator = MSSQLCsvRowGenerator(validateValuesPreLoad)
    override fun accept(record: DestinationRecordRaw) {
        printer.printRecord(
            mssqlRowGenerator
                .generate(record, this.finalSchema)
                .dataWithAirbyteMeta(stream, true)
                .toCsvRecord(finalSchema),
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
class MssqlObjectStorageFormattingWriterFactory(val validateValuesPreLoad: Boolean) :
    ObjectStorageFormattingWriterFactory {
    override fun create(
        stream: DestinationStream,
        outputStream: OutputStream
    ): ObjectStorageFormattingWriter {
        return MSSQLCSVFormattingWriter(
            stream,
            outputStream,
            validateValuesPreLoad,
        )
    }
}
