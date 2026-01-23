/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.AirbyteStreamFactory
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import jakarta.inject.Singleton

/**
 * MongoDB implementation of [AirbyteStreamFactory].
 *
 * Creates [AirbyteStream] objects for discovered MongoDB collections.
 */
@Singleton
class MongoDbAirbyteStreamFactory : AirbyteStreamFactory {

    override fun create(
        config: SourceConfiguration,
        discoveredStream: DiscoveredStream
    ): AirbyteStream {
        val hasPK = discoveredStream.primaryKeyColumnIDs.isNotEmpty()

        // MongoDB supports full refresh and incremental (using _id as cursor)
        val syncModes = listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)

        return AirbyteStreamFactory.createAirbyteStream(discoveredStream).apply {
            supportedSyncModes = syncModes
            sourceDefinedPrimaryKey = discoveredStream.primaryKeyColumnIDs
            // MongoDB uses _id as source-defined cursor for incremental syncs
            sourceDefinedCursor = true
            defaultCursorField = listOf(MongoDbMetadataQuerier.ID_FIELD)
            isResumable = hasPK
        }
    }
}
