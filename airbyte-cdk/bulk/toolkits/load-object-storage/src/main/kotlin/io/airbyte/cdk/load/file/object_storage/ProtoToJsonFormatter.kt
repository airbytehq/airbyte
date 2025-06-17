/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.load.file.object_storage

import com.fasterxml.jackson.core.JsonEncoding
import com.fasterxml.jackson.core.JsonGenerator
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.util.Jsons
import java.io.OutputStream

class ProtoToJsonFormatter(
    stream: DestinationStream,
    private val outputStream: OutputStream,
    rootLevelFlattening: Boolean
) : ObjectStorageFormattingWriter {

    private val fastWriter =
        ProtoToJsonWriter(stream.airbyteValueProxyFieldAccessors, rootLevelFlattening)

    private val generator =
        Jsons.disable(JsonGenerator.Feature.AUTO_CLOSE_TARGET)
            .createGenerator(outputStream, JsonEncoding.UTF8)
            .apply { setRootValueSeparator(null) }

    override fun accept(record: DestinationRecordRaw) {
        when (val source = record.rawData) {
            is DestinationRecordProtobufSource -> {
                generator.writeStartObject()
                fastWriter.writeMeta(generator, record) // _airbyte_* fields
                fastWriter.writePayload(generator, source) // actual data
                generator.writeEndObject()
                generator.writeRaw('\n')
            }
            else -> {
                throw RuntimeException(
                    "ProtoToJsonFormatter only supports conversion of proto records to JSON",
                )
            }
        }
    }

    override fun flush() {
        generator.flush()
        outputStream.flush()
    }

    override fun close() {
        generator.close()
        outputStream.close()
    }
}
