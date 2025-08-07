/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.typing_deduping.legacy_raw_tables

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.QueryJobConfiguration
import com.google.cloud.bigquery.TableId
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.TableNames
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.FinalTableInitialStatus
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.RawTableInitialStatus
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingDatabaseInitialStatus

class BigqueryTypingDedupingDatabaseInitialStatusGatherer(private val bq: BigQuery) :
    DatabaseInitialStatusGatherer<TypingDedupingDatabaseInitialStatus> {
    private fun getInitialRawTableState(
        rawTableName: TableName,
        suffix: String
    ): RawTableInitialStatus? {
        bq.getTable(TableId.of(rawTableName.namespace, rawTableName.name + suffix))
        // Table doesn't exist. There are no unprocessed records, and no timestamp.
        ?: return null

        val rawTableIdQuoted = """`${rawTableName.namespace}`.`${rawTableName.name}$suffix`"""
        val unloadedRecordTimestamp =
            bq.query(
                    QueryJobConfiguration.of(
                        """
                            SELECT TIMESTAMP_SUB(MIN(_airbyte_extracted_at), INTERVAL 1 MICROSECOND)
                            FROM $rawTableIdQuoted
                            WHERE _airbyte_loaded_at IS NULL
                            """.trimIndent()
                    )
                )
                .iterateAll()
                .iterator()
                .next()
                .first()
        // If this value is null, then there are no records with null loaded_at.
        // If it's not null, then we can return immediately - we've found some unprocessed records
        // and their timestamp.
        if (!unloadedRecordTimestamp.isNull) {
            return RawTableInitialStatus(
                hasUnprocessedRecords = true,
                maxProcessedTimestamp = unloadedRecordTimestamp.timestampInstant,
            )
        }

        val loadedRecordTimestamp =
            bq.query(
                    QueryJobConfiguration.of(
                        """
                    SELECT MAX(_airbyte_extracted_at)
                    FROM $rawTableIdQuoted
                    """.trimIndent()
                    )
                )
                .iterateAll()
                .iterator()
                .next()
                .first()
        // We know (from the previous query) that all records have been processed by T+D already.
        // So we just need to get the timestamp of the most recent record.
        return if (loadedRecordTimestamp.isNull) {
            // Null timestamp because the table is empty. T+D can process the entire raw table
            // during this sync.
            RawTableInitialStatus(hasUnprocessedRecords = false, maxProcessedTimestamp = null)
        } else {
            // The raw table already has some records. T+D can skip all records with timestamp <=
            // this value.
            RawTableInitialStatus(
                hasUnprocessedRecords = false,
                maxProcessedTimestamp = loadedRecordTimestamp.timestampInstant
            )
        }
    }

    override suspend fun gatherInitialStatus(
        streams: TableCatalog,
    ): Map<DestinationStream, TypingDedupingDatabaseInitialStatus> {
        return streams.mapValues { (stream, names) ->
            val (tableNames, _) = names
            // we're never actually doing anything with the final table
            // so just return a hardcoded "safe" status
            val finalTableStatus =
                FinalTableInitialStatus(
                    isSchemaMismatch = false,
                    isEmpty = true,
                    finalTableGenerationId = stream.generationId,
                )
            val rawTableState = getInitialRawTableState(tableNames.rawTableName!!, "")
            val tempRawTableState =
                getInitialRawTableState(
                    tableNames.rawTableName!!,
                    TableNames.TMP_TABLE_SUFFIX,
                )
            TypingDedupingDatabaseInitialStatus(
                finalTableStatus,
                rawTableState,
                tempRawTableState,
            )
        }
    }
}
