/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.migrators

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.Field
import com.google.cloud.bigquery.Schema
import com.google.cloud.bigquery.StandardSQLTypeName
import com.google.cloud.bigquery.StandardTableDefinition
import com.google.cloud.bigquery.TableId
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.github.oshai.kotlinlogging.KotlinLogging

class BigqueryAirbyteMetaAndGenerationIdMigration(private val bigquery: BigQuery) :
    Migration<BigQueryDestinationState> {
    private val logger = KotlinLogging.logger {}

    override fun migrateIfNecessary(
        destinationHandler: DestinationHandler<BigQueryDestinationState>,
        stream: StreamConfig,
        state: DestinationInitialStatus<BigQueryDestinationState>
    ): Migration.MigrationResult<BigQueryDestinationState> {
        if (!state.initialRawTableStatus.rawTableExists) {
            // The raw table doesn't exist. No migration necessary. Update the state.
            logger.info {
                "Skipping airbyte_meta/generation_id migration for ${stream.id.originalNamespace}.${stream.id.originalName} because the raw table doesn't exist"
            }
            return Migration.MigrationResult(state.destinationState, false)
        }

        val rawTable = bigquery.getTable(TableId.of(stream.id.rawNamespace, stream.id.rawName))
        // if the schema is null, then we have bigger problems
        val rawFields = rawTable.getDefinition<StandardTableDefinition>().schema!!.fields
        val hasMeta = rawFields.any { it.name == JavaBaseConstants.COLUMN_NAME_AB_META }
        if (hasMeta) {
            // We've already executed the migration. Do nothing here.
            logger.info {
                "Skipping airbyte_meta/generation_id migration for ${stream.id.originalNamespace}.${stream.id.originalName} because the table already has the columns"
            }
            return Migration.MigrationResult(state.destinationState, false)
        }

        logger.info {
            "Executing airbyte_meta/generation_id migration for ${stream.id.originalNamespace}.${stream.id.originalName}"
        }

        // Define the new columns we're adding.
        // Add meta to the raw table
        val rawMetaField =
            Field.of(JavaBaseConstants.COLUMN_NAME_AB_META, StandardSQLTypeName.STRING)
        // And add generation ID to raw+final tables.
        val generationIdField =
            Field.of(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID, StandardSQLTypeName.INT64)

        // The way bigquery does an "alter table" is by just setting the entire table definition
        // (unless you want to write actual SQL, of course).
        // This adds the column as NULLABLE.
        val newRawTable =
            rawTable
                .toBuilder()
                .setDefinition(
                    StandardTableDefinition.of(
                        Schema.of(rawFields + rawMetaField + generationIdField)
                    )
                )
                .build()
        newRawTable.update()

        if (state.isFinalTablePresent) {
            val finalTable =
                bigquery.getTable(TableId.of(stream.id.finalNamespace, stream.id.finalName))
            val finalFields = finalTable.getDefinition<StandardTableDefinition>().schema!!.fields
            val airbyteMetaIndex =
                finalFields.indexOfFirst { it.name == JavaBaseConstants.COLUMN_NAME_AB_META }
            // Insert generation_id immediately after airbyte_meta
            val newFinalFields =
                finalFields.subList(0, airbyteMetaIndex + 1) +
                    generationIdField +
                    finalFields.subList(airbyteMetaIndex + 1, finalFields.size)
            val newFinalTable =
                finalTable
                    .toBuilder()
                    .setDefinition(StandardTableDefinition.of(Schema.of(newFinalFields)))
                    .build()
            newFinalTable.update()
        }

        // We need to refetch the initial state, because we modified the final table schema.
        return Migration.MigrationResult(state.destinationState, true)
    }
}
