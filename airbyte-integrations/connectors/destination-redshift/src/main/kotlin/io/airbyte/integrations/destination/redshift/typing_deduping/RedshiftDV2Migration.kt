/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcV1V2Migrator
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.github.oshai.kotlinlogging.KotlinLogging

private val logger = KotlinLogging.logger {}

class RedshiftDV2Migration(
    namingConventionTransformer: NamingConventionTransformer,
    database: JdbcDatabase,
    databaseName: String,
    private val sqlGenerator: RedshiftSqlGenerator,
) : Migration<RedshiftState> {
    private val legacyV1V2migrator =
        JdbcV1V2Migrator(namingConventionTransformer, database, databaseName)
    override fun migrateIfNecessary(
        destinationHandler: DestinationHandler<RedshiftState>,
        stream: StreamConfig,
        state: DestinationInitialStatus<RedshiftState>
    ): Migration.MigrationResult<RedshiftState> {
        logger.info { "Initializing DV2 Migration check" }
        legacyV1V2migrator.migrateIfNecessary(sqlGenerator, destinationHandler, stream)
        return Migration.MigrationResult(
            RedshiftState(
                needsSoftReset = false,
                isAirbyteMetaPresentInRaw = false,
                isGenerationIdPresent = false
            ),
            true,
        )
    }
}
