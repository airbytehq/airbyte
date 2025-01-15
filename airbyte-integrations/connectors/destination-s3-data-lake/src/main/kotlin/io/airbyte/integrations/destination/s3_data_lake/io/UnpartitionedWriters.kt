/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.io

import org.apache.iceberg.FileFormat
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.Schema
import org.apache.iceberg.data.Record
import org.apache.iceberg.io.FileAppenderFactory
import org.apache.iceberg.io.FileIO
import org.apache.iceberg.io.OutputFileFactory
import org.apache.iceberg.io.UnpartitionedWriter

/**
 * [BaseDeltaTaskWriter] implementation that handles delta (insert, update, delete) writes to an
 * un-partitioned Iceberg [org.apache.iceberg.Table].
 */
class UnpartitionedDeltaWriter(
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
        spec,
        format,
        appenderFactory,
        outputFileFactory,
        io,
        targetFileSize,
        schema,
        identifierFieldIds
    ) {

    private val writer = RowDataDeltaWriter(null)

    override fun route(row: Record): BaseDeltaTaskWriter.RowDataDeltaWriter {
        return writer
    }

    override fun close() {
        writer.close()
    }
}

/**
 * [org.apache.iceberg.io.BaseTaskWriter] implementation that handles append-only writes to an
 * un-partitioned Iceberg [org.apache.iceberg.Table].
 */
class UnpartitionedAppendWriter(
    spec: PartitionSpec,
    format: FileFormat,
    appenderFactory: FileAppenderFactory<Record>,
    outputFileFactory: OutputFileFactory,
    io: FileIO,
    targetFileSize: Long,
) :
    UnpartitionedWriter<Record>(
        spec,
        format,
        appenderFactory,
        outputFileFactory,
        io,
        targetFileSize
    )
