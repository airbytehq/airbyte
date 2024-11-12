/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.util.ThreadRenamingCoroutineName
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.github.oshai.kotlinlogging.KotlinLogging
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
) {
    private val log = KotlinLogging.logger {}

    private val feedBootstrap: FeedBootstrap<*> =
        FeedBootstrap.create(root.outputConsumer, root.metaFieldDecorator, root.stateManager, feed)

    /** Reads records from this [feed]. */
    suspend fun read() {
        log.info { "SGX reading stream${feed.label}" }
        var partitionsCreatorID = 1L
        while (true) {
            // Create PartitionReader instances.
            val partitionReaders: List<PartitionReader> = createPartitions(partitionsCreatorID)
            if (partitionReaders.isEmpty()) {
                log.info {
                    "no more partitions to read for '${feed.label}' in round $partitionsCreatorID"
                }
                // Publish a checkpoint if applicable.
                maybeCheckpoint()
                // Publish stream completion.
                root.streamStatusManager.notifyComplete(feed)
                break
            } else {
                log.info {
                    "SGX reading partition $partitionsCreatorID for feed ${feed.label}. partitionReaders=${partitionReaders}"
                }
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
        } catch (e: TimeoutCancellationException) {
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
                    val (opaqueStateValue: OpaqueStateValue, numRecords: Long) =
                        pendingResult.getOrThrow()
                    root.stateManager.scoped(feed).set(opaqueStateValue, numRecords)
                    log.info {
                        "updated state of '${feed.label}', moved it $numRecords record(s) forward"
                    }
                    // Move on to the next PartitionReader instance.
                    pendingPartitionReaderID++
                }
            } finally {
                // Publish a checkpoint if applicable.
                maybeCheckpoint()
            }
        }
    }

    private suspend fun ctx(nameSuffix: String): CoroutineContext =
        coroutineContext + ThreadRenamingCoroutineName("${feed.label}-$nameSuffix") + Dispatchers.IO

    private fun maybeCheckpoint() {
        val stateMessages: List<AirbyteStateMessage> = root.stateManager.checkpoint()
        if (stateMessages.isEmpty()) {
            return
        }
        log.info { "checkpoint of ${stateMessages.size} state message(s)" }
        for (stateMessage in stateMessages) {
            root.outputConsumer.accept(stateMessage)
        }
    }
}
