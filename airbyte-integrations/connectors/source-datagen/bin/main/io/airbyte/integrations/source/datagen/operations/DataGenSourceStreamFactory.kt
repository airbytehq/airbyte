/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.operations

import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.AirbyteStreamFactory
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

@Singleton
@Primary
open class DataGenSourceStreamFactory : AirbyteStreamFactory {
    override fun create(
        config: SourceConfiguration,
        discoveredStream: DiscoveredStream
    ): AirbyteStream =
        AirbyteStreamFactory.createAirbyteStream(discoveredStream).apply {
            supportedSyncModes = listOf(SyncMode.FULL_REFRESH)
            isResumable = false
        }
}
