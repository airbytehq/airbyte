/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineMessage
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

    @Singleton
    @Named("objectLoaderPartQueue")
    @Requires(bean = ObjectLoader::class)
    fun objectLoaderPartQueue(): PartitionedQueue<PipelineMessage<ObjectKey, Part>> {
        val bytes = memoryManager.totalCapacityBytes * loader.maxMemoryRatioReservedForParts
        val reservation = runBlocking { memoryManager.reserve(bytes.toLong(), this) }
        val bytesPerPartition = reservation.bytesReserved // / loader.numUploadWorkers
        val partsPerPartition = bytesPerPartition / loader.partSizeBytes

//        if (partsPerPartition < 1) {
//            throw IllegalArgumentException(
//                "Reserved $bytes/${memoryManager.totalCapacityBytes}b not enough for ${loader.numUploadWorkers} ${loader.partSizeBytes}b parts"
//            )
//        }
//
//        log.info {
//            "Reserved $bytes/${memoryManager.totalCapacityBytes}b for ${loader.numUploadWorkers} ${loader.partSizeBytes}b parts => $partsPerPartition capacity per queue partition"
//        }

        return PartitionedQueue(
//            (0 until loader.numUploadWorkers)
//                .map {
                    arrayOf(ChannelMessageQueue(
                        Channel<PipelineMessage<ObjectKey, Part>>(partsPerPartition.toInt())
                    ))
//                }
//                .toTypedArray()
        )
    }
}
