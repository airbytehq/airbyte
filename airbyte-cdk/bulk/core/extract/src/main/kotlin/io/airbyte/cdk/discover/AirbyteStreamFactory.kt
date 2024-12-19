/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.discover

import io.airbyte.protocol.models.Field as AirbyteField
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.github.oshai.kotlinlogging.KotlinLogging

private val log = KotlinLogging.logger {}
/** Stateless object for building an [AirbyteStream] during DISCOVER. */
interface AirbyteStreamFactory {
    /** Connector-specific [AirbyteStream] creation logic for GLOBAL-state streams. */
    fun createGlobal(discoveredStream: DiscoveredStream): AirbyteStream

    /** Connector-specific [AirbyteStream] creation logic for STREAM-state streams. */
    fun createNonGlobal(discoveredStream: DiscoveredStream): AirbyteStream

    companion object {

        fun createAirbyteStream(discoveredStream: DiscoveredStream): AirbyteStream =
            CatalogHelpers.createAirbyteStream(
                discoveredStream.id.name,
                discoveredStream.id.namespace,
                discoveredStream.columns.map {
                    val retVal =  AirbyteField.of(it.id, it.type.airbyteSchemaType.asJsonSchemaType())
                    log.info{"field of type $retVal from ${it.type.airbyteSchemaType} for stream $discoveredStream"}
                    retVal
                },
            )
    }
}
