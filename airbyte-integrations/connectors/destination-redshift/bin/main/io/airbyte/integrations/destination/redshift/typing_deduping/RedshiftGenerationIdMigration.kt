/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.github.oshai.kotlinlogging.KotlinLogging

private val logger = KotlinLogging.logger {}

class RedshiftGenerationIdMigration(
    private val database: JdbcDatabase,
    private val databaseName: String,
) : Migration<RedshiftState> {
    override fun migrateIfNecessary(
        destinationHandler: DestinationHandler<RedshiftState>,
        stream: StreamConfig,
        state: DestinationInitialStatus<RedshiftState>
    ): Migration.MigrationResult<RedshiftState> {
        if (state.destinationState.isGenerationIdPresent) {
            logger.info {
                "Skipping generation_id migration for ${stream.id.originalNamespace}.${stream.id.originalName} because our state says it's already done"
            }
            return Migration.MigrationResult(state.destinationState, invalidateInitialState = false)
        }

        if (!state.initialRawTableStatus.rawTableExists) {
            // The raw table doesn't exist. No migration necessary. Update the state.
            logger.info {
                "Skipping generation_id migration for ${stream.id.originalNamespace}.${stream.id.originalName} because the raw table doesn't exist"
            }
            return Migration.MigrationResult(
                state.destinationState.copy(isGenerationIdPresent = true),
                invalidateInitialState = false
            )
        }

        // Add generation_id to the raw table if necessary
        val rawTableDefinitionQueryResult: List<JsonNode> =
            database.queryJsons(
                """
                SHOW COLUMNS
                FROM TABLE "$databaseName"."${stream.id.rawNamespace}"."${stream.id.rawName}"
                LIKE '${JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID}'
                """.trimIndent()
            )
        if (rawTableDefinitionQueryResult.isNotEmpty()) {
            logger.info {
                "${stream.id.originalNamespace}.${stream.id.originalName}: Skipping generation_id migration for raw table because it already has the generation_id column"
            }
        } else {
            logger.info {
                "Migrating generation_id for table ${stream.id.rawNamespace}.${stream.id.rawName}"
            }
            // Quote for raw table columns
            val alterRawTableSql =
                """
                ALTER TABLE "${stream.id.rawNamespace}"."${stream.id.rawName}" 
                ADD COLUMN "${JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID}" BIGINT;
                """.trimIndent()
            database.execute(alterRawTableSql)
        }

        // Add generation_id to the final table if necessary
        // As a slight optimization, only do this if we previously detected that the final table
        // schema is wrong
        if (state.isFinalTablePresent && state.isSchemaMismatch) {
            val finalTableColumnQueryResult: List<JsonNode> =
                database.queryJsons(
                    """
                SHOW COLUMNS
                FROM TABLE "$databaseName"."${stream.id.finalNamespace}"."${stream.id.finalName}"
                LIKE '${JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID}'
                """.trimIndent()
                )
            if (finalTableColumnQueryResult.isNotEmpty()) {
                logger.info {
                    "${stream.id.originalNamespace}.${stream.id.originalName}: Skipping generation_id migration for final table because it already has the generation_id column"
                }
            } else {
                logger.info {
                    "Migrating generation_id for table ${stream.id.finalNamespace}.${stream.id.finalName}"
                }
                database.execute(
                    """
                    ALTER TABLE "${stream.id.finalNamespace}"."${stream.id.finalName}" 
                    ADD COLUMN "${JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID}" BIGINT NULL;
                    """.trimIndent()
                )
            }
        } else {
            logger.info {
                "${stream.id.originalNamespace}.${stream.id.originalName}: Skipping generation_id migration for final table. Final table exists: ${state.isFinalTablePresent}; final table schema is incorrect: ${state.isSchemaMismatch}"
            }
        }

        return Migration.MigrationResult(
            state.destinationState.copy(isGenerationIdPresent = true),
            invalidateInitialState = true
        )
    }
}
