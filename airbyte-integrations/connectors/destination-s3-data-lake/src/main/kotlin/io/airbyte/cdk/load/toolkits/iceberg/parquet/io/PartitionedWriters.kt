/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import java.io.IOException
import java.io.UncheckedIOException
import org.apache.iceberg.FileFormat
import org.apache.iceberg.PartitionKey
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.data.InternalRecordWrapper
import org.apache.iceberg.data.Record
import org.apache.iceberg.io.FileAppenderFactory
import org.apache.iceberg.io.FileIO
import org.apache.iceberg.io.OutputFileFactory
import org.apache.iceberg.io.PartitionedWriter
import org.apache.iceberg.util.Tasks

/**
 * [BaseDeltaTaskWriter] implementation that handles delta (insert, update, delete) writes to a
 * partitioned Iceberg [org.apache.iceberg.Table].
 */
class PartitionedDeltaWriter(
    table: Table,
    spec: PartitionSpec,
    format: FileFormat,
    appenderFactory: FileAppenderFactory<Record>,
    outputFileFactory: OutputFileFactory,
    io: FileIO,
    targetFileSize: Long,
    schema: Schema,
    identifierFieldIds: Set<Int>,
) :
    BaseDeltaTaskWriter(
        table,
        spec,
        format,
        appenderFactory,
        outputFileFactory,
        io,
        targetFileSize,
        schema,
        identifierFieldIds
    ) {

    private val partitionKey = PartitionKey(spec, schema)
    private val writers = mutableMapOf<PartitionKey, RowDataDeltaWriter>()

    override fun route(row: Record): RowDataDeltaWriter {
        partitionKey.partition(wrapper().wrap(row))

        var writer: RowDataDeltaWriter? = writers[partitionKey]
        if (writer == null) {
            val copiedKey: PartitionKey = partitionKey.copy()
            writer = RowDataDeltaWriter(copiedKey)
            writers[copiedKey] = writer
        }

        return writer
    }

    override fun close() {
        try {
            Tasks.foreach(writers.values)
                .throwFailureWhenFinished()
                .noRetry()
                .run(RowDataDeltaWriter::close, IOException::class.java)

            writers.clear()
        } catch (e: IOException) {
            throw UncheckedIOException("Failed to close equality delta writer", e)
        }
    }
}

/**
 * [org.apache.iceberg.io.BaseTaskWriter] implementation that handles append-only writes to a
 * partitioned Iceberg [org.apache.iceberg.Table].
 */
class PartitionedAppendWriter(
    spec: PartitionSpec,
    format: FileFormat,
    appenderFactory: FileAppenderFactory<Record>,
    outputFileFactory: OutputFileFactory,
    io: FileIO,
    targetFileSize: Long,
    schema: Schema,
) :
    PartitionedWriter<Record>(
        spec,
        format,
        appenderFactory,
        outputFileFactory,
        io,
        targetFileSize
    ) {
    private val partitionKey = PartitionKey(spec, schema)
    private val wrapper = InternalRecordWrapper(schema.asStruct())

    override fun partition(row: Record): PartitionKey {
        partitionKey.partition(wrapper.wrap(row))
        return partitionKey
    }
}
