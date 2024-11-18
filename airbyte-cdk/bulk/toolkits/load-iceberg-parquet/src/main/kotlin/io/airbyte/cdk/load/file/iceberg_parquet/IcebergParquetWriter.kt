/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.iceberg_parquet

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.iceberg_parquet.toIcebergRecord
import io.airbyte.cdk.load.data.iceberg_parquet.toIcebergSchema
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
    tableSchema: Schema,
) : ObjectStorageFormattingWriter {
    private val pipeline = ParquetMapperPipelineFactory().create(stream)
    private val catalogSchema =
        pipeline.finalSchema.withAirbyteMeta(rootLevelFlattening).toIcebergSchema()

    init {
        if (!catalogSchema.sameSchema(tableSchema)) {
            throw IllegalArgumentException("Table schema is different than catalog schema")
        }
    }

    override fun accept(record: DestinationRecord) {
        val dataMapped =
            pipeline
                .map(record.data, record.meta?.changes)
                .withAirbyteMeta(stream, record.emittedAtMs, rootLevelFlattening)
        val toIcebergRecord = dataMapped.toIcebergRecord(catalogSchema)
        icebergParquetWriter.write(toIcebergRecord)
    }

    override fun close() {
        icebergParquetWriter.close()
    }
}
