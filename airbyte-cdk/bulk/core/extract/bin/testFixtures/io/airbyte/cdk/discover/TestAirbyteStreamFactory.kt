/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.discover

import io.airbyte.cdk.command.SourceConfiguration
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

    override fun create(
        config: SourceConfiguration,
        discoveredStream: DiscoveredStream
    ): AirbyteStream =
        AirbyteStreamFactory.createAirbyteStream(discoveredStream).apply {
            val hasPK = discoveredStream.primaryKeyColumnIDs.isNotEmpty()
            supportedSyncModes = listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
            if (config.isCdc()) {
                metaFieldDecorator.decorateAirbyteStream(this)
            }
            sourceDefinedPrimaryKey =
                if (hasPK) discoveredStream.primaryKeyColumnIDs else emptyList()
            sourceDefinedCursor = config.isCdc() && hasPK
            isResumable = hasPK
        }
}
