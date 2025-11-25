/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.datagen

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

class DataGenSourceMetadataQuerier(val configuration: DataGenSourceConfiguration) :
    MetadataQuerier {

    override fun extraChecks() {}

    override fun close() {
        // Nothing to do here.
    }

    override fun fields(streamID: StreamIdentifier): List<Field> {
        val flavor = configuration.flavor
        return flavor.fields[streamID.name] ?: emptyList()
    }

    override fun streamNamespaces(): List<String> {
        return listOf(configuration.flavor.namespace)
    }

    override fun streamNames(streamNamespace: String?): List<StreamIdentifier> {
        return configuration.flavor.tableNames
            .map { tableName ->
                StreamDescriptor().withName(tableName).withNamespace(streamNamespace)
            }
            .map(StreamIdentifier::from)
    }

    override fun primaryKey(
        streamID: StreamIdentifier,
    ): List<List<String>> {
        return configuration.flavor.primaryKeys[streamID.name] ?: listOf()
    }

    /** DataGen implementation of [MetadataQuerier.Factory]. */
    @Singleton
    @Primary
    class Factory() : MetadataQuerier.Factory<DataGenSourceConfiguration> {
        /** The [SourceConfiguration] is deliberately not injected in order to support tests. */
        override fun session(config: DataGenSourceConfiguration): MetadataQuerier {
            return DataGenSourceMetadataQuerier(config)
        }
    }
}
