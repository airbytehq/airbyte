/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.write.load

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.test.util.SchemaDumper
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.clickhouse.client.ClickhouseAirbyteClient
import io.mockk.mockk

object ClickhouseSchemaDumper : SchemaDumper {
    override suspend fun discoverSchema(
        spec: ConfigurationSpecification,
        namespace: String?,
        name: String
    ): String {
        val config = ClickhouseSpecToConfig.specToConfig(spec)
        val schemaEvolutionClient =
            ClickhouseAirbyteClient(
                ClientProvider.getClient(config),
                sqlGenerator = mockk(),
                tempTableNameGenerator = mockk(),
            )
        val baseSchema =
            Jsons.writerWithDefaultPrettyPrinter()
                .writeValueAsString(
                    schemaEvolutionClient.discoverSchema(
                        TableName(namespace ?: config.resolvedDatabase, name)
                    )
                )
        val additionalInfo = "TODO fetch table engine"
        return baseSchema + "\n" + additionalInfo
    }
}
