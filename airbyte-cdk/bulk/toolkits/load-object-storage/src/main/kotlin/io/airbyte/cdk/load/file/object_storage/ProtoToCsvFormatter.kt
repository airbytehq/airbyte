/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.collectUnknownPaths
import io.airbyte.cdk.load.data.csv.toCsvHeader
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.file.csv.toCsvPrinterWithHeader
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.Meta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.io.OutputStream

class ProtoToCsvFormatter(
    stream: DestinationStream,
    private val outputStream: OutputStream,
    rootLevelFlattening: Boolean,
    extractedAtAsTimestampWithTimezone: Boolean,
) : ObjectStorageFormattingWriter {

    private val finalSchema: ObjectType = stream.schema.withAirbyteMeta(rootLevelFlattening)

    private val header: Array<String> = finalSchema.toCsvHeader()
    private val printer = finalSchema.toCsvPrinterWithHeader(outputStream)
    private val unknownColumnChanges =
        stream.schema.collectUnknownPaths().map {
            Meta.Change(
                it,
                AirbyteRecordMessageMetaChange.Change.NULLED,
                AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR,
            )
        }

    private val writer =
        ProtoToCsvWriter(
            header = header,
            columns = stream.airbyteValueProxyFieldAccessors,
            rootLevelFlattening = rootLevelFlattening,
            extractedAtTsTz = extractedAtAsTimestampWithTimezone,
        )

    override fun accept(record: DestinationRecordRaw) {
        val src = record.rawData
        require(src is DestinationRecordProtobufSource) {
            "ProtoToCsvFormatter only supports DestinationRecordProtobufSource"
        }
        printer.printRecord(
            *writer.toCsvRow(record, src, record.rawData.sourceMeta.changes + unknownColumnChanges)
        )
    }

    override fun flush() {
        printer.flush()
        outputStream.flush()
    }
    override fun close() {
        printer.close()
        outputStream.close()
    }
}
