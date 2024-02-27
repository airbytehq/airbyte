package io.airbyte.integrations.destination.redshift.typing_deduping

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialState
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftSqlGenerator.SUPER_DATA_TYPE
import org.jooq.conf.ParamType
import org.jooq.impl.DSL
import org.jooq.impl.DSL.quotedName
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class RedshiftRawTableAirbyteMetaMigration(
    private val database: JdbcDatabase,
    private val databaseName: String
): Migration<RedshiftState> {
  private val logger: Logger = LoggerFactory.getLogger(RedshiftRawTableAirbyteMetaMigration::class.java)

  override fun requireMigration(state: RedshiftState): Boolean = !state.rawTableHasAirbyteMeta

  override fun migrateIfNecessary(
      destinationHandler: DestinationHandler<RedshiftState>,
      stream: StreamConfig,
      state: DestinationInitialState<RedshiftState>
  ): Migration.MigrationResult<RedshiftState> {
    if (!state.initialRawTableState.rawTableExists) {
      // The raw table doesn't exist. No migration necessary. Update the state.
      logger.info("Skipping RawTableAirbyteMetaMigration for ${stream.id.originalNamespace}.${stream.id.originalName} because the raw table doesn't exist")
      return Migration.MigrationResult(state.destinationState.copy(rawTableHasAirbyteMeta = true), false)
    }

    val existingRawTable = JdbcDestinationHandler
        .findExistingTable(database, databaseName, stream.id.rawNamespace, stream.id.rawName)
        // The table should exist because we checked for it above
        .get()
    if (existingRawTable.columns[JavaBaseConstants.COLUMN_NAME_AB_META] != null) {
      // The raw table already has the _airbyte_meta column. No migration necessary. Update the state.
      return Migration.MigrationResult(state.destinationState.copy(rawTableHasAirbyteMeta = true), false)
    }


    logger.info("Executing RawTableAirbyteMetaMigration for ${stream.id.originalNamespace}.${stream.id.originalName} for real")
    destinationHandler.execute(Sql.of(
        DSL.alterTable(quotedName(stream.id.rawNamespace, stream.id.rawName))
            .addColumn(quotedName(JavaBaseConstants.COLUMN_NAME_AB_META), SUPER_DATA_TYPE)
            .getSQL(ParamType.INLINED)
    ))

    // Update the state. We didn't modify the table in a relevant way, so don't invalidate the InitialState.
    // We do need a soft reset, to rebuild the final table with updated airbyte_meta
    // (i.e. `changes` instead of `errors`).
    return Migration.MigrationResult(
        state.destinationState.copy(needsSoftReset = true, rawTableHasAirbyteMeta = true),
        false)
  }
}
