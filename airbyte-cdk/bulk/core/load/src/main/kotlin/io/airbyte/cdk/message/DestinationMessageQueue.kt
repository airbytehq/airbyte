/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.message

import io.airbyte.cdk.command.DestinationCatalog
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.command.WriteConfiguration
import io.airbyte.cdk.state.MemoryManager
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.locks.ReentrantLock
import kotlin.concurrent.withLock
import kotlinx.coroutines.runBlocking

/**
 * Wrapper for record messages published to the message queue, containing metadata like index and
 * size.
 *
 * In a future where we deserialize only the info necessary for routing, this could include a dumb
 * container for the serialized, and deserialization could be deferred until the spooled records
 * were recovered from disk.
 */
sealed class DestinationRecordWrapped : Sized

data class StreamRecordWrapped(
    val index: Long,
    override val sizeBytes: Long,
    val record: DestinationRecord
) : DestinationRecordWrapped()

data class StreamCompleteWrapped(
    val index: Long,
) : DestinationRecordWrapped() {
    override val sizeBytes: Long = 0L
}

/**
 * Message queue to which @[DestinationRecordWrapped] messages can be published on a @
 * [DestinationStream] key.
 *
 * It maintains a map of @[QueueChannel]s by stream, and tracks the memory usage across all
 * channels, blocking when the maximum is reached.
 *
 * This maximum is expected to be low, as the assumption is that data will be spooled to disk as
 * quickly as possible.
 */
@Singleton
class DestinationMessageQueue(
    catalog: DestinationCatalog,
    config: WriteConfiguration,
    private val memoryManager: MemoryManager,
    private val queueChannelFactory: QueueChannelFactory<DestinationRecordWrapped>
) : MessageQueue<DestinationStream, DestinationRecordWrapped> {
    private val channels:
        ConcurrentHashMap<DestinationStream.Descriptor, QueueChannel<DestinationRecordWrapped>> =
        ConcurrentHashMap()

    private val totalQueueSizeBytes = AtomicLong(0L)
    private val maxQueueSizeBytes: Long
    private val memoryLock = ReentrantLock()
    private val memoryLockCondition = memoryLock.newCondition()

    init {
        catalog.streams.forEach { channels[it.descriptor] = queueChannelFactory.make(this) }
        val adjustedRatio =
            config.maxMessageQueueMemoryUsageRatio /
                (1.0 + config.estimatedRecordMemoryOverheadRatio)
        maxQueueSizeBytes = runBlocking { memoryManager.reserveRatio(adjustedRatio) }
    }

    override suspend fun acquireQueueBytesBlocking(bytes: Long) {
        memoryLock.withLock {
            while (totalQueueSizeBytes.get() + bytes > maxQueueSizeBytes) {
                memoryLockCondition.await()
            }
            totalQueueSizeBytes.addAndGet(bytes)
        }
    }

    override suspend fun releaseQueueBytes(bytes: Long) {
        memoryLock.withLock {
            totalQueueSizeBytes.addAndGet(-bytes)
            memoryLockCondition.signalAll()
        }
    }

    override suspend fun getChannel(
        key: DestinationStream,
    ): QueueChannel<DestinationRecordWrapped> {
        return channels[key.descriptor]
            ?: throw IllegalArgumentException(
                "Reading from non-existent QueueChannel: ${key.descriptor}"
            )
    }

    private val log = KotlinLogging.logger {}
}
