/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write

import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.integrations.destination.snowflake.SnowflakeBeanFactory
import io.airbyte.integrations.destination.snowflake.cdk.SnowflakeMigratingConfigurationSpecificationSupplier
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfigurationFactory
import java.nio.file.Files
import java.time.Instant
import java.time.temporal.ChronoUnit

object SnowflakeRawDataCleaner : DestinationCleaner {
    override fun cleanup() {
        val config =
            SnowflakeConfigurationFactory()
                .make(
                    SnowflakeMigratingConfigurationSpecificationSupplier(
                            Files.readString(RAW_CONFIG_PATH)
                        )
                        .get()
                )
        val dataSource =
            SnowflakeBeanFactory()
                .snowflakeDataSource(snowflakeConfiguration = config, airbyteEdition = "COMMUNITY")

        dataSource.use { ds ->
            ds.connection.use { connection ->
                val statement = connection.createStatement()
                val sql =
                    """SHOW TABLES
                    IN SCHEMA "${config.internalTableSchema?.toSnowflakeCompatibleName()}" 
                    STARTS WITH 'test'
                """.trimIndent()
                val tables = statement.executeQuery(sql)
                while (tables.next()) {
                    val databaseName = tables.getString("database_name")
                    val schemaName = tables.getString("schema_name")
                    val tableName = tables.getString("name")
                    val createdOn = tables.getTimestamp("created_on").toInstant()
                    // Clear all raw test tables in the database older than 24 hours
                    if (createdOn.isBefore(Instant.now().minus(24, ChronoUnit.HOURS))) {
                        val fullyQualifiedTable = "\"$databaseName\".\"$schemaName\".\"$tableName\""
                        statement.execute("DROP TABLE IF EXISTS $fullyQualifiedTable CASCADE")
                    }
                }
            }
        }
    }
}
