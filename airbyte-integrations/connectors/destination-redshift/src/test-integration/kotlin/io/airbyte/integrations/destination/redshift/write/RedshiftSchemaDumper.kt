/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.test.util.FullTableSchema
import io.airbyte.cdk.load.test.util.SchemaDumper

/**
 * [SchemaDumper] implementation for Redshift regression tests. Creates a [RedshiftAirbyteClient]
 * via [RedshiftTestConfigProvider] and delegates to [RedshiftAirbyteClient.discoverSchema]
 * [io.airbyte.integrations.destination.redshift.client.RedshiftAirbyteClient.discoverSchema].
 */
class RedshiftSchemaDumper(spec: ConfigurationSpecification) : SchemaDumper {
    private val config = RedshiftTestConfigProvider.configFrom(spec)
    private val airbyteClient = RedshiftTestConfigProvider.airbyteClientFrom(spec)

    override suspend fun discoverSchema(namespace: String?, name: String): FullTableSchema {
        val tableName =
            TableName(
                (namespace ?: config.schema).lowercase(),
                name.lowercase(),
            )
        val tableSchema = airbyteClient.discoverSchema(tableName)
        return FullTableSchema(tableSchema)
    }
}
