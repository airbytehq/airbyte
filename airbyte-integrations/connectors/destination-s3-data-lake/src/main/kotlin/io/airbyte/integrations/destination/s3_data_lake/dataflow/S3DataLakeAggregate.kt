/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.dataflow

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.Overwrite
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.message.ArrowBatchDTO
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.RecordWrapper
import io.github.oshai.kotlinlogging.KotlinLogging
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.apache.iceberg.DataFile
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
    private var arrowWriter: ArrowBatchFileWriter? = null
    private var recordPathUsed = false

    override fun accept(record: RecordDTO) {
        check(arrowWriter == null) {
            "Cannot mix record and ARROW writes for ${stream.mappedDescriptor}"
        }
        recordPathUsed = true
        val wrappedRecord =
            RecordWrapper(
                delegate = icebergUtil.toIcebergRecord(record.fields, schema),
                operation = icebergUtil.getOperation(record.fields, stream.tableSchema.importType)
            )

        writer.write(wrappedRecord)
    }

    override fun acceptArrowBatch(batch: ArrowBatchDTO) {
        check(!recordPathUsed) {
            "Cannot mix record and ARROW writes for ${stream.mappedDescriptor}"
        }
        require(table.spec().isUnpartitioned) {
            "ARROW batches only support unpartitioned Iceberg tables"
        }
        require(
            stream.tableSchema.importType is Append || stream.tableSchema.importType == Overwrite
        ) { "ARROW batches only support append and overwrite syncs" }
        val arrowBatchWriter =
            arrowWriter
                ?: ArrowBatchFileWriter(
                        table,
                        stream,
                        icebergUtil.constructGenerationIdSuffix(stream.generationId),
                    )
                    .also { arrowWriter = it }
        arrowBatchWriter.write(batch)
    }

    override fun onPublish() {
        arrowWriter?.complete()
    }

    override suspend fun flush() {
        logger.info {
            "Flushing aggregate to staging branch $stagingBranchName for stream ${stream.mappedDescriptor}"
        }

        val writeResult =
            arrowWriter?.complete()?.let { dataFiles ->
                CommitFiles(dataFiles = dataFiles, deleteFiles = emptyList())
            }
                ?: writer.complete().let {
                    CommitFiles(
                        dataFiles = it.dataFiles().toList(),
                        deleteFiles = it.deleteFiles().toList(),
                    )
                }

        commitWriteResult(writeResult)

        logger.info { "Flushed records to staging branch $stagingBranchName" }

        withContext(Dispatchers.IO) {
            logger.info { "Closing writer for $stagingBranchName" }
            arrowWriter?.close()
            writer.close()
        }
    }

    private fun commitWriteResult(writeResult: CommitFiles) {
        if (writeResult.deleteFiles.isNotEmpty()) {
            // Use row delta for updates/deletes (dedup mode)
            val delta = table.newRowDelta().toBranch(stagingBranchName)
            writeResult.dataFiles.forEach { delta.addRows(it) }
            writeResult.deleteFiles.forEach { delta.addDeletes(it) }
            synchronized(commitLock) { delta.commit() }
        } else {
            // Use append for simple appends
            val append = table.newAppend().toBranch(stagingBranchName)
            writeResult.dataFiles.forEach { append.appendFile(it) }
            synchronized(commitLock) { append.commit() }
        }
    }

    private data class CommitFiles(
        val dataFiles: List<DataFile>,
        val deleteFiles: List<org.apache.iceberg.DeleteFile>
    )

    companion object {
        val commitLock: Any = Any()
    }
}
