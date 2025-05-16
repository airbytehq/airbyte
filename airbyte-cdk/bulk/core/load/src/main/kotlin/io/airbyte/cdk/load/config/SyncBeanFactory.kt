/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.config

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.FileTransferQueueMessage
import io.airbyte.cdk.load.message.MultiProducerChannel
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.StrictPartitionedQueue
import io.airbyte.cdk.load.pipeline.BatchUpdate
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.write.LoadStrategy
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.runBlocking

const val CHECK_STREAM_NAMESPACE = "airbyte_internal_test"

/** Factory for instantiating beans necessary for the sync process. */
@Factory
class SyncBeanFactory {
    /* ******************
     * RESOURCE MANAGERS
     * ******************/

    @Singleton
    @Secondary
    @Named("globalMemoryManager")
    fun globalMemoryManager(): ReservationManager {
        return ReservationManager(Runtime.getRuntime().maxMemory())
    }

    @Singleton
    @Named("queueMemoryManager")
    fun queueMemoryMananger(
        config: DestinationConfiguration,
        @Named("globalMemoryManager") globalMemoryManager: ReservationManager
    ): ReservationManager {
        val recordQueueBytes =
            config.maxMessageQueueMemoryUsageRatio * globalMemoryManager.totalCapacityBytes
        val reservation = runBlocking {
            globalMemoryManager.reserve(recordQueueBytes.toLong(), null)
        }
        return ReservationManager(reservation.bytesReserved)
    }

    /* ********************
     * ASYNCHRONOUS QUEUES
     * ********************/

    // DEPRECATED: Legacy file transfer.
    @Singleton
    @Named("fileMessageQueueLegacy")
    fun fileMessageQueueLegacy(
        config: DestinationConfiguration,
    ): MultiProducerChannel<FileTransferQueueMessage> {
        val channel = Channel<FileTransferQueueMessage>(config.batchQueueDepth)
        return MultiProducerChannel(1, channel, "fileMessageQueueLegacy")
    }

    /** A separate queue for records with file references for file uploading. */
    @Singleton
    @Named("recordsWithFilesQueue")
    fun fileQueue(
        loadStrategy: LoadStrategy? = null,
    ): PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>> {
        return StrictPartitionedQueue(
            Array(loadStrategy?.inputPartitions ?: 1) {
                ChannelMessageQueue(Channel(Channel.UNLIMITED))
            }
        )
    }

    /**
     * A queue of streams to open on. This allows the dev to control the number of concurrent calls
     * to open by controlling how many workers (coroutines) are pulling from this queue.
     */
    @Singleton
    @Named("openStreamQueue")
    class OpenStreamQueue : ChannelMessageQueue<DestinationStream>(Channel(Channel.UNLIMITED))

    /** A queue for updating batch states, which is not partitioned. */
    @Singleton
    @Named("batchStateUpdateQueue")
    fun batchStateUpdateQueue(): ChannelMessageQueue<BatchUpdate> {
        return ChannelMessageQueue(Channel(100))
    }

    /* *************
     * GLOBAL FLAGS
     * *************/

    /** True if the catalog has at least one stream that includeFiles. */
    @Singleton
    @Named("isFileTransfer")
    fun isFileTransfer(catalog: DestinationCatalog): Boolean =
        catalog.streams.any { it.includeFiles }

    /* *************
     * GLOBAL STATE
     * *************/

    @Singleton
    @Named("defaultDestinationTaskLauncherHasThrown")
    fun defaultDestinationTaskLauncherHasThrown(): AtomicBoolean = AtomicBoolean(false)
}
