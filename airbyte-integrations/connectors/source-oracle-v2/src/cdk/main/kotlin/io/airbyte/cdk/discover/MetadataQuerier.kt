/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.discover

import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.jdbc.JdbcMetadataQuerier
import io.micronaut.context.annotation.DefaultImplementation

/** A very thin abstraction around JDBC metadata queries. */
interface MetadataQuerier : AutoCloseable {

    /**
     * Queries the information_schema for all table names in the schemas specified by the connector
     * configuration.
     */
    fun tableNames(): List<TableName>

    /** Executes a SELECT * on the table, discards the results, and extracts all column metadata. */
    fun columnMetadata(table: TableName): List<ColumnMetadata>

    /** Queries the information_schema for all primary keys for the given table. */
    fun primaryKeys(table: TableName): List<List<String>>

    /** Factory for [MetadataQuerier] instances. */
    @DefaultImplementation(JdbcMetadataQuerier.Factory::class)
    interface Factory {

        /** [DiscoverMapper] which is required by the [MetadataQuerier] instances. */
        val discoverMapper: DiscoverMapper

        /** An implementation might open a connection to build a [MetadataQuerier] instance. */
        fun session(config: SourceConfiguration): MetadataQuerier
    }
}
