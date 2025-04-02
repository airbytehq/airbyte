/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

/**
 * Internal representation of destination streams. This is intended to be a case class specialized
 * for usability.
 */
data class DestinationCatalog(val streams: List<DestinationStream> = emptyList()) {
    private val log = KotlinLogging.logger {}

    private val byDescriptor: Map<DestinationStream.Descriptor, DestinationStream> =
        streams.associateBy { it.descriptor }

    init {
        if (streams.isEmpty()) {
            throw IllegalArgumentException(
                "Catalog must have at least one stream: check that files are in the correct location."
            )
        }
        log.info { "Destination catalog initialized: $streams" }
    }

    fun getStream(name: String, namespace: String?): DestinationStream {
        val descriptor = DestinationStream.Descriptor(namespace = namespace, name = name)
        return byDescriptor[descriptor]
            ?: throw IllegalArgumentException("Stream not found: namespace=$namespace, name=$name")
    }

    fun getStream(descriptor: DestinationStream.Descriptor): DestinationStream {
        return byDescriptor[descriptor]
            ?: throw IllegalArgumentException("Stream not found: $descriptor")
    }

    fun asProtocolObject(): ConfiguredAirbyteCatalog =
        ConfiguredAirbyteCatalog().withStreams(streams.map { it.asProtocolObject() })

    fun size(): Int = streams.size
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
    @Secondary
    fun make(): DestinationCatalog {
        return DestinationCatalog(streams = catalog.streams.map { streamFactory.make(it) })
    }
}
