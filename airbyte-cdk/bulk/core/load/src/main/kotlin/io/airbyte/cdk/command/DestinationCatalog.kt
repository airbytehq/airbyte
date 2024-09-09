/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.command

import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

/**
 * Internal representation of destination streams. This is intended to be a case class specialized
 * for usability.
 */
data class DestinationCatalog(
    val streams: List<DestinationStream> = emptyList(),
) {
    private val byDescriptor: Map<DestinationStream.Descriptor, DestinationStream> =
        streams.associateBy { it.descriptor }

    fun getStream(name: String, namespace: String): DestinationStream {
        val descriptor = DestinationStream.Descriptor(namespace = namespace, name = name)
        return byDescriptor[descriptor]
            ?: throw IllegalArgumentException("Stream not found: namespace=$namespace, name=$name")
    }
}

interface DestinationCatalogFactory {
    fun make(): DestinationCatalog
}

@Factory
class DefaultDestinationCatalogFactory(
    private val catalog: ConfiguredAirbyteCatalog,
    private val streamFactory: DestinationStreamFactory
) {
    @Singleton
    fun make(): DestinationCatalog {
        return DestinationCatalog(streams = catalog.streams.map { streamFactory.make(it) })
    }
}
