/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.dataflow

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.iceberg.parquet.toIcebergRecord
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.RecordWrapper
import io.github.oshai.kotlinlogging.KotlinLogging
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.data.Record
import org.apache.iceberg.io.BaseTaskWriter

private val logger = KotlinLogging.logger {}

/**
 * Aggregate implementation for S3 Data Lake destination.
 *
 * Receives pre-coerced RecordDTO from the dataflow pipeline and converts to Iceberg records for
 * writing.
 */
class S3DataLakeAggregate(
    private val stream: DestinationStream,
    private val table: Table,
    private val schema: Schema,
    private val stagingBranchName: String,
    private val writer: BaseTaskWriter<Record>,
    private val icebergUtil: IcebergUtil,
) : Aggregate {
    override fun accept(record: RecordDTO) {
        val wrappedRecord =
            RecordWrapper(
                delegate = icebergUtil.toIcebergRecord(record.fields, schema),
                operation = icebergUtil.getOperation(record.fields, stream.importType)
            )

        writer.write(wrappedRecord)
    }

    override suspend fun flush() {
        logger.info {
            "Flushing aggregate to staging branch $stagingBranchName for stream ${stream.mappedDescriptor}"
        }

        val writeResult = writer.complete()

        if (writeResult.deleteFiles().isNotEmpty()) {
            // Use row delta for updates/deletes (dedup mode)
            val delta = table.newRowDelta().toBranch(stagingBranchName)
            writeResult.dataFiles().forEach { delta.addRows(it) }
            writeResult.deleteFiles().forEach { delta.addDeletes(it) }
            synchronized(S3DataLakeAggregate::class.java) { delta.commit() }
        } else {
            // Use append for simple appends
            val append = table.newAppend().toBranch(stagingBranchName)
            writeResult.dataFiles().forEach { append.appendFile(it) }
            synchronized(S3DataLakeAggregate::class.java) { append.commit() }
        }

        logger.info { "Flushed records to staging branch $stagingBranchName" }

        // not sure if this wrapping is necessary
        withContext(Dispatchers.IO) {
            logger.info { "Closing writer for $stagingBranchName" }
            writer.close()
        }
    }
}
