package io.airbyte.integrations.destination.snowflake.typing_deduping.migrations

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.typing_deduping.*
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import org.jooq.Field
import org.jooq.conf.ParamType
import org.jooq.impl.DSL.*
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/*
Slightly sketchy to accept a JdbcDatabase here. Migrations should generally prefer to use the
DestinationHandler argument in [migrateIfNecessary] to execute SQL, and DestinationInitialState for
deciding whether a migration is necessary. However, in this case, we need to actually query for data
in the raw table. There's no performance win to doing this via DestinationHandler.gatherInitialState,
since we need to query each table separately anyway. So we just take the database here. However, we
_do_ still use destinationHandler.execute, because that gives us debug SQL logs for when we run the
actual migration.
*/
class ExtractedAtUtcTimezoneMigration(private val database: JdbcDatabase) : Migration<SnowflakeState> {
  private val logger: Logger = LoggerFactory.getLogger(ExtractedAtUtcTimezoneMigration::class.java)

  override fun requireMigration(state: SnowflakeState): Boolean {
    return !state.extractedAtInUtc
  }

  override fun migrateIfNecessary(destinationHandler: DestinationHandler<SnowflakeState>, stream: StreamConfig, state: DestinationInitialState<SnowflakeState>): Migration.MigrationResult<SnowflakeState> {
    if (!state.initialRawTableState.rawTableExists) {
      // The raw table doesn't exist. No migration necessary. Update the state.
      logger.info("Skipping ExtractedAtUtcTimezoneMigration for ${state.streamConfig.id.originalNamespace}.${state.streamConfig.id.originalName} because the raw table doesn't exist")
      return Migration.MigrationResult(state.destinationState.copy(extractedAtInUtc = true), false)
    }

    val rawRecordTimezone: JsonNode? = database.queryJsons(
        { connection ->
          connection.prepareStatement(
              select(
                  field(sql("extract(timezone_hour from \"_airbyte_extracted_at\")")).`as`("tzh"),
                  field(sql("extract(timezone_minute from \"_airbyte_extracted_at\")")).`as`("tzm")
              ).from(table(quotedName(stream.id().rawNamespace, stream.id().rawName)))
                  .limit(1)
                  .getSQL(ParamType.INLINED))
        },
        { rs ->
          (Jsons.emptyObject() as ObjectNode)
              .put("tzh", rs.getInt("tzh"))
              .put("tzm", rs.getInt("tzm"))
        }
    ).first()
    if (rawRecordTimezone == null
        || (rawRecordTimezone.get("tzh").intValue() == 0 && rawRecordTimezone.get("tzm").intValue() == 0)) {
      // There are no raw records, or the raw records are already in UTC. No migration necessary. Update the state.
      logger.info("Skipping ExtractedAtUtcTimezoneMigration for ${state.streamConfig.id.originalNamespace}.${state.streamConfig.id.originalName} because the raw table doesn't contain records needing migration.")
      return Migration.MigrationResult(state.destinationState.copy(extractedAtInUtc = true), false)
    }

    logger.info("Executing ExtractedAtUtcTimezoneMigration for ${state.streamConfig.id.originalNamespace}.${state.streamConfig.id.originalName} for real.")

    destinationHandler.execute(Sql.of(
        update(table(quotedName(stream.id().rawNamespace, stream.id().rawName)))
            .set(
                field(quotedName(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT)),
                // this is the easiest way to forcibly set the offset on a timestamptz.
                // We convert to timestamp_ntz to remove the offset,
                // then convert to string and append a 'Z' offset,
                // then convert back to timestamp_tz.
                // We _could_ go through convert_timezone and manually add a negative offset number of hours
                // but that's a lot more work for no real benefit.
                field(sql("""
                  cast(cast(cast("_airbyte_extracted_at" as timestampntz) as string) || 'Z' as timestamptz)
                  """.trimIndent())) as Any
            ).getSQL(ParamType.INLINED))
    )

    // Invalidate the initial state - we've modified all the extracted_at timestamps, so need to refetch them.
    return Migration.MigrationResult(state.destinationState.copy(needsSoftReset = true, extractedAtInUtc = true), true)
  }

}
