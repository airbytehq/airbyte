/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.migrations

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeSqlGenerator
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeV1V2Migrator
import io.github.oshai.kotlinlogging.KotlinLogging

private val log = KotlinLogging.logger {}

class SnowflakeDV2Migration(
    namingConventionTransformer: NamingConventionTransformer,
    jdbcDatabase: JdbcDatabase,
    databaseName: String,
    private val sqlGenerator: SnowflakeSqlGenerator
) : Migration<SnowflakeState> {
    private val legacyV1V2migrator =
        SnowflakeV1V2Migrator(namingConventionTransformer, jdbcDatabase, databaseName)
    override fun migrateIfNecessary(
        destinationHandler: DestinationHandler<SnowflakeState>,
        stream: StreamConfig,
        state: DestinationInitialStatus<SnowflakeState>
    ): Migration.MigrationResult<SnowflakeState> {
        log.info { "Initializing DV2 Migration check" }
        legacyV1V2migrator.migrateIfNecessary(sqlGenerator, destinationHandler, stream)
        return Migration.MigrationResult(SnowflakeState(false), true)
    }
}
