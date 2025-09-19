/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.GlobalCheckpoint
import io.airbyte.cdk.load.message.GlobalSnapshotCheckpoint
import io.airbyte.cdk.load.util.use
import io.airbyte.cdk.output.OutputConsumer
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentSkipListMap
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
    val socketMode: Boolean,
    val namespaceMapper: NamespaceMapper
) {
    private val log = KotlinLogging.logger {}
    private val storedCheckpointsLock = Mutex()
    private val lastFlushTimeMs = AtomicLong(0L)
    private val committedCount: ConcurrentHashMap<DestinationStream.Descriptor, CheckpointValue> =
        ConcurrentHashMap<DestinationStream.Descriptor, CheckpointValue>()

    data class GlobalCheckpointHolder(val checkpointMessage: Reserved<CheckpointMessage>)

    private val checkpointsAreGlobal: AtomicReference<Boolean?> = AtomicReference(null)
    private val streamCheckpoints:
        ConcurrentHashMap<
            DestinationStream.Descriptor,
            ConcurrentSkipListMap<CheckpointKey, Reserved<CheckpointMessage>>
        > =
        ConcurrentHashMap()
    private val globalCheckpoints = ConcurrentSkipListMap<CheckpointKey, GlobalCheckpointHolder>()
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
            if (checkpointsAreGlobal.updateAndGet { it == true } != false) {
                throw IllegalStateException(
                    "Global checkpoints cannot be mixed with non-global checkpoints"
                )
            }

            val indexedMessages: ConcurrentSkipListMap<CheckpointKey, Reserved<CheckpointMessage>> =
                streamCheckpoints.getOrPut(streamDescriptor) { ConcurrentSkipListMap() }
            indexedMessages[checkpointKey] = checkpointMessage

            log.info { "Added checkpoint for stream: $streamDescriptor at index: $checkpointKey" }
        }
    }

    // TODO: Is it an error if we don't get all the streams every time?
    suspend fun addGlobalCheckpoint(
        checkpointKey: CheckpointKey,
        checkpointMessage: Reserved<CheckpointMessage>
    ) {
        storedCheckpointsLock.withLock {
            if (checkpointsAreGlobal.updateAndGet { it != false } != true) {
                throw IllegalStateException(
                    "Global checkpoint cannot be mixed with non-global checkpoints"
                )
            }

            globalCheckpoints[checkpointKey] = GlobalCheckpointHolder(checkpointMessage)
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
            when (checkpointsAreGlobal.get()) {
                null -> log.info { "No checkpoints to flush" }
                true -> flushGlobalCheckpoints()
                false -> flushStreamCheckpoints()
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
                if (head.value.checkpointMessage.value is GlobalSnapshotCheckpoint) {
                    checkSnapshotStreams(head)
                } else {
                    checkGlobalStreams(head.key, head.value.checkpointMessage.value.sourceStats)
                }

            if (allStreamsPersisted) {
                flushGlobalState(checkpointKey = head.key, checkpoint = head.value)
            } else {
                log.debug { "Not flushing global checkpoint ${head.key}" }
                break
            }
        }
    }

    private fun checkGlobalStreams(
        key: CheckpointKey,
        sourceReportedCount: CheckpointMessage.Stats?
    ): Boolean {
        val allCommitted =
            catalog.streams.all {
                syncManager
                    .getStreamManager(it.mappedDescriptor)
                    .areRecordsPersistedForCheckpoint(key.checkpointId)
            }
        if (!socketMode) return allCommitted
        if (!allCommitted) return false
        val total =
            catalog.streams.sumOf {
                syncManager
                    .getStreamManager(it.mappedDescriptor)
                    .committedCount(key.checkpointId)
                    .records
            }
        return total == sourceReportedCount!!.recordCount
    }

    private fun checkSnapshotStreams(
        entry: MutableMap.MutableEntry<CheckpointKey, GlobalCheckpointHolder>
    ): Boolean {
        val snapshot = entry.value.checkpointMessage.value as GlobalSnapshotCheckpoint
        var committedFromPartitions = 0L
        val allPersisted =
            snapshot.streamCheckpoints.all { (descriptor, innerKey) ->
                val manager = syncManager.getStreamManager(descriptor)
                committedFromPartitions += manager.committedCount(innerKey.checkpointId).records
                manager.areRecordsPersistedForCheckpoint(innerKey.checkpointId)
            }

        val expected = snapshot.sourceStats!!.recordCount
        if (!allPersisted) return false
        return if (committedFromPartitions == expected) {
            true
        } else {
            checkGlobalStreams(
                snapshot.checkpointKey!!,
                CheckpointMessage.Stats(recordCount = expected - committedFromPartitions)
            )
        }
    }

    private suspend fun flushGlobalState(
        checkpointKey: CheckpointKey,
        checkpoint: GlobalCheckpointHolder
    ) {
        log.info { "Flushing global checkpoint with key $checkpointKey" }
        if (socketMode) {
            // We have already verified before deciding to call flushGlobalState in socket mode that
            // the destination
            // and source counts match thus it's safe to set the destinationStats to source stats
            // value
            checkpoint.checkpointMessage.value.updateStats(
                destinationStats = checkpoint.checkpointMessage.value.sourceStats
            )
        }

        if (checkpoint.checkpointMessage.value is GlobalSnapshotCheckpoint) {
            checkpoint.checkpointMessage.value.streamCheckpoints.map { (mappedDescriptor, innerKey)
                ->
                val manager = syncManager.getStreamManager(mappedDescriptor)

                val checkPointValue = manager.committedCount(innerKey.checkpointId)
                committedCount.increment(mappedDescriptor, checkPointValue)
            }
        }
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

        if (socketMode) {
            updateCountsForStreamsWithinGlobalMessage(checkpoint)
        }

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

    private fun updateCountsForStreamsWithinGlobalMessage(checkpoint: GlobalCheckpointHolder) {
        val checkpointMap: Map<DestinationStream.Descriptor, CheckpointMessage.Checkpoint> =
            when (val value = checkpoint.checkpointMessage.value) {
                is GlobalSnapshotCheckpoint -> value.checkpoints
                is GlobalCheckpoint -> value.checkpoints
                else -> error("Unsupported checkpoint type: ${value::class.simpleName}")
            }.associateBy { namespaceMapper.map(namespace = it.unmappedNamespace, it.unmappedName) }

        catalog.streams
            .mapNotNull { stream ->
                val committedData = committedCount[stream.mappedDescriptor]
                val streamLevelCheckpoint = checkpointMap[stream.mappedDescriptor]

                if (committedData != null && streamLevelCheckpoint != null) {
                    Pair(streamLevelCheckpoint, committedData)
                } else null
            }
            .forEach { (checkpoint, committedData) ->
                checkpoint.updateStats(
                    committedData.records,
                    committedData.serializedBytes,
                    committedData.rejectedRecords,
                )
            }
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
                    if (
                        socketMode && delta.records != nextMessage.value.sourceStats!!.recordCount
                    ) {
                        return
                    }
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
class FreeingAnnotatingCheckpointConsumer(
    private val consumer: OutputConsumer,
) : suspend (Reserved<CheckpointMessage>, Long, Long, Long) -> Unit {
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
