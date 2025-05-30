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
import io.airbyte.integrations.destination.postgres.typing_deduping.PostgresSqlGenerator.*
import org.jooq.conf.ParamType
import org.jooq.impl.DSL
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class PostgresRawTableAirbyteMetaMigration(
    private val database: JdbcDatabase,
    private val databaseName: String
) : Migration<PostgresState> {
    private val logger: Logger = LoggerFactory.getLogger(this.javaClass)

    // TODO: This class is almost similar to RedshiftAirbyteMetaMigration except the JSONB type.
    // try to unify later.
    override fun migrateIfNecessary(
        destinationHandler: DestinationHandler<PostgresState>,
        stream: StreamConfig,
        state: DestinationInitialStatus<PostgresState>
    ): Migration.MigrationResult<PostgresState> {
        if (!state.initialRawTableStatus.rawTableExists) {
            // The raw table doesn't exist. No migration necessary. Update the state.
            logger.info(
                "Skipping RawTableAirbyteMetaMigration for ${stream.id.originalNamespace}.${stream.id.originalName} because the raw table doesn't exist"
            )
            return Migration.MigrationResult(
                state.destinationState.copy(isAirbyteMetaPresentInRaw = true),
                false
            )
        }

        // The table should exist because we checked for it above, so safe to get it.
        val existingRawTable =
            JdbcDestinationHandler.findExistingTable(
                    database,
                    databaseName,
                    stream.id.rawNamespace,
                    stream.id.rawName
                )
                .get()

        if (existingRawTable.columns[JavaBaseConstants.COLUMN_NAME_AB_META] != null) {
            // The raw table already has the _airbyte_meta column. No migration necessary. Update
            // the state.
            return Migration.MigrationResult(
                state.destinationState.copy(isAirbyteMetaPresentInRaw = true),
                false
            )
        }

        logger.info(
            "Executing RawTableAirbyteMetaMigration for ${stream.id.rawNamespace}.${stream.id.rawName} for real"
        )

        destinationHandler.execute(
            Sql.of(
                DSL.alterTable(DSL.name(stream.id.rawNamespace, stream.id.rawName))
                    .addColumn(
                        DSL.name(JavaBaseConstants.COLUMN_NAME_AB_META),
                        PostgresSqlGenerator.JSONB_TYPE
                    )
                    .getSQL(ParamType.INLINED)
            )
        )

        // Update the state. We didn't modify the table in a relevant way, so don't invalidate the
        // InitialState.
        // We will not do a soft reset since it could be time-consuming, instead we leave the old
        // data i.e. `errors` instead of `changes` as is since this column is controlled by us.
        return Migration.MigrationResult(
            state.destinationState.copy(needsSoftReset = false, isAirbyteMetaPresentInRaw = true),
            false
        )
    }
}
