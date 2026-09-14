/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

import io.airbyte.cdk.load.component.TableSchema

/**
 * Destinations will eventually all have a
 * [io.airbyte.cdk.load.component.TableSchemaEvolutionClient] for most purposes. However, some
 * destinations want to assert against more than just the column names+types; this interface
 * supports arbitrary information. For example, destination-clickhouse can include the TableEngine
 * definition.
 */
interface SchemaDumper {
    /**
     * for destinations that already have a TableSchemaEvolutionClient, this can be as simple as
     * ```kotlin
     * // figure out the table name as needed
     * val tableName = TableName(namespace ?: config.resolvedDatabase, name)
     * return FullTableSchema(client.discoverSchema(tableName))
     * ```
     *
     * But you can add other stuff into the additionalInfo field as needed (clickhouse table engine,
     * bigquery clustering/partitioning keys, postgres indexes, etc.).
     */
    suspend fun discoverSchema(namespace: String?, name: String): FullTableSchema
}

/**
 * Some destinations only care about the column names+types, which are fully represented by
 * [TableSchema]. For destinations that care about other stuff, there's an [additionalInfo] field.
 */
data class FullTableSchema(
    val tableSchema: TableSchema,
    val additionalInfo: Map<String, Any?> = emptyMap(),
)
