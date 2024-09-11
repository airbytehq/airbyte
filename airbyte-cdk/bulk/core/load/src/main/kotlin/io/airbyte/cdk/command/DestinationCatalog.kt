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

// I'd caution against using Micronaut for this.
// and instead consider inlining the generation of the DestinationCatalog in the WriteOperation
// and then plumb it and its friends in some immutable DestinationContext data class.
//
// The main reason for this is that DI quickly becomes tentacular and hard to reason about.
// In other words, there's a very real complexity cost to every new injectable bean that you add.
// It adds up very quickly and is super hard to simplify later on.
//
// Furthermore, you open yourself up to exceptions being thrown at startup time when the
// factory does its thing, which is probably not what you want: if 1 out of 10 streams is bad you
// probably want to print some stream error message for the bad stream but keep chugging along
// for the 9 others.
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
