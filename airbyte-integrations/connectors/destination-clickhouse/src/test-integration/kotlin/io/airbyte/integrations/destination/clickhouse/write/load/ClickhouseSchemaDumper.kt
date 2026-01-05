/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.write.load

import com.clickhouse.client.api.data_formats.ClickHouseBinaryFormatReader
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.test.util.SchemaDumper
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.clickhouse.client.ClickhouseAirbyteClient
import io.mockk.mockk
import kotlinx.coroutines.future.await

object ClickhouseSchemaDumper : SchemaDumper {
    override suspend fun discoverSchema(
        spec: ConfigurationSpecification,
        namespace: String?,
        name: String
    ): String {
        val config = ClickhouseSpecToConfig.specToConfig(spec)
        val client = ClientProvider.getClient(config)
        val airbyteClient =
            ClickhouseAirbyteClient(
                client,
                sqlGenerator = mockk(),
                tempTableNameGenerator = mockk(),
            )
        val tableName = TableName(namespace ?: config.resolvedDatabase, name)
        val baseSchema =
            Jsons.writerWithDefaultPrettyPrinter()
                .writeValueAsString(airbyteClient.discoverSchema(tableName))

        val engineQueryResponse =
            client
                .query(
                    "SELECT engine_full FROM system.tables WHERE database = {database:String} AND name = {name:String}",
                    mapOf(
                        "database" to tableName.namespace,
                        "name" to tableName.name,
                    ),
                )
                .await()
        val reader: ClickHouseBinaryFormatReader = client.newBinaryFormatReader(engineQueryResponse)
        reader.next()
        val tableEngine = reader.getString("engine_full")
        // baseSchema has newlines, so if we just do """...""".trimIndent(), it ends up kind of ugly
        return StringBuilder()
            .apply {
                append("Schema: ")
                append(baseSchema)
                append("\n")
                append("Table Engine: ")
                append(tableEngine)
            }
            .toString()
    }
}
