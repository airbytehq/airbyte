/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.SinglePartitionQueueWithMultiPartitionBroadcast
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.state.ReservationManager
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

    /**
     * Queue between step 1 (format parts) and step 2 (load them): it will hold the actual part
     * bytes and needs to be sized based on the available reserved memory.
     */
    @Singleton
    @Named("objectLoaderPartQueue")
    @Requires(bean = ObjectLoader::class)
    fun objectLoaderPartQueue():
        SinglePartitionQueueWithMultiPartitionBroadcast<
            PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>> {
        val bytes = memoryManager.totalCapacityBytes * loader.maxMemoryRatioReservedForParts
        val reservation = runBlocking { memoryManager.reserve(bytes.toLong(), this) }
        val maxNumParts = reservation.bytesReserved / loader.partSizeBytes
        val numWorkersHoldingParts = loader.numPartWorkers + loader.numUploadWorkers
        val maxNumPartsEnqueued = maxNumParts - numWorkersHoldingParts

        require(maxNumPartsEnqueued > 0) {
            "${reservation.bytesReserved}b is not enough for ${loader.numPartWorkers} part workers and ${loader.numUploadWorkers} upload workers each to hold ${loader.partSizeBytes}b parts in memory (max=$maxNumParts- $numWorkersHoldingParts = $maxNumPartsEnqueued < 1)"
        }

        log.info {
            "Reserved $bytes/${memoryManager.totalCapacityBytes}b for $maxNumParts ${loader.partSizeBytes}b parts $numWorkersHoldingParts for workers and $maxNumPartsEnqueued enqueued"
        }

        return SinglePartitionQueueWithMultiPartitionBroadcast(
            ChannelMessageQueue(Channel(maxNumPartsEnqueued.toInt())),
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
            PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult>> {
        return SinglePartitionQueueWithMultiPartitionBroadcast(
            ChannelMessageQueue(Channel(OBJECT_LOADER_MAX_ENQUEUED_COMPLETIONS)),
            1
        )
    }
}
