/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.airbyte.integrations.destination.redshift.constants.RedshiftDestinationConstants.SUPER_TYPE
import org.jooq.conf.ParamType
import org.jooq.impl.DSL
import org.jooq.impl.DSL.name
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class RedshiftRawTableAirbyteMetaMigration(
    private val database: JdbcDatabase,
    private val databaseName: String
) : Migration<RedshiftState> {
    private val logger: Logger =
        LoggerFactory.getLogger(RedshiftRawTableAirbyteMetaMigration::class.java)

    override fun migrateIfNecessary(
        destinationHandler: DestinationHandler<RedshiftState>,
        stream: StreamConfig,
        state: DestinationInitialStatus<RedshiftState>
    ): Migration.MigrationResult<RedshiftState> {
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

        val existingRawTable =
            JdbcDestinationHandler.findExistingTable(
                    database,
                    databaseName,
                    stream.id.rawNamespace,
                    stream.id.rawName
                )
                // The table should exist because we checked for it above
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
            "Executing RawTableAirbyteMetaMigration for ${stream.id.originalNamespace}.${stream.id.originalName} for real"
        )
        destinationHandler.execute(
            getRawTableMetaColumnAddDdl(stream.id.rawNamespace, stream.id.rawName)
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

    fun getRawTableMetaColumnAddDdl(namespace: String, name: String): Sql {
        return Sql.of(
            DSL.alterTable(name(namespace, name))
                .addColumn(name(JavaBaseConstants.COLUMN_NAME_AB_META), SUPER_TYPE)
                .getSQL(ParamType.INLINED)
        )
    }
}
