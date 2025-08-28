/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.node.ObjectNode
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.output.DataChannelMedium.*
import io.airbyte.cdk.output.OutputMessageRouter
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.output.sockets.toJson
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import java.time.Duration
import java.time.Instant
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference
import kotlin.coroutines.coroutineContext
import kotlinx.coroutines.ensureActive

/** Base class for JDBC implementations of [PartitionReader]. */
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
sealed class JdbcPartitionReader<P : JdbcPartition<*>>(
    val partition: P,
) : PartitionReader {

    lateinit var outputMessageRouter: OutputMessageRouter
    lateinit var outputRoute: ((NativeRecordPayload, Map<Field, FieldValueChange>?) -> Unit)

    protected var partitionId: String = generatePartitionId(4)
    val streamState: JdbcStreamState<*> = partition.streamState
    val stream: Stream = streamState.stream
    val sharedState: JdbcSharedState = streamState.sharedState
    val selectQuerier: SelectQuerier = sharedState.selectQuerier

    /** The [AcquiredResource] acquired for this [JdbcPartitionReader]. */
    private val acquiredResources = AtomicReference<Map<ResourceType, AcquiredResource>>()

    /** Calling [close] releases the resources acquired for the [JdbcPartitionReader]. */
    interface AcquiredResource : AutoCloseable {
        val resource: Resource.Acquired?
    }

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        val resourceTypes =
            when (streamState.streamFeedBootstrap.dataChannelMedium) {
                STDIO -> listOf(ResourceType.RESOURCE_DB_CONNECTION)
                SOCKET ->
                    listOf(ResourceType.RESOURCE_DB_CONNECTION, ResourceType.RESOURCE_OUTPUT_SOCKET)
            }
        val resources: Map<ResourceType, AcquiredResource> =
            partition.tryAcquireResourcesForReader(resourceTypes)
                ?: return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
        acquiredResources.set(resources)

        outputMessageRouter =
            OutputMessageRouter(
                streamState.streamFeedBootstrap.dataChannelMedium,
                streamState.streamFeedBootstrap.dataChannelFormat,
                streamState.streamFeedBootstrap.outputConsumer,
                mapOf("partition_id" to partitionId),
                streamState.streamFeedBootstrap,
                acquiredResources
                    .get()
                    .filter { it.value.resource != null }
                    .map { it.key to it.value.resource!! }
                    .toMap()
            )
        outputRoute = outputMessageRouter.recordAcceptors[stream.id]!!

        return PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
    }

    fun out(row: SelectQuerier.ResultRow) {
        outputRoute(row.data, row.changes)
    }

    override fun releaseResources() {
        if (::outputMessageRouter.isInitialized) {
            outputMessageRouter.close()
        }
        acquiredResources.getAndSet(null)?.forEach { it.value.close() }
        partitionId = generatePartitionId(4)
    }

    /** If configured max feed read time elapsed we exit with a transient error */
    protected fun checkMaxReadTimeElapsed() {
        sharedState.configuration.maxSnapshotReadDuration?.let {
            if (Duration.between(sharedState.snapshotReadStartTime, Instant.now()) > it) {
                throw TransientErrorException("Shutting down snapshot reader: max duration elapsed")
            }
        }
    }

    protected fun outputPendingMessages() {
        if (streamState.streamFeedBootstrap.dataChannelMedium == STDIO) {
            return
        }
        while (PartitionReader.pendingStates.isNotEmpty()) {
            var pendingMessage = PartitionReader.pendingStates.poll() ?: break
            when (pendingMessage) {
                is AirbyteStateMessage -> {
                    outputMessageRouter.acceptNonRecord(pendingMessage)
                }
                is AirbyteStreamStatusTraceMessage -> {
                    outputMessageRouter.acceptNonRecord(pendingMessage)
                }
            }
        }
    }
}

/** JDBC implementation of [PartitionReader] which reads the [partition] in its entirety. */
class JdbcNonResumablePartitionReader<P : JdbcPartition<*>>(
    partition: P,
) : JdbcPartitionReader<P>(partition) {
    val runComplete = AtomicBoolean(false)
    val numRecords = AtomicLong()

    override suspend fun run() {
        outputPendingMessages()
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
        return PartitionReadCheckpoint(
            partition.completeState,
            numRecords.get(),
            when (streamState.streamFeedBootstrap.dataChannelMedium) {
                SOCKET -> partitionId
                STDIO -> null
            }
        )
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

        outputPendingMessages()
        /* Don't start read if we've gone over max duration.
        We check for elapsed duration before reading and not while because
        existing exiting with an exception skips checkpoint(), so any work we
        did before time has elapsed will be wasted. */
        checkMaxReadTimeElapsed()

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
                for (row in result) {
                    out(row)
                    lastRecord.set(row.data.toJson(Jsons.objectNode()))
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
            return PartitionReadCheckpoint(
                partition.completeState,
                numRecords.get(),
                when (streamState.streamFeedBootstrap.dataChannelMedium) {
                    SOCKET -> partitionId
                    STDIO -> null
                }
            )
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
        return PartitionReadCheckpoint(
            checkpointState,
            numRecords.get(),
            when (streamState.streamFeedBootstrap.dataChannelMedium) {
                SOCKET -> partitionId
                STDIO -> null
            }
        )
    }
}
