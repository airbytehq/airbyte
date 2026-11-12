/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.test.util.FullTableSchema
import io.airbyte.cdk.load.test.util.SchemaDumper

/**
 * Discovers Databricks table schemas for regression tests. Delegates to
 * [DatabricksAirbyteClient.discoverSchema].
 */
class DatabricksSchemaDumper(spec: ConfigurationSpecification) : SchemaDumper {
    private val config = DatabricksTestConfigProvider.configFrom(spec)
    private val client = DatabricksTestConfigProvider.airbyteClientFrom(spec)

    override suspend fun discoverSchema(namespace: String?, name: String): FullTableSchema {
        val resolvedNamespace = (namespace ?: config.schema).lowercase()
        val tableName = TableName(namespace = resolvedNamespace, name = name.lowercase())
        val schema = client.discoverSchema(tableName)
        return FullTableSchema(schema)
    }
}
