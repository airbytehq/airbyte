/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.GlobalSnapshotCheckpoint
import io.airbyte.cdk.load.util.use
import io.airbyte.cdk.output.OutputConsumer
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.TreeMap
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference
import kotlinx.coroutines.delay
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

/**
 * Represents the checkpoint's order (stream-level for stream state, global for global state).
 * Specifically, no state shall be released for CheckpointIndex N until all state for
 * CheckpointIndexes 1..N-1 have been released.
 *
 * Begins at 1.
 */
@JvmInline value class CheckpointIndex(val value: Int)

/**
 * Uniquely identifies the checkpoint. This is used by the StreamManager to count persisted records
 * against the checkpoint. Specifically, it should be passed to the StreamManager to determine data
 * sufficiency.
 *
 * Unique, unordered.
 */
@JvmInline value class CheckpointId(val value: String)

/**
 * Used internally by the checkpoint manager to maintain ordered maps of checkpoints. Ordered by
 * index only.
 */
data class CheckpointKey(
    val checkpointIndex: CheckpointIndex,
    val checkpointId: CheckpointId,
) : Comparable<CheckpointKey> {
    // order only by index
    override fun compareTo(other: CheckpointKey): Int {
        return this.checkpointIndex.value - other.checkpointIndex.value
    }
}

enum class CheckpointType {
    GLOBAL,
    SNAPSHOT,
    STREAM
}

/**
 * Message-type agnostic streams checkpoint manager.
 *
 * Accepts global and stream checkpoints, and enforces that stream and global checkpoints are not
 * mixed. Determines ready checkpoints by querying the StreamsManager for the checkpoint of the
 * record index range associated with each checkpoint message.
 *
 * TODO: Force flush on a configured schedule
 *
 * TODO: Ensure that checkpoint is flushed at the end, and require that all checkpoints be flushed
 * before the destination can succeed.
 */
class CheckpointManager(
    val catalog: DestinationCatalog,
    val syncManager: SyncManager,
    val outputConsumer: suspend (Reserved<CheckpointMessage>, Long, Long, Long) -> Unit,
    val timeProvider: TimeProvider,
) {
    private val log = KotlinLogging.logger {}
    private val storedCheckpointsLock = Mutex()
    private val lastFlushTimeMs = AtomicLong(0L)
    private val committedCount: ConcurrentHashMap<DestinationStream.Descriptor, CheckpointValue> =
        ConcurrentHashMap<DestinationStream.Descriptor, CheckpointValue>()

    data class GlobalCheckpoint(val checkpointMessage: Reserved<CheckpointMessage>)

    private val checkpointType: AtomicReference<CheckpointType?> = AtomicReference(null)
    private val streamCheckpoints:
        ConcurrentHashMap<
            DestinationStream.Descriptor, TreeMap<CheckpointKey, Reserved<CheckpointMessage>>> =
        ConcurrentHashMap()
    private val snapshotStreamCheckpoints:
        ConcurrentHashMap<
            DestinationStream.Descriptor, TreeMap<CheckpointKey, Reserved<CheckpointMessage>>> =
        ConcurrentHashMap()
    private val globalCheckpoints: TreeMap<CheckpointKey, GlobalCheckpoint> = TreeMap()
    private val lastCheckpointKeyEmitted =
        ConcurrentHashMap<DestinationStream.Descriptor, CheckpointKey>()

    init {
        lastFlushTimeMs.set(timeProvider.currentTimeMillis())
    }

    suspend fun addStreamCheckpoint(
        streamDescriptor: DestinationStream.Descriptor,
        checkpointKey: CheckpointKey,
        checkpointMessage: Reserved<CheckpointMessage>,
    ) {
        storedCheckpointsLock.withLock {
            val previousCheckpointType = checkpointType.getAndUpdate { CheckpointType.STREAM }
            if (previousCheckpointType != null && previousCheckpointType != CheckpointType.STREAM) {
                throw IllegalStateException(
                    "Global checkpoints cannot be mixed with non-global checkpoints"
                )
            }

            val indexedMessages: TreeMap<CheckpointKey, Reserved<CheckpointMessage>> =
                streamCheckpoints.getOrPut(streamDescriptor) { TreeMap() }
            indexedMessages[checkpointKey] = checkpointMessage

            log.info { "Added checkpoint for stream: $streamDescriptor at index: $checkpointKey" }
        }
    }

    suspend fun addSnapshotCheckpoint(
        checkpointKey: CheckpointKey,
        checkpointMessage: Reserved<CheckpointMessage>,
    ) {
        storedCheckpointsLock.withLock {
            val previousCheckpointType = checkpointType.getAndUpdate { CheckpointType.SNAPSHOT }
            if (
                previousCheckpointType != null && previousCheckpointType != CheckpointType.SNAPSHOT
            ) {
                throw IllegalStateException(
                    "Global checkpoints cannot be mixed with non-global checkpoints"
                )
            }

            if (checkpointMessage.value is GlobalSnapshotCheckpoint) {
                checkpointMessage.value.streamCheckpoints.forEach {
                    (streamDescriptor, checkpointKey) ->
                    val indexedMessages: TreeMap<CheckpointKey, Reserved<CheckpointMessage>> =
                        snapshotStreamCheckpoints.getOrPut(streamDescriptor) { TreeMap() }
                    indexedMessages[checkpointKey] = checkpointMessage
                    log.info {
                        "Added snapshot checkpoint for stream: $streamDescriptor at index: $checkpointKey"
                    }
                }

                globalCheckpoints[checkpointKey] = GlobalCheckpoint(checkpointMessage)
                log.info { "Added global snapshot checkpoint with key $checkpointKey" }
            }
        }
    }

    // TODO: Is it an error if we don't get all the streams every time?
    suspend fun addGlobalCheckpoint(
        checkpointKey: CheckpointKey,
        checkpointMessage: Reserved<CheckpointMessage>
    ) {
        storedCheckpointsLock.withLock {
            val previousCheckpointType = checkpointType.getAndUpdate { CheckpointType.GLOBAL }
            if (previousCheckpointType != null && previousCheckpointType != CheckpointType.GLOBAL) {
                throw IllegalStateException(
                    "Global checkpoint cannot be mixed with non-global checkpoints"
                )
            }

            globalCheckpoints[checkpointKey] = GlobalCheckpoint(checkpointMessage)
            log.info { "Added global checkpoint with key $checkpointKey" }
        }
    }

    suspend fun flushReadyCheckpointMessages() {
        storedCheckpointsLock.withLock {
            /*
               Iterate over the checkpoints in order, evicting each that passes
               the persistence check. If a checkpoint is not persisted, then
               we can break the loop since the checkpoints are ordered. For global
               checkpoints, all streams must be persisted up to the checkpoint.
            */
            when (checkpointType.get()) {
                null -> log.info { "No checkpoints to flush" }
                CheckpointType.GLOBAL -> flushGlobalCheckpoints()
                CheckpointType.STREAM -> flushStreamCheckpoints()
                CheckpointType.SNAPSHOT -> flushSnapshotCheckpoints()
            }
        }
    }

    private suspend fun flushSnapshotCheckpoints() {
        if (snapshotStreamCheckpoints.isEmpty() && globalCheckpoints.isEmpty()) {
            log.debug { "No global snapshot checkpoints to flush" }
            return
        }
        val allStreamsPersisted =
            catalog.streams.all { stream ->
                val manager = syncManager.getStreamManager(stream.mappedDescriptor)
                val streamCheckpoints = snapshotStreamCheckpoints[stream.mappedDescriptor]
                val persistedResults = mutableListOf<Boolean>()

                streamCheckpoints?.let {
                    /*
                     * If there are checkpoints for the given stream, check that records have been
                     * persisted for each checkpoint ID for the stream.  If all are true/have been
                     * persisted up to the associated checkpoint ID, then the stream is up to date.
                     * If the stream does not have any checkpoints stored or is not currently tracked
                     * by the manager, return true so that the flush will continue as there is
                     * nothing for that stream to ensure that it has been persisted.
                     */
                    while (streamCheckpoints.isNotEmpty()) {
                        val (nextCheckpointKey, _) = streamCheckpoints.firstEntry() ?: break
                        val persisted =
                            manager.areRecordsPersistedForCheckpoint(nextCheckpointKey.checkpointId)
                        persistedResults.add(persisted)
                        if (persisted) {
                            // If the stream has been persisted to the checkpoint ID, remove it from
                            // the list so that we don't scan it again.
                            streamCheckpoints.remove(nextCheckpointKey)
                        } else {
                            // If any stream has not been persisted, immediately break the loop
                            break
                        }
                    }
                }

                persistedResults.all { it }
            }

        while (globalCheckpoints.isNotEmpty()) {
            val head = globalCheckpoints.firstEntry() ?: break
            if (allStreamsPersisted) {
                flushGlobalState(checkpointKey = head.key, checkpoint = head.value)
            } else {
                log.debug { "Not flushing global checkpoint ${head.key}" }
                break
            }
        }
    }

    private suspend fun flushGlobalCheckpoints() {
        if (globalCheckpoints.isEmpty()) {
            log.debug { "No global checkpoints to flush" }
            return
        }
        while (globalCheckpoints.isNotEmpty()) {
            val head = globalCheckpoints.firstEntry() ?: break
            val previousStateEmitted =
                catalog.streams.all { stream ->
                    wasPreviousStateEmitted(stream.mappedDescriptor, head.key.checkpointIndex)
                }
            if (!previousStateEmitted) {
                log.debug { "State for checkpoint before ${head.key} has not been emitted yet." }
                break
            }

            val allStreamsPersisted =
                if (syncManager.hasGlobalCount(head.key.checkpointId)) {
                    syncManager.areAllStreamsPersistedForGlobalCheckpoint(head.key.checkpointId)
                } else {
                    catalog.streams.all {
                        syncManager
                            .getStreamManager(it.mappedDescriptor)
                            .areRecordsPersistedForCheckpoint(head.key.checkpointId)
                    }
                }

            if (allStreamsPersisted) {
                flushGlobalState(checkpointKey = head.key, checkpoint = head.value)
            } else {
                log.debug { "Not flushing global checkpoint ${head.key}" }
                break
            }
        }
    }

    private suspend fun flushGlobalState(
        checkpointKey: CheckpointKey,
        checkpoint: GlobalCheckpoint
    ) {
        log.info { "Flushing global checkpoint with key $checkpointKey" }

        val aggregate =
            catalog.streams
                .map { stream ->
                    val delta =
                        syncManager
                            .getStreamManager(stream.mappedDescriptor)
                            .committedCount(checkpointKey.checkpointId)

                    /* increment() returns the new aggregate for this stream. */
                    committedCount.increment(stream.mappedDescriptor, delta)
                }
                .reduce { acc, inc -> acc.plus(inc) }

        sendStateMessage(
            checkpoint.checkpointMessage,
            checkpointKey,
            catalog.streams.map { it.mappedDescriptor },
            aggregate.records,
            aggregate.serializedBytes,
            aggregate.rejectedRecords,
        )
        globalCheckpoints.remove(checkpointKey) // don't remove until after we've successfully sent
    }

    private fun ConcurrentHashMap<DestinationStream.Descriptor, CheckpointValue>.increment(
        descriptor: DestinationStream.Descriptor,
        delta: CheckpointValue,
    ): CheckpointValue = merge(descriptor, delta) { acc, inc -> acc.plus(inc) }!!

    private suspend fun flushStreamCheckpoints() {
        val noCheckpointStreams = mutableSetOf<DestinationStream.Descriptor>()
        for (stream in catalog.streams) {

            val manager = syncManager.getStreamManager(stream.mappedDescriptor)
            val streamCheckpoints = streamCheckpoints[stream.mappedDescriptor]
            if (streamCheckpoints == null) {
                noCheckpointStreams.add(stream.mappedDescriptor)

                continue
            }
            while (true) {
                val (nextCheckpointKey, nextMessage) = streamCheckpoints.firstEntry() ?: break

                if (
                    !wasPreviousStateEmitted(
                        stream.mappedDescriptor,
                        nextCheckpointKey.checkpointIndex
                    )
                ) {
                    break
                }

                val persisted =
                    manager.areRecordsPersistedForCheckpoint(nextCheckpointKey.checkpointId)
                if (persisted) {

                    val delta = manager.committedCount(nextCheckpointKey.checkpointId)
                    val aggregate = committedCount.increment(stream.mappedDescriptor, delta)

                    nextMessage.value.updateStats(
                        destinationStats =
                            CheckpointMessage.Stats(
                                recordCount = delta.records,
                                rejectedRecordCount = delta.rejectedRecords,
                            )
                    )
                    sendStateMessage(
                        nextMessage,
                        nextCheckpointKey,
                        listOf(stream.mappedDescriptor),
                        aggregate.records,
                        aggregate.serializedBytes,
                        aggregate.rejectedRecords,
                    )

                    log.info {
                        "Flushed checkpoint for stream: ${stream.mappedDescriptor} at index: $nextCheckpointKey (records=${aggregate.records}, bytes=${aggregate.serializedBytes})"
                    }

                    // don't remove until after we've successfully sent
                    streamCheckpoints.remove(nextCheckpointKey)
                } else {
                    log.debug {
                        val expectedCount =
                            manager.readCountForCheckpoint(nextCheckpointKey.checkpointId)
                        val committedCount =
                            manager.persistedRecordCountForCheckpoint(
                                nextCheckpointKey.checkpointId
                            )
                        "Not flushing next checkpoint for index $nextCheckpointKey (committed $committedCount records of expected $expectedCount)"
                    }
                    break
                }
            }
        }
        if (noCheckpointStreams.isNotEmpty()) {
            log.debug { "No checkpoints for streams: $noCheckpointStreams" }
        }
    }

    private fun wasPreviousStateEmitted(
        descriptor: DestinationStream.Descriptor,
        nextCheckpointIndex: CheckpointIndex
    ): Boolean {
        val lastIndex = lastCheckpointKeyEmitted[descriptor]?.checkpointIndex?.value ?: 0
        if (nextCheckpointIndex.value != lastIndex + 1) {
            // This state cannot be emitted, because we have not emitted the previous.
            // (This implies that we also have not received it yet, or else it would
            // have been first in this table.)
            log.debug {
                "Cannot flush checkpoint for index $nextCheckpointIndex because previous index has not been flushed."
            }
            return false
        }

        return true
    }

    private suspend fun sendStateMessage(
        checkpointMessage: Reserved<CheckpointMessage>,
        checkpointKey: CheckpointKey,
        streamCheckpoints: List<DestinationStream.Descriptor>,
        totalRecords: Long,
        totalBytes: Long,
        totalRejectedRecords: Long,
    ) {
        streamCheckpoints.forEach { stream -> lastCheckpointKeyEmitted[stream] = checkpointKey }
        lastFlushTimeMs.set(timeProvider.currentTimeMillis())
        outputConsumer.invoke(checkpointMessage, totalRecords, totalBytes, totalRejectedRecords)
    }

    suspend fun awaitAllCheckpointsFlushed() {
        while (true) {
            val allCheckpointsFlushed =
                storedCheckpointsLock.withLock {
                    globalCheckpoints.isEmpty() && streamCheckpoints.all { it.value.isEmpty() }
                }
            if (allCheckpointsFlushed) {
                log.info { "All checkpoints flushed" }
                break
            }
            log.info { "Waiting for all checkpoints to flush" }
            // Not usually a fan of busywaiting, but it's extremely unlikely we
            // get here without more than a handful of stragglers
            delay(1000L)
            flushReadyCheckpointMessages()
        }
    }
}

@SuppressFBWarnings(
    "NP_NONNULL_PARAM_VIOLATION",
    justification = "message is guaranteed to be non-null by Kotlin's type system"
)
@Singleton
class FreeingAnnotatingCheckpointConsumer(private val consumer: OutputConsumer) :
    suspend (Reserved<CheckpointMessage>, Long, Long, Long) -> Unit {
    override suspend fun invoke(
        message: Reserved<CheckpointMessage>,
        totalRecords: Long,
        totalBytes: Long,
        totalRejectedRecords: Long,
    ) {
        message.use {
            val outMessage =
                it.value
                    .apply {
                        updateStats(
                            totalRecords = totalRecords,
                            totalBytes = totalBytes,
                            totalRejectedRecords = totalRejectedRecords,
                        )
                    }
                    .asProtocolMessage()
            consumer.accept(outMessage)
        }
    }
}
