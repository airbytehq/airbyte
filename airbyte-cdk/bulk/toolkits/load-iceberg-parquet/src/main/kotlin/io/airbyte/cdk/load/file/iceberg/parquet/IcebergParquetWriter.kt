/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.iceberg.parquet

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.iceberg.parquet.toIcebergRecord
import io.airbyte.cdk.load.data.iceberg.parquet.toIcebergSchema
import io.airbyte.cdk.load.data.parquet.ParquetMapperPipelineFactory
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.file.object_storage.ObjectStorageFormattingWriter
import io.airbyte.cdk.load.message.DestinationRecord
import java.io.Closeable
import org.apache.iceberg.Schema
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.io.DataWriter

class IcebergParquetWriter(private val writer: DataWriter<GenericRecord>) : Closeable {
    fun write(record: GenericRecord) = writer.write(record)
    override fun close() = writer.close()
}

class IcebergWriter(
    private val stream: DestinationStream,
    private val rootLevelFlattening: Boolean,
    private val icebergParquetWriter: IcebergParquetWriter,
    private val tableSchema: Schema,
) : ObjectStorageFormattingWriter {
    private val pipeline = ParquetMapperPipelineFactory().create(stream)
    private val catalogSchema =
        pipeline.finalSchema.withAirbyteMeta(rootLevelFlattening).toIcebergSchema()

    init {
        existingAndIncomingSchemaShouldBeSame()
    }

    private fun existingAndIncomingSchemaShouldBeSame() {
        val incomingFieldSet =
            catalogSchema
                .asStruct()
                .fields()
                .map { Triple(it.name(), it.type(), it.isOptional) }
                .toSet()
        val existingFieldSet =
            tableSchema
                .asStruct()
                .fields()
                .map { Triple(it.name(), it.type(), it.isOptional) }
                .toSet()

        val missingInIncoming = existingFieldSet - incomingFieldSet
        val extraInIncoming = incomingFieldSet - existingFieldSet

        if (missingInIncoming.isNotEmpty() || extraInIncoming.isNotEmpty()) {
            val errorMessage = buildString {
                append("Table schema fields are different than catalog schema:\n")
                if (missingInIncoming.isNotEmpty()) {
                    append("Fields missing in incoming schema: $missingInIncoming\n")
                }
                if (extraInIncoming.isNotEmpty()) {
                    append("Extra fields in incoming schema: $extraInIncoming\n")
                }
            }
            throw IllegalArgumentException(errorMessage)
        }

        val incomingIdentifierFields = catalogSchema.identifierFieldNames()
        val existingIdentifierFieldNames = tableSchema.identifierFieldNames()

        val identifiersMissingInIncoming = existingIdentifierFieldNames - incomingIdentifierFields
        val identifiersExtraInIncoming = incomingIdentifierFields - existingIdentifierFieldNames

        if (identifiersMissingInIncoming.isNotEmpty() || identifiersExtraInIncoming.isNotEmpty()) {
            val errorMessage = buildString {
                append("Identifier fields are different:\n")
                if (identifiersMissingInIncoming.isNotEmpty()) {
                    append(
                        "Identifier Fields missing in incoming schema: $identifiersMissingInIncoming\n"
                    )
                }
                if (identifiersExtraInIncoming.isNotEmpty()) {
                    append(
                        "Identifier Extra fields in incoming schema: $identifiersExtraInIncoming\n"
                    )
                }
            }
            throw IllegalArgumentException(errorMessage)
        }
    }

    override fun accept(record: DestinationRecord) {
        val dataMapped =
            pipeline
                .map(record.data, record.meta?.changes)
                .withAirbyteMeta(stream, record.emittedAtMs, rootLevelFlattening)
        val toIcebergRecord = dataMapped.toIcebergRecord(tableSchema)
        icebergParquetWriter.write(toIcebergRecord)
    }

    override fun close() {
        icebergParquetWriter.close()
    }
}
