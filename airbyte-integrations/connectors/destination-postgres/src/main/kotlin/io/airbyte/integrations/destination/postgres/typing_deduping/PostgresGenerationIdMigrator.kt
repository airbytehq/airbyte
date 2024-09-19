/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.typing_deduping

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.github.oshai.kotlinlogging.KotlinLogging
import org.jooq.conf.ParamType
import org.jooq.impl.DSL
import org.jooq.impl.SQLDataType

private val logger = KotlinLogging.logger {}

class PostgresGenerationIdMigration(
    private val database: JdbcDatabase,
    private val databaseName: String
) : Migration<PostgresState> {
    // TODO: This class is almost similar to RedshiftAirbyteMetaMigration except the JSONB type.
    // try to unify later.
    override fun migrateIfNecessary(
        destinationHandler: DestinationHandler<PostgresState>,
        stream: StreamConfig,
        state: DestinationInitialStatus<PostgresState>
    ): Migration.MigrationResult<PostgresState> {
        var needsStateRefresh = false
        if (state.initialRawTableStatus.rawTableExists) {
            // The table should exist because we checked for it above, so safe to get it.
            val existingRawTable =
                JdbcDestinationHandler.findExistingTable(
                        database,
                        databaseName,
                        stream.id.rawNamespace,
                        stream.id.rawName
                    )
                    .get()

            if (existingRawTable.columns[JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID] != null) {
                // The raw table already has the _airbyte_meta column. No migration necessary.
                logger.info(
                    "Skipping migration for ${stream.id.rawNamespace}.${stream.id.rawName}'s raw table because the generation_id column is already present"
                )
            } else {
                logger.info(
                    "Executing migration for ${stream.id.rawNamespace}.${stream.id.rawName}'s raw table for real"
                )

                needsStateRefresh = true
                destinationHandler.execute(
                    Sql.of(
                        DSL.alterTable(DSL.name(stream.id.rawNamespace, stream.id.rawName))
                            .addColumn(
                                DSL.name(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID),
                                SQLDataType.BIGINT.nullable(true)
                            )
                            .getSQL(ParamType.INLINED)
                    )
                )
            }
        }

        val maybeExistingFinalTable =
            JdbcDestinationHandler.findExistingTable(
                database,
                databaseName,
                stream.id.finalNamespace,
                stream.id.finalName
            )
        if (maybeExistingFinalTable.isEmpty) {
            logger.info(
                "Stopping migration for ${stream.id.originalNamespace}.${stream.id.originalName} because the final table doesn't exist"
            )
            return Migration.MigrationResult(
                state.destinationState.copy(isAirbyteGenerationIdPresent = true),
                needsStateRefresh
            )
        }
        val existingFinalTable = maybeExistingFinalTable.get()
        if (existingFinalTable.columns[JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID] != null) {
            // The raw table already has the _airbyte_meta column. No migration necessary. Update
            // the state.
            logger.info(
                "Skipping migration for ${stream.id.finalNamespace}.${stream.id.finalName} because the generation_id column is already present"
            )
        } else {
            logger.info(
                "Executing migration for ${stream.id.finalNamespace}.${stream.id.finalName} for real"
            )

            needsStateRefresh = true
            destinationHandler.execute(
                Sql.of(
                    DSL.alterTable(DSL.name(stream.id.finalNamespace, stream.id.finalName))
                        .addColumn(
                            DSL.name(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID),
                            SQLDataType.BIGINT.nullable(true)
                        )
                        .getSQL(ParamType.INLINED)
                )
            )
        }

        // We will not do a soft reset since it could be time-consuming, instead we leave the old
        // data i.e. `errors` instead of `changes` as is since this column is controlled by us.
        return Migration.MigrationResult(
            state.destinationState.copy(
                needsSoftReset = false,
                isAirbyteGenerationIdPresent = true
            ),
            needsStateRefresh
        )
    }
}
