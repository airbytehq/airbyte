/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.PipelineInputEvent
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.CheckpointMessageWrapped
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.DestinationFileStreamComplete
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import io.airbyte.cdk.load.message.DestinationStreamAffinedMessage
import io.airbyte.cdk.load.message.FileTransferQueueEndOfStream
import io.airbyte.cdk.load.message.FileTransferQueueMessage
import io.airbyte.cdk.load.message.FileTransferQueueRecord
import io.airbyte.cdk.load.message.GlobalCheckpoint
import io.airbyte.cdk.load.message.GlobalCheckpointWrapped
import io.airbyte.cdk.load.message.GlobalSnapshotCheckpoint
import io.airbyte.cdk.load.message.GlobalSnapshotCheckpointWrapped
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineHeartbeat
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.airbyte.cdk.load.message.StreamCheckpointWrapped
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.BatchEndOfStream
import io.airbyte.cdk.load.pipeline.BatchUpdate
import io.airbyte.cdk.load.util.CloseableCoroutine
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicInteger
import org.apache.mina.util.ConcurrentHashSet

/**
 * The stdio and socket input channel differ in subtle and critical ways
 * - record-wise, sockets are cold flows, stdio publishes to a partitioned channel
 * - sockets receive checkpointId on the record, stdio infers from state message order
 * - speed will receive complete/incomplete on all sockets (no need to publish)
 * - because they are flows, sockets don't need memory management; the buffer can serve as the
 * ```
 *    backpressure scheme (note: the exception to this is for file transfer, which forwards the
 *    record after handling the file; and of course obviously for state)
 * ```
 * These differences might diverge/converge as we tune (i.e., because of lock contention with
 * multiple sockets, or because the socket pattern ends up working for stdio as well). For now,
 * since the main difference is what is done with the pipeline events, we'll consolidate bookkeeping
 * into a single class that yields events from DestinationMessage(s). CheckpointIds can be inferred
 * if the record does not provide one.
 */
@Singleton
class PipelineEventBookkeepingRouter(
    private val catalog: DestinationCatalog,
    private val syncManager: SyncManager,
    private val checkpointQueue: QueueWriter<Reserved<CheckpointMessageWrapped>>,
    private val openStreamQueue: QueueWriter<DestinationStream>,
    private val fileTransferQueue: MessageQueue<FileTransferQueueMessage>,
    @Named("batchStateUpdateQueue")
    private val batchStateUpdateQueue: ChannelMessageQueue<BatchUpdate>,
    @Named("numDataChannels") private val numDataChannels: Int,
    @Named("markEndOfStreamAtEndOfSync") private val markEndOfStreamAtEndOfSync: Boolean,
    private val namespaceMapper: NamespaceMapper
) : CloseableCoroutine {
    private val log = KotlinLogging.logger {}
    private val clientCount = AtomicInteger(numDataChannels)
    private val sawEndOfStreamComplete = ConcurrentHashSet<DestinationStream.Descriptor>()
    private val checkpointIndexes = ConcurrentHashMap<DestinationStream.Descriptor, AtomicInteger>()

    init {
        log.info { "Creating bookkeeping router for $numDataChannels data channels" }
    }

    private fun checkpointAtomic(descriptor: DestinationStream.Descriptor) =
        checkpointIndexes.computeIfAbsent(descriptor) { AtomicInteger(1) }

    private fun currentCheckpointKey(
        descriptor: DestinationStream.Descriptor,
    ): CheckpointKey {
        val atomic = checkpointAtomic(descriptor)
        val id = CheckpointId(atomic.get().toString())
        val index = CheckpointIndex(atomic.get())
        return CheckpointKey(checkpointId = id, checkpointIndex = index)
    }

    suspend fun handleStreamMessage(
        message: DestinationStreamAffinedMessage,
        postProcessingCallback: suspend () -> Unit = {},
        unopenedStreams: MutableSet<DestinationStream.Descriptor>
    ): PipelineInputEvent {
        val stream = message.stream
        if (unopenedStreams.remove(stream.mappedDescriptor)) {
            log.info {
                "Saw first record for stream ${stream.mappedDescriptor}; awaiting setup complete"
            }
            syncManager.awaitSetupComplete()
            log.info { "Setup complete, starting stream ${stream.mappedDescriptor}" }
            openStreamQueue.publish(stream)
            syncManager.getOrAwaitStreamLoader(stream.mappedDescriptor)
            log.info { "Initialization for stream ${stream.mappedDescriptor} complete" }
        }
        val manager = syncManager.getStreamManager(stream.mappedDescriptor)

        return when (message) {
            is DestinationRecord -> {
                val record = message.asDestinationRecordRaw()
                val checkpointId = resolveCheckpointId(record.checkpointId, stream.mappedDescriptor)
                manager.incrementReadCount(checkpointId)
                manager.incrementByteCount(record.serializedSizeBytes, checkpointId)
                PipelineMessage(
                    mapOf(checkpointId to CheckpointValue(1, record.serializedSizeBytes)),
                    StreamKey(stream.mappedDescriptor),
                    record,
                    postProcessingCallback
                )
            }
            is DestinationRecordStreamComplete -> {
                log.info { "Read COMPLETE for stream ${stream.mappedDescriptor}" }
                sawEndOfStreamComplete.add(stream.mappedDescriptor)
                if (!markEndOfStreamAtEndOfSync) {
                    manager.markEndOfStream(true)
                }
                PipelineEndOfStream(stream.mappedDescriptor)
            }

            // DEPRECATED: Legacy file transfer
            is DestinationFile -> {
                val checkpointId = resolveCheckpointId(null, stream.mappedDescriptor)
                val index = manager.incrementReadCount(checkpointId)
                fileTransferQueue.publish(
                    FileTransferQueueRecord(stream, message, index, checkpointId)
                )
                PipelineHeartbeat()
            }
            is DestinationFileStreamComplete -> {
                manager.markEndOfStream(true)
                fileTransferQueue.publish(FileTransferQueueEndOfStream(stream))
                PipelineHeartbeat()
            }
        }
    }

    suspend fun handleCheckpoint(reservation: Reserved<CheckpointMessage>) {
        when (val checkpoint = reservation.value) {
            is StreamCheckpoint -> {
                val mappedDescriptor =
                    namespaceMapper.map(
                        checkpoint.checkpoint.unmappedNamespace,
                        checkpoint.checkpoint.unmappedName,
                    )
                val maybeKey = checkpoint.checkpointKey
                if (maybeKey != null) {
                    if (checkpoint.sourceStats == null) {
                        error(
                            "Source stats should always be present when checkpoint key is provided"
                        )
                    }
                }
                val manager = syncManager.getStreamManager(mappedDescriptor)
                val key = resolveCheckpointKey(maybeKey, mappedDescriptor)
                val count = getCounts(key, manager)
                incrementIndex(mappedDescriptor)
                val messageWithCount =
                    checkpoint.withDestinationStats(CheckpointMessage.Stats(count))
                checkpointQueue.publish(
                    reservation.replace(
                        StreamCheckpointWrapped(
                            manager.stream.mappedDescriptor,
                            key,
                            messageWithCount
                        )
                    )
                )
            }
            is GlobalSnapshotCheckpoint -> {
                val snapshotKey =
                    checkpoint.checkpointKey ?: error("checkpointKey should not be null")
                log.debug { "Got a GlobalSnapshotCheckpoint state message" }
                val streamWithKeyAndCount =
                    catalog.streams.map { stream ->
                        if (checkpoint.sourceStats == null) {
                            error(
                                "Source stats should always be present when checkpoint key is provided"
                            )
                        }

                        val streamManager = syncManager.getStreamManager(stream.mappedDescriptor)

                        val innerKey = checkpoint.streamCheckpoints[stream.mappedDescriptor]
                        incrementIndex(stream.mappedDescriptor)
                        val outerCount = getCounts(snapshotKey, streamManager)

                        val innerCount =
                            if (innerKey != null) {
                                getCounts(
                                    innerKey,
                                    streamManager,
                                )
                            } else {
                                0L
                            }

                        Pair(snapshotKey, outerCount + innerCount)
                    }
                val singleKey =
                    streamWithKeyAndCount.map { (key, _) -> key }.toSet().singleOrNull()
                        ?: error(
                            "For global state, all streams should have the same key: $streamWithKeyAndCount"
                        )
                val totalCounts = streamWithKeyAndCount.sumOf { it.second }
                val messageWithCount =
                    checkpoint.withDestinationStats(CheckpointMessage.Stats(totalCounts))
                checkpointQueue.publish(
                    reservation.replace(
                        GlobalSnapshotCheckpointWrapped(singleKey, messageWithCount)
                    )
                )
            }
            is GlobalCheckpoint -> {
                val streamWithKeyAndCount =
                    catalog.streams.map { stream ->
                        val manager = syncManager.getStreamManager(stream.mappedDescriptor)
                        val maybeKey = checkpoint.checkpointKey
                        if (maybeKey != null) {
                            if (checkpoint.sourceStats == null) {
                                error(
                                    "Source stats should always be present when checkpoint key is provided"
                                )
                            }
                        }
                        val key = resolveCheckpointKey(maybeKey, stream.mappedDescriptor)
                        incrementIndex(stream.mappedDescriptor)
                        Pair(key, getCounts(key, manager))
                    }
                val singleKey =
                    streamWithKeyAndCount.map { (key, _) -> key }.toSet().singleOrNull()
                        ?: error(
                            "For global state, all streams should have the same key: $streamWithKeyAndCount"
                        )
                val totalCounts = streamWithKeyAndCount.sumOf { it.second }
                val messageWithCount =
                    checkpoint.withDestinationStats(CheckpointMessage.Stats(totalCounts))
                checkpointQueue.publish(
                    reservation.replace(GlobalCheckpointWrapped(singleKey, messageWithCount))
                )
            }
        }
    }

    private fun resolveCheckpointId(
        checkpointId: CheckpointId?,
        mappedDescriptor: DestinationStream.Descriptor
    ): CheckpointId = checkpointId ?: currentCheckpointKey(mappedDescriptor).checkpointId

    private fun resolveCheckpointKey(
        checkpointKey: CheckpointKey?,
        mappedDescriptor: DestinationStream.Descriptor
    ): CheckpointKey = checkpointKey ?: currentCheckpointKey(mappedDescriptor)

    private fun incrementIndex(mappedDescriptor: DestinationStream.Descriptor) {
        val next = checkpointAtomic(mappedDescriptor).incrementAndGet()
        log.debug { "Setting nextInferredCheckpointIndex for $mappedDescriptor as $next" }
    }

    private fun getCounts(checkpointKey: CheckpointKey, manager: StreamManager): Long =
        manager.readCountForCheckpoint(checkpointId = checkpointKey.checkpointId) ?: 0

    override suspend fun close() {
        log.info { "Maybe closing bookkeeping router ${clientCount.get()}" }
        if (clientCount.decrementAndGet() == 0) {
            if (markEndOfStreamAtEndOfSync) {
                catalog.streams.forEach {
                    val sawComplete = sawEndOfStreamComplete.contains(it.mappedDescriptor)
                    val manager = syncManager.getStreamManager(it.mappedDescriptor)
                    if (sawComplete) {
                        manager.markEndOfStream(true)
                    }
                    batchStateUpdateQueue.publish(
                        BatchEndOfStream(
                            it.mappedDescriptor,
                            "bookkeepingRouter",
                            0,
                            manager.readCount()
                        )
                    )
                }
            }
            log.info { "Closing internal control channels" }
            fileTransferQueue.close()
            checkpointQueue.close()
            openStreamQueue.close()
            syncManager.markInputConsumed()
        }
    }
}
