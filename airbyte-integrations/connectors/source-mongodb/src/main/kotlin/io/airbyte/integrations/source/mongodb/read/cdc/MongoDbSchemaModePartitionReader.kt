/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.cdc

import io.airbyte.cdk.read.GlobalFeedBootstrap
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.integrations.source.mongodb.read.partition.MongoDbPartitionReaderBase
import io.airbyte.integrations.source.mongodb.read.record.MongoDbSharedState

/**
 * The `Global` feed of a catalog without incremental streams: no change stream is read, but a
 * shared state is still written — the schema mode the sync ran under, and any position a previous
 * sync saved. A GLOBAL state without a `shared_state` cannot be given back to the connector.
 */
class MongoDbSchemaModePartitionReader(
    sharedState: MongoDbSharedState,
    private val feedBootstrap: GlobalFeedBootstrap,
) : MongoDbPartitionReaderBase(sharedState, feedBootstrap) {

    override suspend fun run() {}

    override fun checkpoint(): PartitionReadCheckpoint {
        val state: MongoDbCdcState =
            MongoDbCdcState.fromOpaqueStateValue(feedBootstrap.currentState)
                ?: MongoDbCdcState.of(null, sharedState.configuration.schemaEnforced, null)
        return PartitionReadCheckpoint(state.toOpaqueStateValue(), 0, checkpointPartitionId)
    }
}
