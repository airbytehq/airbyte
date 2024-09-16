/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.migrations

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.jdbc.ColumnDefinition
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.LinkedHashMap

private val log = KotlinLogging.logger {}

class SnowflakeAbMetaAndGenIdMigration(private val database: JdbcDatabase) :
    Migration<SnowflakeState> {
    override fun migrateIfNecessary(
        destinationHandler: DestinationHandler<SnowflakeState>,
        stream: StreamConfig,
        state: DestinationInitialStatus<SnowflakeState>
    ): Migration.MigrationResult<SnowflakeState> {
        if (!state.initialRawTableStatus.rawTableExists) {
            // The raw table doesn't exist. No migration necessary. Update the state.
            log.info {
                "Skipping airbyte_meta/generation_id migration for ${stream.id.originalNamespace}.${stream.id.originalName} " +
                    "because the raw table doesn't exist. GenerationId=${stream.generationId}, " +
                    "minimumGenerationId = ${stream.minimumGenerationId}, postImportAction=${stream.postImportAction}"
            }
            return Migration.MigrationResult(
                state.destinationState.copy(isAirbyteMetaPresentInRaw = true),
                false
            )
        }

        // Snowflake will match the lowercase raw table even with QUOTED_IDENTIFIER_IGNORE_CASE =
        // TRUE
        val results =
            database.queryJsons(
                "SHOW COLUMNS IN TABLE \"${stream.id.rawNamespace}\".\"${stream.id.rawName}\""
            )
        val rawTableDefinition =
            results
                .groupBy { it.get("schema_name").asText()!! }
                .mapValues { (_, v) ->
                    v.groupBy { it.get("table_name").asText()!! }
                        .mapValuesTo(LinkedHashMap()) { (_, v) ->
                            TableDefinition(
                                v.associateTo(LinkedHashMap()) {
                                    // return value of data_type in show columns is a json string.
                                    val dataType = Jsons.deserialize(it.get("data_type").asText())
                                    it.get("column_name").asText()!! to
                                        ColumnDefinition(
                                            it.get("column_name").asText(),
                                            dataType.get("type").asText(),
                                            0,
                                            dataType.get("nullable").asBoolean(),
                                        )
                                },
                            )
                        }
                }
        // default is lower case raw tables, for accounts with QUOTED_IDENTIFIER_IGNORE_CASE = TRUE
        // we have to match uppercase
        val isUpperCaseIdentifer =
            !rawTableDefinition.containsKey(stream.id.rawNamespace) &&
                rawTableDefinition.containsKey(stream.id.rawNamespace.uppercase())
        val rawNamespace: String
        val rawName: String
        val abMetaColumn: String
        if (isUpperCaseIdentifer) {
            rawNamespace = stream.id.rawNamespace.uppercase()
            rawName = stream.id.rawName.uppercase()
            abMetaColumn = JavaBaseConstants.COLUMN_NAME_AB_META.uppercase()
        } else {
            rawNamespace = stream.id.rawNamespace
            rawName = stream.id.rawName
            abMetaColumn = JavaBaseConstants.COLUMN_NAME_AB_META
        }
        rawTableDefinition[rawNamespace]?.get(rawName)?.let { tableDefinition ->
            if (tableDefinition.columns.containsKey(abMetaColumn)) {
                log.info {
                    "Skipping airbyte_meta/generation_id migration for ${stream.id.originalNamespace}.${stream.id.originalName} " +
                        "because the raw table already has the airbyte_meta column"
                }
            } else {
                log.info {
                    "Migrating airbyte_meta/generation_id for table ${stream.id.rawNamespace}.${stream.id.rawName}"
                }
                // Quote for raw table columns
                val alterRawTableSql =
                    """
                        ALTER TABLE "${stream.id.rawNamespace}"."${stream.id.rawName}" 
                        ADD COLUMN "${JavaBaseConstants.COLUMN_NAME_AB_META}" VARIANT, 
                            COLUMN "${JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID}" INTEGER;
                            """.trimIndent()
                database.execute(alterRawTableSql)
            }
        }

        // To avoid another metadata query in Snowflake, we rely on the initial status gathering
        // which already checks for the columns in the final table to indicate schema mismatch
        // to safeguard if the schema mismatch is due to meta columns or customer's column
        // executing an add column with if not exists check
        if (state.isFinalTablePresent && state.isSchemaMismatch) {
            log.info {
                "Migrating generation_id for table ${stream.id.finalNamespace}.${stream.id.finalName}"
            }
            // explicitly uppercase and quote the final table column.
            val alterFinalTableSql =
                """
                ALTER TABLE "${stream.id.finalNamespace}"."${stream.id.finalName}" 
                ADD COLUMN IF NOT EXISTS "${JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID.uppercase()}" INTEGER;
            """.trimIndent()
            database.execute(alterFinalTableSql)
            // Final table schema changed, fetch the initial status again
            return Migration.MigrationResult(
                state.destinationState.copy(isAirbyteMetaPresentInRaw = true),
                true
            )
        } else if (!state.isFinalTablePresent) {
            log.info {
                "skipping migration of generation_id for table ${stream.id.finalNamespace}.${stream.id.finalName} because final table doesn't exist"
            }
        } else {
            log.info {
                "skipping migration of generation_id for table ${stream.id.finalNamespace}.${stream.id.finalName} because schemas match"
            }
        }

        // Final table is untouched, so we don't need to fetch the initial status
        return Migration.MigrationResult(
            state.destinationState.copy(isAirbyteMetaPresentInRaw = true),
            false
        )
    }
}
