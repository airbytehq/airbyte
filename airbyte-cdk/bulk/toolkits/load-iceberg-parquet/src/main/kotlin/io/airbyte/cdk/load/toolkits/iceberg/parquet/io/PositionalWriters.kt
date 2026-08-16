/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import java.io.IOException
import java.io.UncheckedIOException
import org.apache.iceberg.FileFormat
import org.apache.iceberg.PartitionKey
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.data.GenericFileWriterFactory
import org.apache.iceberg.data.Record
import org.apache.iceberg.io.FileIO
import org.apache.iceberg.io.OutputFileFactory
import org.apache.iceberg.util.Tasks

class UnpartitionedPositionDeltaWriter(
    table: Table,
    spec: PartitionSpec,
    format: FileFormat,
    writerFactory: GenericFileWriterFactory,
    outputFileFactory: OutputFileFactory,
    io: FileIO,
    targetFileSize: Long,
    schema: Schema,
    identifierFieldIds: Set<Int>,
    resolver: PositionalDeleteResolver,
    allowWholeFileSupersession: Boolean,
) :
    BasePositionDeltaTaskWriter(
        table,
        spec,
        format,
        writerFactory,
        outputFileFactory,
        io,
        targetFileSize,
        schema,
        identifierFieldIds,
        resolver,
        allowWholeFileSupersession,
    ) {
    private val writer = RowDataPositionDeltaWriter(null)

    override fun route(row: Record): RowDataPositionDeltaWriter = writer

    override fun close() {
        writer.close()
    }
}

class PartitionedPositionDeltaWriter(
    table: Table,
    spec: PartitionSpec,
    format: FileFormat,
    writerFactory: GenericFileWriterFactory,
    outputFileFactory: OutputFileFactory,
    io: FileIO,
    targetFileSize: Long,
    schema: Schema,
    identifierFieldIds: Set<Int>,
    resolver: PositionalDeleteResolver,
    allowWholeFileSupersession: Boolean,
) :
    BasePositionDeltaTaskWriter(
        table,
        spec,
        format,
        writerFactory,
        outputFileFactory,
        io,
        targetFileSize,
        schema,
        identifierFieldIds,
        resolver,
        allowWholeFileSupersession,
    ) {
    private val partitionKey = PartitionKey(spec, schema)
    private val writers = mutableMapOf<PartitionKey, RowDataPositionDeltaWriter>()

    override fun route(row: Record): RowDataPositionDeltaWriter {
        partitionKey.partition(wrapper().wrap(row))
        val key = partitionKey.copy()
        return writers.getOrPut(key) { RowDataPositionDeltaWriter(key) }
    }

    override fun close() {
        try {
            Tasks.foreach(writers.values)
                .throwFailureWhenFinished()
                .noRetry()
                .run(RowDataPositionDeltaWriter::close, IOException::class.java)
            writers.clear()
        } catch (e: IOException) {
            throw UncheckedIOException("Failed to close positional delta writer", e)
        }
    }
}
