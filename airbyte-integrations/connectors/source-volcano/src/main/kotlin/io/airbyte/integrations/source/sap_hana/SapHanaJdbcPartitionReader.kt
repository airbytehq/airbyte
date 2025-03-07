/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sap_hana

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.FieldOrMetaField
import io.airbyte.cdk.read.JdbcPartition
import io.airbyte.cdk.read.JdbcPartitionReader
import io.airbyte.cdk.read.JdbcSharedState
import io.airbyte.cdk.read.JdbcStreamState
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.SelectQuerier
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamRecordConsumer
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference

/** Base class for SAP HANA JDBC implementations of [PartitionReader]. */
sealed class SapHanaJdbcPartitionReader<P : JdbcPartition<*>>(
    val partition: P,
) : PartitionReader {

    private val log = KotlinLogging.logger {}

    val streamState: JdbcStreamState<*> = partition.streamState
    val stream: Stream = streamState.stream
    val sharedState: JdbcSharedState = streamState.sharedState
    val selectQuerier: SelectQuerier = sharedState.selectQuerier
    val streamRecordConsumer: StreamRecordConsumer =
        streamState.streamFeedBootstrap.streamRecordConsumer()

    private val acquiredResources = AtomicReference<JdbcPartitionReader.AcquiredResources>()

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        val acquiredResources: JdbcPartitionReader.AcquiredResources =
            partition.tryAcquireResourcesForReader()
                ?: return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
        this.acquiredResources.set(acquiredResources)
        return PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
    }

    fun out(row: SelectQuerier.ResultRow) {
        val sapHanaStreamState: SapHanaJdbcStreamState = streamState as SapHanaJdbcStreamState
        if (sapHanaStreamState.isReadingFromTriggerTable) {
            val decoratedRow = decorateTriggerBasedCdcRecord(row)
            streamRecordConsumer.accept(decoratedRow, emptyMap())
        } else {
            streamRecordConsumer.accept(row.data, row.changes)
        }
    }

    private fun decorateTriggerBasedCdcRecord(row: SelectQuerier.ResultRow): ObjectNode {
        val before: JsonNode = row.data[TriggerTableConfig.VALUE_BEFORE_FIELD.id]
        val after: JsonNode = row.data[TriggerTableConfig.VALUE_AFTER_FIELD.id]
        val isDelete: Boolean =
            row.data[TriggerTableConfig.OPERATION_TYPE_FIELD.id].asText().uppercase() == "DELETE"
        // Row data is wrapped in a JSON object by trigger already. So we take it as is.
        val data = if (isDelete) before else after
        val validatedData: ObjectNode = validateDataFieldName(data, stream.schema)
        val transactionTimestampJsonNode: JsonNode = row.data[TriggerTableConfig.CURSOR_FIELD.id]
        validatedData.set<JsonNode>(
            CommonMetaField.CDC_UPDATED_AT.id,
            transactionTimestampJsonNode,
        )
        validatedData.set<JsonNode>(
            CommonMetaField.CDC_DELETED_AT.id,
            if (isDelete) transactionTimestampJsonNode else Jsons.nullNode(),
        )
        validatedData.set<JsonNode>(
            TriggerTableConfig.CURSOR_FIELD.id,
            transactionTimestampJsonNode,
        )
        return validatedData
    }

    // Validate the data field name with the schema field name so they have the same case.
    // Field names are case-sensitive in JsonNode
    private fun validateDataFieldName(data: JsonNode, schema: Set<FieldOrMetaField>): ObjectNode {
        val validatedData: ObjectNode = Jsons.objectNode()
        for (field in schema) {
            val value =
                data
                    .fieldNames()
                    .asSequence()
                    .find { it.equals(field.id, ignoreCase = true) }
                    ?.let { data[it] }
                    ?: throw IllegalArgumentException("Field '${field.id}' not found")
            validatedData.set<JsonNode>(field.id, value)
        }
        return validatedData
    }

    override fun releaseResources() {
        acquiredResources.getAndSet(null)?.close()
    }

    /** If configured max feed read time elapsed we exit with a transient error */
    protected fun checkMaxReadTimeElapsed() {
        sharedState.configuration.maxSnapshotReadDuration?.let {
            if (java.time.Duration.between(sharedState.snapshotReadStartTime, Instant.now()) > it) {
                throw TransientErrorException("Shutting down snapshot reader: max duration elapsed")
            }
        }
    }
}

/** JDBC implementation of [PartitionReader] which reads the [partition] in its entirety. */
class SapHanaJdbcNonResumablePartitionReader<P : JdbcPartition<*>>(
    partition: P,
) : SapHanaJdbcPartitionReader<P>(partition) {

    val runComplete = AtomicBoolean(false)
    val numRecords = AtomicLong()

    override suspend fun run() {
        /* Don't start read if we've gone over max duration.
        We check for elapsed duration before reading and not while because
        existing exiting with an exception skips checkpoint(), so any work we
        did before time has elapsed will be wasted. */
        checkMaxReadTimeElapsed()

        selectQuerier
            .executeQuery(
                q = partition.nonResumableQuery,
                parameters =
                    SelectQuerier.Parameters(
                        reuseResultObject = true,
                        fetchSize = streamState.fetchSize
                    ),
            )
            .use { result: SelectQuerier.Result ->
                for (row in result) {
                    out(row)
                    numRecords.incrementAndGet()
                }
            }
        runComplete.set(true)
    }

    override fun checkpoint(): PartitionReadCheckpoint {
        // Sanity check.
        if (!runComplete.get()) throw RuntimeException("cannot checkpoint non-resumable read")
        // The run method executed to completion without a LIMIT clause.
        // This implies that the partition boundary has been reached.
        return PartitionReadCheckpoint(partition.completeState, numRecords.get())
    }
}
