/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference
import kotlin.coroutines.coroutineContext
import kotlinx.coroutines.ensureActive

/** Base class for JDBC implementations of [PartitionReader]. */
sealed class JdbcPartitionReader<P : JdbcPartition<*>>(
    val partition: P,
) : PartitionReader {

    val streamState: JdbcStreamState<*> = partition.streamState
    val stream: Stream = streamState.stream
    val sharedState: JdbcSharedState = streamState.sharedState
    val outputConsumer: OutputConsumer = sharedState.outputConsumer
    val selectQuerier: SelectQuerier = sharedState.selectQuerier

    private val acquiredResources = AtomicReference<AcquiredResources>()

    /** Calling [close] releases the resources acquired for the [JdbcPartitionReader]. */
    fun interface AcquiredResources : AutoCloseable

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        val acquiredResources: AcquiredResources =
            partition.tryAcquireResourcesForReader()
                ?: return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
        this.acquiredResources.set(acquiredResources)
        return PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
    }

    fun out(record: ObjectNode) {
        for (fieldName in streamFieldNames) {
            outData.set<JsonNode>(fieldName, record[fieldName] ?: Jsons.nullNode())
        }
        outputConsumer.accept(msg)
    }

    private val outData: ObjectNode = Jsons.objectNode()

    private val msg =
        AirbyteRecordMessage()
            .withStream(stream.name)
            .withNamespace(stream.namespace)
            .withData(outData)

    val streamFieldNames: List<String> = stream.fields.map { it.id }

    override fun releaseResources() {
        acquiredResources.getAndSet(null)?.close()
    }
}

/** JDBC implementation of [PartitionReader] which reads the [partition] in its entirety. */
class JdbcNonResumablePartitionReader<P : JdbcPartition<*>>(
    partition: P,
) : JdbcPartitionReader<P>(partition) {

    val runComplete = AtomicBoolean(false)
    val numRecords = AtomicLong()

    override suspend fun run() {
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
                for (record in result) {
                    out(record)
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

/**
 * JDBC implementation of [PartitionReader] which reads as much as possible of the [partition], in
 * order, before timing out.
 */
class JdbcResumablePartitionReader<P : JdbcSplittablePartition<*>>(
    partition: P,
) : JdbcPartitionReader<P>(partition) {

    val incumbentLimit = AtomicLong()
    val numRecords = AtomicLong()
    val lastRecord = AtomicReference<ObjectNode?>(null)
    val runComplete = AtomicBoolean(false)

    override suspend fun run() {
        val fetchSize: Int = streamState.fetchSizeOrDefault
        val limit: Long = streamState.limit
        incumbentLimit.set(limit)
        selectQuerier
            .executeQuery(
                q = partition.resumableQuery(limit),
                parameters =
                    SelectQuerier.Parameters(reuseResultObject = true, fetchSize = fetchSize),
            )
            .use { result: SelectQuerier.Result ->
                for (record in result) {
                    out(record)
                    lastRecord.set(record)
                    // Check activity periodically to handle timeout.
                    if (numRecords.incrementAndGet() % fetchSize == 0L) {
                        coroutineContext.ensureActive()
                    }
                }
            }
        runComplete.set(true)
    }

    override fun checkpoint(): PartitionReadCheckpoint {
        if (runComplete.get() && numRecords.get() < streamState.limit) {
            // The run method executed to completion with a LIMIT clause which was not reached.
            return PartitionReadCheckpoint(partition.completeState, numRecords.get())
        }
        // The run method ended because of either the LIMIT or the timeout.
        // Adjust the LIMIT value so that it grows or shrinks to try to fit the timeout.
        if (incumbentLimit.get() > 0L) {
            if (runComplete.get() && streamState.limit <= incumbentLimit.get()) {
                // Increase the limit clause for the next PartitionReader, because it's too small.
                // If it had been bigger then run might have executed for longer.
                streamState.updateLimitState { it.up }
            }
            if (!runComplete.get() && incumbentLimit.get() <= streamState.limit) {
                // Decrease the limit clause for the next PartitionReader, because it's too big.
                // If it had been smaller then run might have completed in time.
                streamState.updateLimitState { it.down }
            }
        }
        val checkpointState: OpaqueStateValue = partition.incompleteState(lastRecord.get()!!)
        return PartitionReadCheckpoint(checkpointState, numRecords.get())
    }
}
