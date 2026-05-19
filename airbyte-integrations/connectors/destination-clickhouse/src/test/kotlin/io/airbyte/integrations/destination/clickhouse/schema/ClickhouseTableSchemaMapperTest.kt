/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.schema

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.integrations.destination.clickhouse.client.ClickhouseSqlTypes
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfiguration
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class ClickhouseTableSchemaMapperTest {
    private val mapper =
        ClickhouseTableSchemaMapper(
            config =
                ClickhouseConfiguration(
                    hostname = "hostname",
                    port = "port",
                    protocol = "protocol",
                    database = "database",
                    username = "username",
                    password = "password",
                    enableJson = false,
                    tunnelConfig = SshNoTunnelMethod,
                    recordWindowSize = 42000,
                ),
            tempTableNameGenerator = TempTableNameGenerator { it.copy(name = "${it.name}_tmp") },
        )

    @Test
    fun `toFinalSchema preserves nullable cursor columns in dedupe mode`() {
        val tableSchema =
            StreamTableSchema(
                tableNames = TableNames(finalTableName = TableName("namespace", "table")),
                columnSchema =
                    ColumnSchema(
                        inputSchema = emptyMap(),
                        inputToFinalColumnNames =
                            mapOf("order_id" to "order_id", "updated_at" to "updated_at"),
                        finalSchema =
                            mapOf(
                                "order_id" to ColumnType(ClickhouseSqlTypes.INT64, true),
                                "updated_at" to
                                    ColumnType(
                                        ClickhouseSqlTypes.DATETIME_WITH_PRECISION,
                                        true,
                                    ),
                            ),
                    ),
                importType =
                    Dedupe(
                        primaryKey = listOf(listOf("order_id")),
                        cursor = listOf("updated_at"),
                    ),
            )

        val finalSchema = mapper.toFinalSchema(tableSchema).columnSchema.finalSchema

        assertEquals(false, finalSchema["order_id"]?.nullable)
        assertEquals(true, finalSchema["updated_at"]?.nullable)
    }
}
