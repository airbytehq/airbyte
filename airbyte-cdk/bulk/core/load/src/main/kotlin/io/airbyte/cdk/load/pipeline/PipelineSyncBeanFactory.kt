/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.write.LoadStrategy
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlinx.coroutines.channels.Channel

/** Temporary. I'll merge this into the main SyncBeanFactory once I'm done with the refactor. */
@Factory
class PipelineSyncBeanFactory(
    private val destinationConfiguration: DestinationConfiguration,
    private val loadStrategy: LoadStrategy? = null,
) {

    /**
     * A single record queue for the whole sync, containing all streams, optionally partitioned by a
     * configurable number of partitions.
     */
    @Singleton
    @Named("recordQueue")
    fun recordQueue(): PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordAirbyteValue>> {
        return PartitionedQueue(
            Array(loadStrategy?.inputPartitions ?: 1) {
                ChannelMessageQueue(
                    Channel(
                        destinationConfiguration.maxRecordQueueDepth
                    )
                )
            }
        )
    }

    /** A queue for updating batch states, which is not partitioned. */
    @Singleton
    @Named("batchStateUpdateQueue")
    fun batchStateUpdateQueue(): ChannelMessageQueue<BatchUpdate> {
        return ChannelMessageQueue(Channel(100))
    }
}
