package io.airbyte.integrations.source.datagen.partitionops

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.integrations.source.datagen.partitionobjs.DataGenSharedState
import io.airbyte.integrations.source.datagen.partitionobjs.DataGenSourcePartition
import io.airbyte.integrations.source.datagen.partitionobjs.DataGenStreamState
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.ConcurrentHashMap
import jakarta.inject.Singleton

private val log = KotlinLogging.logger {}

@Singleton
class DataGenSourcePartitionFactory(val sharedState: DataGenSharedState) {
    private val streamStates = ConcurrentHashMap<StreamIdentifier, DataGenStreamState>()

    fun streamState(streamFeedBootstrap: StreamFeedBootstrap): DataGenStreamState =
        streamStates.getOrPut(streamFeedBootstrap.feed.id) {
            DataGenStreamState(sharedState, streamFeedBootstrap)
        }

    fun create(streamFeedBootstrap: StreamFeedBootstrap): DataGenSourcePartition? {
        log.info { "Starting partition creation for stream: ${streamFeedBootstrap.feed.id}"}
        val stream: Stream = streamFeedBootstrap.feed
        val streamState: DataGenStreamState = streamState(streamFeedBootstrap)

        if (streamFeedBootstrap.currentState == DataGenStreamState.completeState) {
            return null
        }

        // An empty table stream state will be marked as a nullNode. This prevents repeated attempt
//        // to read it
//        if (streamFeedBootstrap.currentState?.isNull == true) {
//            return null
//        }

        return DataGenSourcePartition(streamState)
    }
    fun split(unsplitPartition: DataGenSourcePartition, opaqueStateValues: List<OpaqueStateValue>
    ): List<DataGenSourcePartition> {
        return listOf(unsplitPartition)
    }

}
