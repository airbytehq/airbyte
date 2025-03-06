/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.discover

import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.protocol.models.Field as AirbyteField
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.CatalogHelpers

/** Stateless object for building an [AirbyteStream] during DISCOVER. */
interface AirbyteStreamFactory {
    /** Connector-specific [AirbyteStream] creation logic. */
    fun create(config: SourceConfiguration, discoveredStream: DiscoveredStream): AirbyteStream

    companion object {

        fun createAirbyteStream(discoveredStream: DiscoveredStream): AirbyteStream =
            CatalogHelpers.createAirbyteStream(
                discoveredStream.id.name,
                discoveredStream.id.namespace,
                discoveredStream.columns.map {
                    AirbyteField.of(it.id, it.type.airbyteSchemaType.asJsonSchemaType())
                },
            )
    }
}
