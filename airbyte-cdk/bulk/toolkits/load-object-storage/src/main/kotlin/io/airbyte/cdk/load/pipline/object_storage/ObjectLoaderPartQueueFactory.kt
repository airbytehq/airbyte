/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.StrictPartitionedQueue
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.runBlocking

data class ObjectKey(override val stream: DestinationStream.Descriptor, val objectKey: String) :
    WithStream

@Factory
class ObjectLoaderPartQueueFactory(
    val loader: ObjectLoader,
) {
    val log = KotlinLogging.logger {}

    companion object {
        const val OBJECT_LOADER_MAX_ENQUEUED_COMPLETIONS = 10_000
    }

    @Singleton
    @Secondary
    @Named("objectLoaderMemoryReservation")
    @Requires(bean = ObjectLoader::class)
    fun objectLoaderMemoryReservation(
        @Named("globalMemoryManager") globalMemoryManager: ReservationManager
    ): Reserved<ObjectLoader> {
        val totalPartBytes =
            (loader.maxMemoryRatioReservedForParts * globalMemoryManager.totalCapacityBytes)
                .toLong()
        log.info {
            "Reserved ${totalPartBytes}b for ${loader::class.java.simpleName} for part processing"
        }
        return runBlocking { globalMemoryManager.reserve(totalPartBytes, loader) }
    }

    /**
     * If we naively accept the part size and concurrency settings, we might end up with a connector
     * that passes CI but can't run in a resource-limited production environment, because there
     * isn't enough memory even for the workers to hold parts in flight.
     *
     * Therefore we will always clamp the part size to fit the available memory. This might still
     * lead to runtime failures (ie, if it drops below a storage-client-specified minimum), but it
     * is much less likely.
     */
    @Singleton
    @Named("objectLoaderClampedPartSizeBytes")
    @Requires(bean = ObjectLoader::class)
    fun objectLoaderClampedPartSizeBytes(
        @Named("objectLoaderMemoryReservation") reservation: Reserved<ObjectLoader>
    ): Long {
        // 1 per worker, plus at least one per partition leading to the upload workers.
        val maxNumPartsInMemory = loader.numPartWorkers + (loader.numUploadWorkers * 2)
        val maxPartSizeBytes = reservation.bytesReserved / maxNumPartsInMemory

        if (loader.partSizeBytes > maxPartSizeBytes) {
            log.warn {
                "Clamping part size from ${loader.partSizeBytes}b to ${maxPartSizeBytes}b to fit $maxNumPartsInMemory parts in ${reservation.bytesReserved}b reserved memory"
            }
            return maxPartSizeBytes
        }

        return loader.partSizeBytes
    }

    @Singleton
    @Named("objectLoaderPartQueueCapacity")
    @Requires(bean = ObjectLoader::class)
    fun objectLoaderPartQueueCapacity(
        @Named("objectLoaderClampedPartSizeBytes") clampedPartSizeBytes: Long,
        @Named("objectLoaderMemoryReservation") reservation: Reserved<ObjectLoader>
    ): Int {
        val maxNumParts = reservation.bytesReserved / clampedPartSizeBytes
        val numWorkersHoldingParts = loader.numPartWorkers + loader.numUploadWorkers
        val maxQueueCapacity = (maxNumParts - numWorkersHoldingParts) / loader.numUploadWorkers
        // Our earlier calculations should ensure this is always at least 1, but
        // we'll clamp it to be safe.
        val capacity = maxQueueCapacity.toInt().coerceAtLeast(1)
        log.info {
            "Creating part queue with capacity $capacity for $maxNumParts parts of size $clampedPartSizeBytes (minus $numWorkersHoldingParts held by workers)"
        }

        return capacity
    }

    /**
     * Queue between step 1 (format parts) and step 2 (load them): it will hold the actual part
     * bytes and needs to be sized based on the available reserved memory.
     */
    @Singleton
    @Named("objectLoaderPartQueue")
    @Requires(bean = ObjectLoader::class)
    fun objectLoaderPartQueue(
        @Named("objectLoaderPartQueueCapacity") capacity: Int
    ): PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>> {
        return StrictPartitionedQueue(
            (0 until loader.numUploadWorkers)
                .map {
                    ChannelMessageQueue(
                        Channel<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>(
                            capacity
                        )
                    )
                }
                .toTypedArray()
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
    fun <T : RemoteObject<*>> objectLoaderLoadedPartQueue():
        PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult<T>>> {
        return StrictPartitionedQueue(
            (0 until loader.numUploadCompleters)
                .map {
                    ChannelMessageQueue(
                        Channel<PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult<T>>>(
                            OBJECT_LOADER_MAX_ENQUEUED_COMPLETIONS / loader.numUploadWorkers
                        )
                    )
                }
                .toTypedArray()
        )
    }
}
