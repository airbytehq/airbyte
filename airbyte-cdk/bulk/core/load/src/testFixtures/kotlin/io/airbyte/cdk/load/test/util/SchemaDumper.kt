/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

/**
 * Most destinations will eventually have a
 * [io.airbyte.cdk.load.component.TableSchemaEvolutionClient] instead. However, some destinations
 * want to assert against more than just the column names+types; this interface supports arbitrary
 * information. For example, destination-clickhouse can include the TableEngine definition.
 */
interface SchemaDumper {
    /**
     * for destinations that already have a TableSchemaEvolutionClient, this is typically just
     * ```
     * return Jsons.writerWithDefaultPrettyPrinter()
     *   .writeValueAsString(client.discoverSchema(<something>))
     * ```
     * Converting namespace+name to TableName is doable but slightly nontrivial, e.g.
     * ```kotlin
     * val tableName = TableName(namespace ?: config.resolvedDatabase, name)
     * ```
     *
     * Your connector can append additional information as needed.
     */
    suspend fun discoverSchema(namespace: String?, name: String): String
}
