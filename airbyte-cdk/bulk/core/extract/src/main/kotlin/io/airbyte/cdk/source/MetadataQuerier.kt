/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.source

import io.airbyte.cdk.command.SourceConfiguration

/** A very thin abstraction around JDBC metadata queries. */
interface MetadataQuerier : AutoCloseable {
    /**
     * Queries the information_schema for all table names in the schemas specified by the connector
     * configuration.
     */
    fun streamNamespaces(): List<String>

    fun streamNames(streamNamespace: String?): List<String>

    /** Executes a SELECT * on the table, discards the results, and extracts all column metadata. */
    fun fields(
        streamName: String,
        streamNamespace: String?,
    ): List<Field>

    /** Queries the information_schema for any primary key on the given table. */
    fun primaryKey(
        streamName: String,
        streamNamespace: String?,
    ): List<List<String>>

    /** Factory for [MetadataQuerier] instances. */
    fun interface Factory<T : SourceConfiguration> {
        /** An implementation might open a connection to build a [MetadataQuerier] instance. */
        fun session(config: T): MetadataQuerier
    }
}
