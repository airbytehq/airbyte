/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.iceberg_parquet.toIcebergRecord
import io.airbyte.cdk.load.data.iceberg_parquet.toIcebergSchema
import io.airbyte.cdk.load.data.parquet.ParquetMapperPipelineFactory
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.file.iceberg_parquet.IcebergParquetWriter
import io.airbyte.cdk.load.file.object_storage.ObjectStorageFormattingWriter
import io.airbyte.cdk.load.message.DestinationRecord
import org.apache.iceberg.Schema

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
        if (catalogSchema.sameSchema(tableSchema)) {
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
