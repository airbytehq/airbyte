/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.output.OutputMessageRouter
import io.airbyte.cdk.output.OutputMessageRouter.OutputChannelType.STDIO
import io.airbyte.cdk.output.sockets.toJson
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Duration
import java.time.Instant
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference
import kotlin.coroutines.coroutineContext
import kotlin.time.toKotlinDuration
import kotlinx.coroutines.ensureActive

/** Base class for JDBC implementations of [PartitionReader]. */
sealed class JdbcPartitionReader<P : JdbcPartition<*>>(
    val partition: P,
) : PartitionReader {

    lateinit var outputMessageRouter: OutputMessageRouter
    private val charPool: List<Char> = ('a'..'z') + ('A'..'Z') + ('0'..'9')

    private fun generatePartitionId(length: Int): String =
        (1..length).map { charPool.random() }.joinToString("")

    protected var partitionId: String = generatePartitionId(4)
    val streamState: JdbcStreamState<*> = partition.streamState
    val stream: Stream = streamState.stream
    val sharedState: JdbcSharedState = streamState.sharedState
    val selectQuerier: SelectQuerier = sharedState.selectQuerier

    /** The [AcquiredResource] acquired for this [JdbcPartitionReader]. */

    private val acquiredResources = AtomicReference<Map<ResourceType, AcquiredResource>>()

    /** Calling [close] releases the resources acquired for the [JdbcPartitionReader]. */
    interface AcquiredResource: AutoCloseable {
        val resource: Resource.Acquired?
    }

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        val resourceTypes = when (streamState.streamFeedBootstrap.outputChannelType) {
            STDIO -> listOf(ResourceType.RESOURCE_DB_CONNECTION)
            else -> listOf(ResourceType.RESOURCE_DB_CONNECTION, ResourceType.RESOURCE_OUTPUT_SOCKET)

        }
        val acquiredResources: Map<ResourceType, AcquiredResource> =
            partition.tryAcquireResourcesForReader(resourceTypes)
                ?: return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
        this.acquiredResources.set(acquiredResources)

        outputMessageRouter = OutputMessageRouter(
            streamState.streamFeedBootstrap.outputChannelType,
            streamState.streamFeedBootstrap.outputConsumer,
            mapOf("partition_id" to partitionId),
             streamState.streamFeedBootstrap,
            this.acquiredResources.get().filter { it.value.resource != null }.map{ it.key to it.value.resource!! }.toMap())

        return PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
    }

    fun out(row: SelectQuerier.ResultRow) {
        /*val s = streamState.streamFeedBootstrap.protoStreamRecordConsumer(ProtoRecordOutputConsumer(boostedOutputConsumer!!.socket,
            Clock.systemUTC(), 256))
            s.accept(row.data, row.changes)*/

//        streamRecordConsumer.accept(row.data, row.changes)
//        messageProcessor.acceptRecord(row.data)
        outputMessageRouter.recordAcceptor(row.data)
    }

    override fun releaseResources() {
//        streamRecordConsumer.close() // TEMP: swith to .use {}
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
        var s = PartitionReader.pendingStates.poll()

        while (s != null) {
            when (s) {
                is AirbyteStateMessage -> {
/*
                    val o = ProtoRecordOutputConsumer(boostedOutputConsumer!!.socket,
                        Clock.systemUTC(), 256)
                    o.accept(s)
*/
//                    boostedOutputConsumer?.accept(s)
                    outputMessageRouter.acceptNonRecord(s, needAlsoSimpleOutout = false)
                }
                is AirbyteStreamStatusTraceMessage -> {
/*
                    val o = ProtoRecordOutputConsumer(boostedOutputConsumer!!.socket,
                        Clock.systemUTC(), 256)
                    o.accept(s)
*/
//                    boostedOutputConsumer?.accept(s)
                    outputMessageRouter.acceptNonRecord(s, needAlsoSimpleOutout = false)
                }
            }
            s = PartitionReader.pendingStates.poll()
        }
    }

}

/** JDBC implementation of [PartitionReader] which reads the [partition] in its entirety. */
class JdbcNonResumablePartitionReader<P : JdbcPartition<*>>(
    partition: P,
) : JdbcPartitionReader<P>(partition) {
    private val log = KotlinLogging.logger {}
    val runComplete = AtomicBoolean(false)
    val numRecords = AtomicLong()

    lateinit var dur: Instant

    override suspend fun run() {
        synchronized(this) {
            if (::dur.isInitialized.not()) { dur = Instant.now() }
        }

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
//                    numRecords.incrementAndGet()
                    if (numRecords.incrementAndGet() % 500_000 == 0L) {
                        log.info { "*** Read $numRecords records from partition $partitionId" }
                    }
                }
            }
        runComplete.set(true)
        log.info { "*** --------------- Partition time: ${Duration.between(dur, Instant.now()).toKotlinDuration()} ---------------" }
    }

    override fun checkpoint(): PartitionReadCheckpoint {
        // Sanity check.
        if (!runComplete.get()) throw RuntimeException("cannot checkpoint non-resumable read")
        // The run method executed to completion without a LIMIT clause.
        // This implies that the partition boundary has been reached.
        return PartitionReadCheckpoint(partition.completeState, numRecords.get(), partitionId)
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
            return PartitionReadCheckpoint(partition.completeState, numRecords.get(), partitionId)
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
        return PartitionReadCheckpoint(checkpointState, numRecords.get(), partitionId)
    }
}
