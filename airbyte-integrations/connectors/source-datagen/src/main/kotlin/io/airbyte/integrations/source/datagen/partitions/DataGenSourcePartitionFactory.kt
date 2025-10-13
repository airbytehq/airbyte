/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.partitions

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

private val log = KotlinLogging.logger {}

@Singleton
class DataGenSourcePartitionFactory(val sharedState: DataGenSharedState) {
    private val streamStates = ConcurrentHashMap<StreamIdentifier, DataGenStreamState>()

    fun streamState(streamFeedBootstrap: StreamFeedBootstrap): DataGenStreamState =
        streamStates.getOrPut(streamFeedBootstrap.feed.id) {
            DataGenStreamState(sharedState, streamFeedBootstrap)
        }

    fun create(streamFeedBootstrap: StreamFeedBootstrap): DataGenSourcePartition? {
        log.info { "Starting partition creation for stream: ${streamFeedBootstrap.feed.id}" }

        if (streamFeedBootstrap.currentState == DataGenStreamState.completeState) {
            return null
        }

        return DataGenSourcePartition(streamState(streamFeedBootstrap), 1, 0)
    }

    fun split(unsplitPartition: DataGenSourcePartition): List<DataGenSourcePartition> {
        val modulo = sharedState.configuration.maxConcurrency
        return List(modulo) { i -> DataGenSourcePartition(unsplitPartition.streamState, modulo, i) }
    }
}
