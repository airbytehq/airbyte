/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.config

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.pipeline.BatchUpdate
import io.airbyte.cdk.load.state.CheckpointManager
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.SyncManager
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

    @Singleton
    fun checkpointManager(
        catalog: DestinationCatalog,
        syncManager: SyncManager,
        outputConsumer: suspend (Reserved<CheckpointMessage>, Long, Long) -> Unit,
        timeProvider: TimeProvider,
    ): CheckpointManager<Reserved<CheckpointMessage>> =
        CheckpointManager(
            catalog,
            syncManager,
            outputConsumer,
            timeProvider,
        )

    /* ********************
     * ASYNCHRONOUS QUEUES
     * ********************/

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
