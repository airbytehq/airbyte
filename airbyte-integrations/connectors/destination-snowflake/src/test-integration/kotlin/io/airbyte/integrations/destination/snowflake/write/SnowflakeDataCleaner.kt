/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write

import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.integrations.destination.snowflake.SnowflakeBeanFactory
import io.airbyte.integrations.destination.snowflake.cdk.SnowflakeMigratingConfigurationSpecificationSupplier
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfigurationFactory
import io.airbyte.integrations.destination.snowflake.sql.STAGE_NAME_PREFIX
import java.nio.file.Files
import java.sql.Connection
import java.time.Instant
import java.time.Period

private val RETENTION_PERIOD = Period.ofDays(1)

object SnowflakeDataCleaner : DestinationCleaner {
    override fun cleanup() {
        val config =
            SnowflakeConfigurationFactory()
                .make(
                    SnowflakeMigratingConfigurationSpecificationSupplier(
                            Files.readString(CONFIG_PATH)
                        )
                        .get()
                )
        val dataSource =
            SnowflakeBeanFactory()
                .snowflakeDataSource(snowflakeConfiguration = config, airbyteEdition = "COMMUNITY")
        dataSource.use { ds ->
            ds.connection.use { connection ->
                when (config.legacyRawTablesOnly) {
                    true -> cleanRawData(connection, config)
                    else -> cleanNormalizedData(connection, config)
                }
            }
        }
    }

    private fun cleanNormalizedData(connection: Connection, config: SnowflakeConfiguration) {
        val statement = connection.createStatement()
        val schemas =
            statement.executeQuery(
                "SHOW SCHEMAS IN DATABASE \"${config.database.toSnowflakeCompatibleName()}\""
            )
        while (schemas.next()) {
            val schemaName = schemas.getString("name")
            val createdOn = schemas.getTimestamp("created_on")
            // Clear all test schemas in the database older than 24 hours
            if (
                schemaName.startsWith(prefix = "test", ignoreCase = true) &&
                    createdOn.toInstant().isBefore(Instant.now().minus(RETENTION_PERIOD))
            ) {
                statement.execute("DROP SCHEMA IF EXISTS \"$schemaName\" CASCADE")
            }
        }
    }

    private fun cleanRawData(connection: Connection, config: SnowflakeConfiguration) {
        val statement = connection.createStatement()
        val tableSql =
            """SHOW TABLES
                    IN SCHEMA "${config.internalTableSchema?.toSnowflakeCompatibleName()}" 
                    STARTS WITH 'test'
                """.trimIndent()
        val tables = statement.executeQuery(tableSql)
        while (tables.next()) {
            val databaseName = tables.getString("database_name")
            val schemaName = tables.getString("schema_name")
            val tableName = tables.getString("name")
            val createdOn = tables.getTimestamp("created_on").toInstant()
            // Clear all raw test tables in the database older than 24 hours
            if (createdOn.isBefore(Instant.now().minus(RETENTION_PERIOD))) {
                val fullyQualifiedTable = "\"$databaseName\".\"$schemaName\".\"$tableName\""
                statement.execute("DROP TABLE IF EXISTS $fullyQualifiedTable CASCADE")
            }
        }

        val stagesSql =
            """SHOW STAGES
                    IN SCHEMA "${config.internalTableSchema?.toSnowflakeCompatibleName()}" 
                    STARTS WITH '${STAGE_NAME_PREFIX}test'
                """.trimIndent()
        val stages = statement.executeQuery(stagesSql)
        while (stages.next()) {
            val databaseName = tables.getString("database_name")
            val schemaName = tables.getString("schema_name")
            val stageName = tables.getString("name")
            val createdOn = tables.getTimestamp("created_on").toInstant()
            // Clear all raw staging tables in the database older than 24 hours
            if (createdOn.isBefore(Instant.now().minus(RETENTION_PERIOD))) {
                val fullyQualifiedTable = "\"$databaseName\".\"$schemaName\".\"$stageName\""
                statement.execute("DROP TABLE IF EXISTS $fullyQualifiedTable CASCADE")
            }
        }
    }
}
