/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.WithStream
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton

/** Temporary. I'll merge this into the main SyncBeanFactory once I'm done with the refactor. */
@Factory
class PipelineSyncBeanFactory<K : WithStream>(
    @Value("\${airbyte.destination.core.load-pipeline.input-parts}")
    private val numWorkers: Int? = null
) {

    /**
     * A single record queue for the whole sync, containing all streams, optionally partitioned by a
     * configurable number of partitions.
     */
    @Singleton
    @Named("recordQueue")
    fun recordQueue(): PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordAirbyteValue>> {
        return PartitionedQueue(numWorkers ?: 1, capacity = 1000)
    }

    /** A queue for updating batch states, which is not partitioned. */
    @Singleton
    @Named("batchStateUpdateQueue")
    fun batchStateUpdateQueue(): ChannelMessageQueue<BatchUpdate> {
        return object : ChannelMessageQueue<BatchUpdate>() {}
    }
}
