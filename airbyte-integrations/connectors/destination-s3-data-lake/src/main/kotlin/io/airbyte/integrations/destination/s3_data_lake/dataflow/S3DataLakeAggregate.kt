/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.dataflow

import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.RecordWrapper
import io.github.oshai.kotlinlogging.KotlinLogging
import kotlin.math.min
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.data.Record
import org.apache.iceberg.io.BaseTaskWriter
import software.amazon.awssdk.core.exception.SdkServiceException

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
                operation = icebergUtil.getOperation(record.fields, stream.tableSchema.importType)
            )

        writer.write(wrappedRecord)
    }

    override suspend fun flush() {
        logger.info {
            "Flushing aggregate to staging branch $stagingBranchName for stream ${stream.mappedDescriptor}"
        }

        val writeResult = writer.complete()

        if (writeResult.deleteFiles().isNotEmpty()) {
            commitWithRetry("row delta") {
                val delta = table.newRowDelta().toBranch(stagingBranchName)
                writeResult.dataFiles().forEach { delta.addRows(it) }
                writeResult.deleteFiles().forEach { delta.addDeletes(it) }
                synchronized(commitLock) { delta.commit() }
            }
        } else {
            commitWithRetry("append") {
                val append = table.newAppend().toBranch(stagingBranchName)
                writeResult.dataFiles().forEach { append.appendFile(it) }
                synchronized(commitLock) { append.commit() }
            }
        }

        logger.info { "Flushed records to staging branch $stagingBranchName" }

        // not sure if this wrapping is necessary
        withContext(Dispatchers.IO) {
            logger.info { "Closing writer for $stagingBranchName" }
            writer.close()
        }
    }

    private suspend fun commitWithRetry(operationName: String, operation: () -> Unit) {
        var lastException: Exception? = null
        for (attempt in 1..MAX_COMMIT_ATTEMPTS) {
            try {
                operation()
                return
            } catch (e: Exception) {
                if (!isThrottlingException(e)) throw e
                lastException = e
                if (attempt < MAX_COMMIT_ATTEMPTS) {
                    val delayMs =
                        min(BASE_RETRY_DELAY_MS * (1L shl (attempt - 1)), MAX_RETRY_DELAY_MS)
                    logger.warn(e) {
                        "Glue API throttled during $operationName " +
                            "(attempt $attempt/$MAX_COMMIT_ATTEMPTS), retrying in ${delayMs}ms."
                    }
                    delay(delayMs)
                }
            }
        }
        throw TransientErrorException(
            "Glue API rate limit exceeded during Iceberg $operationName.",
            lastException
        )
    }

    companion object {
        val commitLock: Any = Any()
        private const val MAX_COMMIT_ATTEMPTS = 5
        private const val BASE_RETRY_DELAY_MS = 1_000L
        private const val MAX_RETRY_DELAY_MS = 30_000L

        fun isThrottlingException(e: Throwable): Boolean {
            var current: Throwable? = e
            while (current != null) {
                if (current is SdkServiceException && current.isThrottlingException) {
                    return true
                }
                current = current.cause
            }
            return false
        }
    }
}
