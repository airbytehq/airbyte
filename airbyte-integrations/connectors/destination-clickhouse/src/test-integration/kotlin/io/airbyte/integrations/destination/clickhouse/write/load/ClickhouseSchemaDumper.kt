/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.write.load

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.test.util.FullTableSchema
import io.airbyte.cdk.load.test.util.SchemaDumper
import io.airbyte.integrations.destination.clickhouse.Utils
import kotlinx.coroutines.future.await

class ClickhouseSchemaDumper(spec: ConfigurationSpecification) : SchemaDumper {
    private val config = Utils.specToConfig(spec)
    private val client = Utils.getClickhouseClient(spec)
    private val airbyteClient = Utils.getClickhouseAirbyteClient(spec)

    override suspend fun discoverSchema(namespace: String?, name: String): FullTableSchema {
        val tableName = TableName(namespace ?: config.resolvedDatabase, name)
        val tableSchema = airbyteClient.discoverSchema(tableName)

        val tableEngine =
            client
                .newBinaryFormatReader(
                    client
                        .query(
                            """
                        SELECT engine_full FROM system.tables
                        WHERE database = {database:String} AND name = {name:String}
                        """.trimIndent(),
                            mapOf(
                                "database" to tableName.namespace,
                                "name" to tableName.name,
                            ),
                        )
                        .await()
                )
                .use { reader ->
                    reader.next()
                    reader.getString("engine_full")
                }
        // baseSchema has newlines, so if we just do """...""".trimIndent(), it ends up kind of ugly
        return FullTableSchema(
            tableSchema,
            mapOf("tableEngine" to tableEngine),
        )
    }
}
