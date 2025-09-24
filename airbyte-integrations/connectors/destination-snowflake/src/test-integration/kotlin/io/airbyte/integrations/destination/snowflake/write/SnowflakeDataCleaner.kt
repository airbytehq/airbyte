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
                            createdOn
                                .toInstant()
                                .isBefore(Instant.now().minus(24, ChronoUnit.HOURS))
                    ) {
                        statement.execute("DROP SCHEMA IF EXISTS \"$schemaName\" CASCADE")
                    }
                }
            }
        }
    }
}
