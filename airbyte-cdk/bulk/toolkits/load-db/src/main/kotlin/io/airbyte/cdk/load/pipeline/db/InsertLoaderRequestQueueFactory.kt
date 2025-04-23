/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.db

import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.ResourceReservingPartitionedQueue
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.write.db.InsertLoader
import io.airbyte.cdk.load.write.db.InsertLoaderRequest
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

@Factory
@Requires(bean = InsertLoader::class)
class InsertLoaderRequestQueueFactory<Q : InsertLoaderRequest>() {
    @Singleton
    @Named("insertLoaderClampedRequestSizeBytes")
    @Requires(bean = InsertLoader::class)
    fun insertLoaderClampedPartSizeBytes(
        @Named("insertLoaderRequestQueue") queue: ResourceReservingPartitionedQueue<*>
    ) = queue.clampedMessageSize

    @Singleton
    @Named("insertLoaderRequestQueue")
    @Requires(bean = InsertLoader::class)
    fun <Q : InsertLoaderRequest> insertLoaderRequestQueue(
        insertLoader: InsertLoader<Q>,
        @Named("globalMemoryManager") reservationManager: ReservationManager,
    ): ResourceReservingPartitionedQueue<
        PipelineEvent<StreamKey, InsertLoaderRequestBuilderAccumulator.Result<Q>>> {
        return ResourceReservingPartitionedQueue(
            reservationManager = reservationManager,
            ratioOfTotalMemoryToReserve = insertLoader.maxMemoryRatioToUseForRequests,
            numConsumers = insertLoader.numRequestExecutors,
            numProducers = insertLoader.numRequestBuilders,
            expectedResourceUsagePerUnit = insertLoader.estimatedByteSizePerRequest
        )
    }
}
