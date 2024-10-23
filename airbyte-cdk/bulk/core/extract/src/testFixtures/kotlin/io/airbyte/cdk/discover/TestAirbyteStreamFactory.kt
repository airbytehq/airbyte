/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.discover

import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.micronaut.context.annotation.Requires
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton

@Singleton
@Requires(env = [Environment.TEST])
@Requires(notEnv = [Environment.CLI])
class TestAirbyteStreamFactory(
    val metaFieldDecorator: TestMetaFieldDecorator,
) : AirbyteStreamFactory {

    override fun createGlobal(discoveredStream: DiscoveredStream): AirbyteStream =
        AirbyteStreamFactory.createAirbyteStream(discoveredStream).apply {
            supportedSyncModes = listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
            metaFieldDecorator.decorateAirbyteStream(this)
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
