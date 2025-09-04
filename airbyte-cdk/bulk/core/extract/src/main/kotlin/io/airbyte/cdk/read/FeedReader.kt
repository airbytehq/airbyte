/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.output.DataChannelFormat
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.output.DataChannelMedium.*
import io.airbyte.cdk.output.OutputMessageRouter
import io.airbyte.cdk.util.ThreadRenamingCoroutineName
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Clock
import java.util.concurrent.atomic.AtomicInteger
import kotlin.coroutines.CoroutineContext
import kotlin.coroutines.coroutineContext
import kotlin.time.toKotlinDuration
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Deferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.async
import kotlinx.coroutines.launch
import kotlinx.coroutines.selects.select
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout

/**
 * A [FeedReader] manages the publishing of RECORD, STATE and TRACE messages for a single [feed].
 */
class FeedReader(
    val root: RootReader,
    val feed: Feed,
    val resourceAcquirer: ResourceAcquirer,
    dataChannelFormat: DataChannelFormat,
    val dataChannelMedium: DataChannelMedium,
    bufferByteSizeThresholdForFlush: Int,
    val clock: Clock,
) {
    private val log = KotlinLogging.logger {}

    private val stateId: AtomicInteger = AtomicInteger(1)

    // Global state ID is unique for each state emitted regardless of the feed it originates from.
    companion object {
        private val globalStateId: AtomicInteger = AtomicInteger(1)
    }

    private val feedBootstrap: FeedBootstrap<*> =
        FeedBootstrap.create(
            root.outputConsumer,
            root.metaFieldDecorator,
            root.stateManager,
            feed,
            dataChannelFormat,
            dataChannelMedium,
            bufferByteSizeThresholdForFlush,
            clock
        )

    /** Reads records from this [feed]. */
    suspend fun read() {
        var partitionsCreatorID = 1L
        while (true) {
            // Create PartitionReader instances.
            val partitionReaders: List<PartitionReader> = createPartitions(partitionsCreatorID)
            if (partitionReaders.isEmpty()) {
                log.info {
                    "no more partitions to read for '${feed.label}' in round $partitionsCreatorID"
                }
                // Publish stream completion.
                root.streamStatusManager.notifyComplete(feed)
                // Publish a checkpoint if applicable.
                maybeCheckpoint(true)

                break
            }
            // Launch coroutines which read from each partition.
            val scheduledPartitionReaders =
                mutableMapOf<Long, Deferred<Result<PartitionReadCheckpoint>>>()
            var partitionReaderID = 1L
            var previousAcquirerJob: Job? = null
            for (partitionReader in partitionReaders) {
                val (acquirerJob: Job, readerJob: Deferred<Result<PartitionReadCheckpoint>>) =
                    asyncReadPartition(
                        partitionsCreatorID,
                        partitionReaderID,
                        partitionReader,
                        previousAcquirerJob,
                    )
                previousAcquirerJob = acquirerJob
                scheduledPartitionReaders[partitionReaderID++] = readerJob
            }
            // Wait for all PartitionReader coroutines to complete.
            awaitAllPartitionReaders(scheduledPartitionReaders)
            partitionsCreatorID++
        }
    }

    private suspend fun createPartitions(partitionsCreatorID: Long): List<PartitionReader> {
        val partitionsCreator: PartitionsCreator = run {
            for (factory in root.partitionsCreatorFactories) {
                log.info { "Attempting bootstrap using ${factory::class}." }
                return@run factory.make(feedBootstrap) ?: continue
            }
            throw SystemErrorException(
                "Unable to bootstrap for feed $feed with ${root.partitionsCreatorFactories}"
            )
        }
        withContext(ctx("round-$partitionsCreatorID-acquire-resources")) {
            acquirePartitionsCreatorResources(partitionsCreatorID, partitionsCreator)
        }
        if (1L == partitionsCreatorID) {
            root.streamStatusManager.notifyStarting(feed)
        }
        return withContext(ctx("round-$partitionsCreatorID-create-partitions")) {
            createPartitionsWithResources(partitionsCreatorID, partitionsCreator)
        }
    }

    private suspend fun acquirePartitionsCreatorResources(
        partitionsCreatorID: Long,
        partitionsCreator: PartitionsCreator,
    ) {
        while (true) {
            val status: PartitionsCreator.TryAcquireResourcesStatus =
            // Resource acquisition always executes serially.
            root.resourceAcquisitionMutex.withLock { partitionsCreator.tryAcquireResources() }
            if (status == PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN) break
            root.waitForResourceAvailability()
        }
        log.info {
            "acquired resources to create partitions " +
                "for '${feed.label}' in round $partitionsCreatorID"
        }
    }

    private suspend fun createPartitionsWithResources(
        partitionsCreatorID: Long,
        partitionsCreator: PartitionsCreator,
    ): List<PartitionReader> {
        log.info { "creating partitions for '${feed.label}' in round $partitionsCreatorID" }
        return try {
            partitionsCreator.run()
        } finally {
            log.info {
                "releasing resources acquired to create partitions " +
                    "for '${feed.label}' in round $partitionsCreatorID"
            }
            partitionsCreator.releaseResources()
            root.notifyResourceAvailability()
        }
    }

    private suspend fun asyncReadPartition(
        partitionsCreatorID: Long,
        partitionReaderID: Long,
        partitionReader: PartitionReader,
        previousAcquirerJob: Job?,
    ): Pair<Job, Deferred<Result<PartitionReadCheckpoint>>> {
        // Create resource acquisition job.
        // Resource acquisition needs to be asynchronous because it may block for an indeterminate
        // amount of time
        // which would prevent PartitionReader instances which have already started and completed
        // from either
        // emitting a checkpoint or triggering cancellations.
        val acquirerJobNameSuffix =
            "round-$partitionsCreatorID-partition-$partitionReaderID-acquire-resources"
        val acquirerJob: Job =
            CoroutineScope(ctx(acquirerJobNameSuffix)).launch {
                // Wait for the previous PartitionReader to acquire resources first ...
                previousAcquirerJob?.join()
                // ... before acquiring resources for this PartitionReader.
                acquirePartitionReaderResources(
                    partitionsCreatorID,
                    partitionReaderID,
                    partitionReader,
                )
            }
        // Create reader job which waits on the acquirer job.
        val readerJobNameSuffix = "round-$partitionsCreatorID-partition-$partitionReaderID-read"
        val readerJob: Deferred<Result<PartitionReadCheckpoint>> =
            CoroutineScope(ctx(readerJobNameSuffix)).async {
                // Poke-catch all exceptions, these will be handled further on.
                runCatching {
                    // Acquire resources first.
                    acquirerJob.join()
                    // Read partition.
                    readPartitionWithResources(
                        partitionsCreatorID,
                        partitionReaderID,
                        partitionReader,
                    )
                }
            }
        return acquirerJob to readerJob
    }

    private suspend fun acquirePartitionReaderResources(
        partitionsCreatorID: Long,
        partitionReaderID: Long,
        partitionReader: PartitionReader,
    ) {
        while (true) {
            val status: PartitionReader.TryAcquireResourcesStatus =
            // Resource acquisition always executes serially.
            root.resourceAcquisitionMutex.withLock { partitionReader.tryAcquireResources() }
            if (status == PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN) break
            root.waitForResourceAvailability()
        }
        log.info {
            "acquired resources to read partition $partitionReaderID for '${feed.label}' in round $partitionsCreatorID"
        }
    }

    private suspend fun readPartitionWithResources(
        partitionsCreatorID: Long,
        partitionReaderID: Long,
        partitionReader: PartitionReader,
    ): PartitionReadCheckpoint {
        log.info {
            "reading partition $partitionReaderID " +
                "for '${feed.label}' in round $partitionsCreatorID"
        }
        var checkpoint: PartitionReadCheckpoint
        try {
            if (partitionReader is UnlimitedTimePartitionReader) {
                partitionReader.run()
            } else {
                log.info {
                    "Running partition reader with ${root.timeout.toKotlinDuration()} timeout"
                }
                withTimeout(root.timeout.toKotlinDuration()) { partitionReader.run() }
            }
            log.info {
                "completed reading partition $partitionReaderID " +
                    "for '${feed.label}' in round $partitionsCreatorID"
            }
            checkpoint = partitionReader.checkpoint()
        } catch (_: TimeoutCancellationException) {
            log.info {
                "timed out reading partition $partitionReaderID " +
                    "for '${feed.label}' in round $partitionsCreatorID"
            }
            checkpoint = partitionReader.checkpoint()
        } finally {
            log.info {
                "releasing resources acquired to read partition $partitionReaderID " +
                    "for '${feed.label}' in round $partitionsCreatorID"
            }
            partitionReader.releaseResources()
            root.notifyResourceAvailability()
        }
        log.info {
            "read ${checkpoint.numRecords} record(s) from partition $partitionReaderID " +
                "for '${feed.label}' in round $partitionsCreatorID"
        }
        return checkpoint
    }

    private suspend fun awaitAllPartitionReaders(
        scheduled: Map<Long, Deferred<Result<PartitionReadCheckpoint>>>,
    ) {
        fun label(partitionReaderID: Long): String =
            "partition $partitionReaderID / ${scheduled.size} for '${feed.label}'"
        // This map stores known results for all  PartitionReader instances.
        val results = mutableMapOf<Long, Result<PartitionReadCheckpoint>>()
        // Although the PartitionReader instances run concurrently, the FeedReader mimics serial
        // execution.
        // This simplifies publishing checkpoints of forward progress.
        // The following var tracks which PartitionReader is due next.
        var pendingPartitionReaderID = 1L
        // Loop until all PartitionReader instances have completed one way or another.
        while (results.size < scheduled.size) {
            // Wait for one of them which hasn't yet completed to complete.
            val completedIDs: Set<Long> = results.keys.toSet()
            val (completedPartitionReaderID: Long, result: Result<PartitionReadCheckpoint>) =
                select {
                    for ((partitionReaderID, deferred) in scheduled) {
                        if (partitionReaderID !in completedIDs) {
                            deferred.onAwait { partitionReaderID to it }
                        }
                    }
                }
            // If the completed coroutine failed, cancel the coroutines for all PartitionReaders
            // which are "later" as far as the mimicked order of execution is concerned.
            // Everything they've done and are going to do is going to be wasted anyway
            // so make them finish ASAP.
            result.onFailure { exception: Throwable ->
                log.warn(exception) { "exception thrown in ${label(completedPartitionReaderID)}" }
                val message = "canceled due to failure of ${label(completedPartitionReaderID)}"
                for ((partitionReaderID, deferred) in scheduled) {
                    if (partitionReaderID > completedPartitionReaderID) {
                        log.warn { "canceling ${label(partitionReaderID)}" }
                        val cancellationException = CancellationException(message, exception)
                        deferred.cancel(cancellationException)
                        // Don't select from this one in the next iteration.
                        // We don't want select to fail by throwing a CancellationException.
                        results[partitionReaderID] = Result.failure(cancellationException)
                    }
                }
            }
            // Store the result and try to make forward progress in the mimicked serial execution.
            results[completedPartitionReaderID] = result
            try {
                while (true) {
                    // Exit the loop if the pending result doesn't exist yet.
                    val pendingResult: Result<PartitionReadCheckpoint> =
                        results[pendingPartitionReaderID] ?: break
                    // Re-throw any exception that the PartitionReader may have thrown.
                    // Otherwise, update the StateManager with the forward progress.
                    log.info {
                        "processing result (success = ${pendingResult.isSuccess}) from reading " +
                            label(pendingPartitionReaderID)
                    }
                    val (
                        opaqueStateValue: OpaqueStateValue, numRecords: Long, partitionId: String?
                    ) =
                        pendingResult.getOrThrow()
                    root.stateManager
                        .scoped(feed)
                        .set(
                            opaqueStateValue,
                            numRecords,
                            partitionId,
                            when (dataChannelMedium) {
                                // State messages in SOCKET mode have an incrementing integer ID.
                                SOCKET -> stateId.getAndIncrement()
                                STDIO -> null
                            }
                        )
                    log.info {
                        "updated state of '${feed.label}', moved it $numRecords record(s) forward"
                    }
                    // Move on to the next PartitionReader instance.
                    pendingPartitionReaderID++
                }
            } finally {
                // Publish a checkpoint if applicable.
                maybeCheckpoint(false)
            }
        }
    }

    private suspend fun ctx(nameSuffix: String): CoroutineContext =
        coroutineContext + ThreadRenamingCoroutineName("${feed.label}-$nameSuffix") + Dispatchers.IO

    // Acquires resources for the OutputMessageRouter and executes the provided action with it
    private fun attemptWithMessageRouter(doWithRouter: (OutputMessageRouter) -> Unit) {
        val acquiredSocket: SocketResource.AcquiredSocket? =
            resourceAcquirer.tryAcquireResource(ResourceType.RESOURCE_OUTPUT_SOCKET)
                as? SocketResource.AcquiredSocket

        acquiredSocket?.use {
            OutputMessageRouter(
                    feedBootstrap.dataChannelMedium,
                    feedBootstrap.dataChannelFormat,
                    feedBootstrap.outputConsumer,
                    emptyMap(),
                    feedBootstrap,
                    mapOf(ResourceType.RESOURCE_OUTPUT_SOCKET to acquiredSocket),
                )
                .use { doWithRouter(it) }
        }
    }

    // In STDIO mode (legacy) we emit state messages to standard output.
    // In SOCKET mode we emil state messages to stadard output and also states and stream statuses
    // are sent over sockets,
    // According to the configured format (json or protobuf).
    // This function emit to stdout and also uses running partition readers to emit pending states
    // and stream statuses.
    // Finally when all readers are done, it acquires socket resource and use it to emit the pending
    // states and stream statuses.
    private fun maybeCheckpoint(finalCheckpoint: Boolean) {
        val stateMessages: List<AirbyteStateMessage> = root.stateManager.checkpoint()
        if (stateMessages.isEmpty() && PartitionReader.pendingStates.isEmpty()) {
            return
        }

        // Legacy flow - checkpoint state messages to stdout
        if (dataChannelMedium == STDIO) {
            log.info { "checkpoint of ${stateMessages.size} state message(s)" }
            for (stateMessage in stateMessages) {
                root.outputConsumer.accept(stateMessage)
            }
            return
        }
        // Socket flow - checkpoint state messages to stdout and also to one connected socket
        log.info { "checkpoint of ${stateMessages.size} state message(s)" }
        for (stateMessage in stateMessages) {
            if (stateMessage.type == AirbyteStateMessage.AirbyteStateType.GLOBAL) {
                stateMessage.setAdditionalProperty("id", globalStateId.getAndIncrement())
                // Every global state message has a global partition ID, even if it's not
                // checkpointing the global partition.
                // This is requirement from destination in socket mode.
                if (stateMessage.additionalProperties["partition_id"] == null) {
                    // If the global partition ID is not set, we generate a new unique one.
                    stateMessage.setAdditionalProperty("partition_id", generatePartitionId(4))
                }
            }

            // checkpoint state messages to stdout
            root.outputConsumer.accept(stateMessage)

            // Queue the state message for transmission over sockets.
            PartitionReader.pendingStates.add(stateMessage)
        }

        // If this is the final checkpoint, we initialize the OutputMessageRouter and emit all
        // pending messages through it
        if (finalCheckpoint) {
            attemptWithMessageRouter {
                while (PartitionReader.pendingStates.isNotEmpty()) {
                    val message: Any = PartitionReader.pendingStates.poll() ?: break
                    when (message) {
                        is AirbyteStateMessage -> {
                            it.acceptNonRecord(message)
                        }
                        is AirbyteStreamStatusTraceMessage -> {
                            it.acceptNonRecord(message)
                        }
                        else -> {
                            log.warn {
                                "Unknown message type in pending states queue: ${message::class}"
                            }
                            continue // Skip unknown messages.
                        }
                    }
                }
            }
        }
    }
}
