/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.db

import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.QueueCapacityCalculator
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.StrictPartitionedQueue
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.write.db.InsertLoader
import io.airbyte.cdk.load.write.db.InsertLoaderRequest
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.runBlocking

@Factory
@Requires(bean = InsertLoader::class)
class InsertLoaderRequestQueueFactory<Q : InsertLoaderRequest>(
    private val loader: InsertLoader<Q>,
) {
    private val log = KotlinLogging.logger {}

    /**
     * See comments in ObjectLoaderPartQueueFactory, which uses the same memory strategy. TODO:
     * Generalize this to a type of queue.
     */
    @Singleton
    @Secondary
    @Named("insertLoaderMemoryReservation")
    @Requires(bean = InsertLoader::class)
    fun insertLoaderMemoryReservation(
        @Named("globalMemoryManager") globalMemoryManager: ReservationManager
    ): Reserved<InsertLoader<Q>> {
        val totalRequestBytes =
            (loader.maxMemoryRatioToUseForRequests * globalMemoryManager.totalCapacityBytes)
                .toLong()
        log.info {
            "Reserved ${totalRequestBytes}b for ${loader::class.java.simpleName} for part processing"
        }
        return runBlocking { globalMemoryManager.reserve(totalRequestBytes, loader) }
    }

    @Singleton
    @Named("insertLoaderClampedRequestSizeBytes")
    @Requires(bean = InsertLoader::class)
    fun insertLoaderClampedPartSizeBytes(
        @Named("insertLoaderMemoryReservation") reservation: Reserved<InsertLoader<Q>>
    ): Long {
        val calculator =
            QueueCapacityCalculator(
                numProducers = loader.numRequestBuilders,
                numConsumers = loader.numRequestExecutors,
                availableResourceAmount = reservation.bytesReserved,
                expectedUsagePerMessageAmount = loader.estimatedByteSizePerRequest
            )
        val maybeClampedByteSize = calculator.clampedMessageSize

        if (loader.estimatedByteSizePerRequest > maybeClampedByteSize) {
            log.warn {
                "Clamping part size from ${loader.estimatedByteSizePerRequest}b to ${maybeClampedByteSize}b to fit ${calculator.numUnits} requests in ${reservation.bytesReserved}b reserved memory"
            }
            return maybeClampedByteSize
        }

        return loader.estimatedByteSizePerRequest
    }

    @Singleton
    @Named("insertLoaderRequestQueue")
    @Requires(bean = InsertLoader::class)
    fun insertLoaderRequestQueue(
        @Named("insertLoaderClampedRequestSizeBytes") clampedRequestSizeBytes: Long,
        @Named("insertLoaderMemoryReservation") reservation: Reserved<InsertLoader<Q>>
    ): PartitionedQueue<PipelineEvent<StreamKey, InsertLoaderRequestBuilder.Result<Q>>> {
        val calculator =
            QueueCapacityCalculator(
                numProducers = loader.numRequestBuilders,
                numConsumers = loader.numRequestExecutors,
                availableResourceAmount = reservation.bytesReserved,
                expectedUsagePerMessageAmount = clampedRequestSizeBytes
            )
        val capacity = calculator.queuePartitionCapacity

        return StrictPartitionedQueue(
            (0 until loader.numRequestExecutors)
                .map {
                    ChannelMessageQueue<
                        PipelineEvent<StreamKey, InsertLoaderRequestBuilder.Result<Q>>>(
                        Channel(capacity)
                    )
                }
                .toTypedArray()
        )
    }
}
