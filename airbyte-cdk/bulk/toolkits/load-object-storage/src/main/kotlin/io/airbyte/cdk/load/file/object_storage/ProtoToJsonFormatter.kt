/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.load.file.object_storage

import com.fasterxml.jackson.core.JsonEncoding
import com.fasterxml.jackson.core.JsonGenerator
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.io.OutputStream

class ProtoToJsonFormatter(
    stream: DestinationStream,
    private val outputStream: OutputStream,
    rootLevelFlattening: Boolean
) : ObjectStorageFormattingWriter {

    private fun AirbyteType.collectUnknownPaths(currentPath: String = ""): Set<String> {
        fun join(prefix: String, segment: String) =
            if (prefix == "") segment else "$prefix.$segment"

        return when (this) {
            is UnknownType -> setOf(currentPath)
            StringType,
            BooleanType,
            IntegerType,
            NumberType,
            DateType,
            TimestampTypeWithTimezone,
            TimestampTypeWithoutTimezone,
            TimeTypeWithTimezone,
            TimeTypeWithoutTimezone,
            ObjectTypeWithoutSchema,
            ObjectTypeWithEmptySchema,
            ArrayTypeWithoutSchema -> emptySet()
            is ObjectType ->
                properties
                    .flatMap { (name, field) ->
                        field.type.collectUnknownPaths(join(currentPath, name))
                    }
                    .toSet()
            is ArrayType -> items.type.collectUnknownPaths(currentPath)
            is UnionType -> options.flatMap { it.collectUnknownPaths(currentPath) }.toSet()
        }
    }

    private val fastWriter =
        ProtoToJsonWriter(stream.airbyteValueProxyFieldAccessors, rootLevelFlattening)
    private val unknownColumns = stream.schema.collectUnknownPaths()
    private val unknownColumnsPresent = unknownColumns.isNotEmpty()

    private val generator =
        Jsons.disable(JsonGenerator.Feature.AUTO_CLOSE_TARGET)
            .createGenerator(outputStream, JsonEncoding.UTF8)
            .apply { setRootValueSeparator(null) }

    override fun accept(record: DestinationRecordRaw) {
        when (val source = record.rawData) {
            is DestinationRecordProtobufSource -> {
                val changes = record.rawData.sourceMeta.changes.toMutableList()
                if (unknownColumnsPresent) {
                    unknownColumns.forEach {
                        changes.add(
                            Meta.Change(
                                it,
                                AirbyteRecordMessageMetaChange.Change.NULLED,
                                AirbyteRecordMessageMetaChange.Reason
                                    .DESTINATION_SERIALIZATION_ERROR,
                            ),
                        )
                    }
                }

                generator.writeStartObject()
                fastWriter.writeMeta(generator, record, changes) // _airbyte_* fields
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
