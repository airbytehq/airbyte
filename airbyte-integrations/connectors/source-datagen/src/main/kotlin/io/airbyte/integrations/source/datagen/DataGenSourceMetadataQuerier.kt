/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.datagen

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.integrations.source.datagen.flavor.increment.IncrementDataGenerator
import io.airbyte.integrations.source.datagen.flavor.increment.IncrementFlavor
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

private val log = KotlinLogging.logger {}

class DataGenSourceMetadataQuerier() : MetadataQuerier {

    companion object {
        val incrementFlavor = IncrementFlavor
        val flavors = mapOf(incrementFlavor.namespace to incrementFlavor)
    }

    override fun extraChecks() {}

    override fun close() {
        // Nothing to do here.
    }

    override fun fields(streamID: StreamIdentifier): List<Field> {
        val flavor = flavors[streamID.namespace]
        return flavor?.fields?.get(streamID.name) ?: emptyList()
    }

    override fun streamNamespaces(): List<String> {
         return flavors.keys.toList()
    }

    override fun streamNames(streamNamespace: String?): List<StreamIdentifier> {
         val flavor = streamNamespace?.let { flavors[it] } ?: return emptyList()
         return flavor.tableNames
             .map { tableName -> StreamDescriptor().withName(tableName).withNamespace(streamNamespace) }
             .map(StreamIdentifier::from)
    }

    override fun primaryKey(
        streamID: StreamIdentifier,
    ): List<List<String>> {
        val flavor = flavors[streamID.namespace]
        return listOf(flavor?.primaryKey ?: emptyList())
    }

    /** DataGen implementation of [MetadataQuerier.Factory]. */
    @Singleton
    @Primary
    class Factory() : MetadataQuerier.Factory<DataGenSourceConfiguration> {
        /** The [SourceConfiguration] is deliberately not injected in order to support tests. */
        override fun session(config: DataGenSourceConfiguration): MetadataQuerier {
            return DataGenSourceMetadataQuerier()
        }
    }
}
