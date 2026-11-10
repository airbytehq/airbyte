/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write

import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.integrations.destination.snowflake.SnowflakeBeanFactory
import io.airbyte.integrations.destination.snowflake.cdk.SnowflakeMigratingConfigurationSpecificationSupplier
import io.airbyte.integrations.destination.snowflake.schema.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfigurationFactory
import io.airbyte.integrations.destination.snowflake.sql.escapeJsonIdentifier
import io.airbyte.integrations.destination.snowflake.sql.quote
import java.nio.file.Files
import java.time.Instant
import java.time.Period

private val RETENTION_PERIOD = Period.ofDays(1)

/**
 * Drops every `test*` schema in the test database that is older than [RETENTION_PERIOD].
 *
 * This is sufficient because every artifact the integration tests create lives in such a schema:
 * final tables in the per-test namespace, and raw tables / temp tables / stages in the
 * `test`-prefixed internal schema that [SnowflakeMigrationConfigurationUpdater] points
 * `raw_data_schema` at. `DROP SCHEMA ... CASCADE` takes the tables and stages with it.
 */
object SnowflakeDataCleaner : DestinationCleaner {
    override fun cleanup() {
        val config =
            SnowflakeConfigurationFactory()
                .make(
                    SnowflakeMigratingConfigurationSpecificationSupplier(
                            Files.readString(CONFIG_PATH),
                        )
                        .get(),
                )
        val dataSource =
            SnowflakeBeanFactory()
                .snowflakeDataSource(snowflakeConfiguration = config, airbyteEdition = "COMMUNITY")
        dataSource.use { ds ->
            ds.connection.use { connection ->
                val statement = connection.createStatement()
                val schemas =
                    statement.executeQuery(
                        "SHOW SCHEMAS IN DATABASE ${config.database.toSnowflakeCompatibleName().quote()}",
                    )
                while (schemas.next()) {
                    val schemaName = schemas.getString("name")
                    val createdOn = schemas.getTimestamp("created_on")
                    if (
                        schemaName.startsWith(prefix = "test", ignoreCase = true) &&
                            createdOn.toInstant().isBefore(Instant.now().minus(RETENTION_PERIOD))
                    ) {
                        statement.execute(
                            "DROP SCHEMA IF EXISTS \"${escapeJsonIdentifier(schemaName)}\" CASCADE",
                        )
                    }
                }
            }
        }
    }
}
