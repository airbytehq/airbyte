/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.bulk_loader

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.csv.toCsvHeader
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.file.csv.toCsvPrinterWithHeader
import io.airbyte.cdk.load.file.object_storage.ObjectStorageFormattingWriter
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import java.io.OutputStream

class ProtoToBigQueryObjectStorageFormattingWriter(
    stream: DestinationStream,
    outputStream: OutputStream,
) : ObjectStorageFormattingWriter {

    private val finalSchema = stream.schema.withAirbyteMeta(true)
    private val printer = finalSchema.toCsvPrinterWithHeader(outputStream)
    private val header: Array<String> = finalSchema.toCsvHeader()
    private val csvRowGenerator =
        ProtoToBigQueryCSVRowGenerator(
            header,
            stream,
            stream.airbyteValueProxyFieldAccessors,
        )

    override fun accept(record: DestinationRecordRaw) {
        val src = record.rawData
        require(src is DestinationRecordProtobufSource) {
            "ProtoToBigQueryObjectStorageFormattingWriter only supports DestinationRecordProtobufSource"
        }

        printer.printRecord(*csvRowGenerator.generate(record))
    }

    override fun flush() {
        printer.flush()
    }

    override fun close() {
        printer.close()
    }
}
