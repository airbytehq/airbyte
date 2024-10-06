/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.discover

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.micronaut.context.annotation.Requires
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton

@Singleton
@Requires(env = [Environment.TEST])
@Requires(notEnv = [Environment.CLI])
class TestAirbyteStreamFactory : AirbyteStreamFactory {

    override fun createGlobal(discoveredStream: DiscoveredStream): AirbyteStream =
        AirbyteStreamFactory.createAirbyteStream(discoveredStream).apply {
            supportedSyncModes = listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
            (jsonSchema["properties"] as ObjectNode).apply {
                for (metaField in CommonMetaField.entries) {
                    set<ObjectNode>(metaField.id, metaField.type.airbyteType.asJsonSchema())
                }
            }
            defaultCursorField = listOf(CommonMetaField.CDC_LSN.id)
            sourceDefinedCursor = true
            if (discoveredStream.primaryKeyColumnIDs.isNotEmpty()) {
                sourceDefinedPrimaryKey = discoveredStream.primaryKeyColumnIDs
                isResumable = true
            } else {
                isResumable = false
            }
        }

    override fun createNonGlobal(discoveredStream: DiscoveredStream): AirbyteStream =
        AirbyteStreamFactory.createAirbyteStream(discoveredStream).apply {
            supportedSyncModes = listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
            sourceDefinedCursor = false
            if (discoveredStream.primaryKeyColumnIDs.isNotEmpty()) {
                sourceDefinedPrimaryKey = discoveredStream.primaryKeyColumnIDs
                isResumable = true
            } else {
                isResumable = false
            }
        }
}
