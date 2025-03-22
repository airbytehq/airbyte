/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.SinglePartitionQueueWithMultiPartitionBroadcast
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.runBlocking

data class ObjectKey(override val stream: DestinationStream.Descriptor, val objectKey: String) :
    WithStream

@Factory
class ObjectLoaderPartQueueFactory(
    val loader: ObjectLoader,
    @Named("memoryManager") val memoryManager: ReservationManager,
) {
    val log = KotlinLogging.logger {}

    companion object {
        const val OBJECT_LOADER_MAX_ENQUEUED_COMPLETIONS = 10_000
    }

    @Singleton
    @Named("objectLoaderMemoryReservation")
    @Requires(bean = ObjectLoader::class)
    fun objectLoaderMemoryReservation(): Reserved<*> {
        val bytes = memoryManager.totalCapacityBytes * loader.maxMemoryRatioReservedForParts
        return runBlocking { memoryManager.reserve(bytes.toLong(), this) }
    }

    @Singleton
    @Named("objectLoaderClampedPartSizeBytes")
    @Requires(bean = ObjectLoader::class)
    fun objectLoaderClampedPartSizeBytes(
        @Named("objectLoaderMemoryReservation") reservation: Reserved<*>
    ): Long {
        val maxNumPartsInMemory = loader.numPartWorkers + loader.numUploadWorkers + 1
        val maxPartSizeBytes = reservation.bytesReserved / maxNumPartsInMemory

        if (loader.partSizeBytes > maxPartSizeBytes) {
            log.warn {
                "Clamping part size from ${loader.partSizeBytes}b to ${maxPartSizeBytes}b to fit $maxNumPartsInMemory parts in ${reservation.bytesReserved}b reserved memory"
            }
            return maxPartSizeBytes
        }

        return loader.partSizeBytes
    }

    /**
     * Queue between step 1 (format parts) and step 2 (load them): it will hold the actual part
     * bytes and needs to be sized based on the available reserved memory.
     */
    @Singleton
    @Named("objectLoaderPartQueue")
    @Requires(bean = ObjectLoader::class)
    fun objectLoaderPartQueue(
        @Named("objectLoaderClampedPartSizeBytes") clampedPartSizeBytes: Long,
        @Named("objectLoaderMemoryReservation") reservation: Reserved<*>
    ): SinglePartitionQueueWithMultiPartitionBroadcast<
        PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>> {
        val maxNumParts = reservation.bytesReserved / clampedPartSizeBytes
        val numWorkersHoldingParts = loader.numPartWorkers + loader.numUploadWorkers
        val maxQueueCapacity = maxNumParts - numWorkersHoldingParts
        // Our earlier calculations should ensure this is always at least 1, but
        // we'll clamp it to be safe.
        val capacity = maxQueueCapacity.coerceAtLeast(1).toInt()

        log.info {
            "Creating part queue with capacity for $capacity $maxNumParts parts of size $clampedPartSizeBytes (plus $numWorkersHoldingParts held by workers)"
        }

        return SinglePartitionQueueWithMultiPartitionBroadcast(
            ChannelMessageQueue(Channel(capacity)),
            loader.numUploadWorkers
        )
    }

    /**
     * Queue between part 2 (upload parts) and part 3 (finish the upload). It will hold the fact of
     * upload completion only, so in theory it can be [Channel.UNLIMITED], but to be safe we'll
     * limit it to 10,000 queued completions.
     */
    @Singleton
    @Named("objectLoaderLoadedPartQueue")
    @Requires(bean = ObjectLoader::class)
    fun objectLoaderLoadedPartQueue():
        SinglePartitionQueueWithMultiPartitionBroadcast<
            PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult<RemoteObject<*>>>> {
        return SinglePartitionQueueWithMultiPartitionBroadcast(
            ChannelMessageQueue(Channel(OBJECT_LOADER_MAX_ENQUEUED_COMPLETIONS)),
            1
        )
    }
}
