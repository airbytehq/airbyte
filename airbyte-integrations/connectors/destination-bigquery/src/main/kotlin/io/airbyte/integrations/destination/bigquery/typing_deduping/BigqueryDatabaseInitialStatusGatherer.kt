/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.Field
import com.google.cloud.bigquery.QueryJobConfiguration
import com.google.cloud.bigquery.StandardSQLTypeName
import com.google.cloud.bigquery.StandardTableDefinition
import com.google.cloud.bigquery.TableDefinition
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.TimePartitioning
import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.Overwrite
import io.airbyte.cdk.load.command.SoftDelete
import io.airbyte.cdk.load.command.Update
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.TableNames
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.AlterTableReport
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.FinalTableInitialStatus
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.RawTableInitialStatus
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingDatabaseInitialStatus
import io.airbyte.cdk.util.CollectionUtils.containsAllIgnoreCase
import io.airbyte.cdk.util.CollectionUtils.containsIgnoreCase
import io.airbyte.cdk.util.CollectionUtils.matchingKey
import io.github.oshai.kotlinlogging.KotlinLogging
import java.math.BigInteger
import java.util.stream.Collectors
import java.util.stream.Stream

private val logger = KotlinLogging.logger {}

class BigqueryDatabaseInitialStatusGatherer(private val bq: BigQuery) :
    DatabaseInitialStatusGatherer<TypingDedupingDatabaseInitialStatus> {
    private fun findExistingTable(finalTableName: TableName): TableDefinition? {
        val table = bq.getTable(finalTableName.namespace, finalTableName.name)
        return table?.getDefinition()
    }

    private fun isFinalTableEmpty(finalTableName: TableName): Boolean {
        return BigInteger.ZERO ==
            bq.getTable(TableId.of(finalTableName.namespace, finalTableName.name)).numRows
    }

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
            val (tableNames, columnNameMapping) = names
            val finalTable = findExistingTable(tableNames.finalTableName!!)
            val finalTableStatus =
                finalTable?.let {
                    FinalTableInitialStatus(
                        isSchemaMismatch =
                            !existingSchemaMatchesStreamConfig(
                                stream,
                                columnNameMapping,
                                finalTable
                            ),
                        isEmpty = isFinalTableEmpty(tableNames.finalTableName!!),
                        // for now, just use 0. this means we will always use a temp final table.
                        // platform has a workaround for this, so it's OK.
                        // TODO only fetch this on truncate syncs
                        // TODO once we have destination state, use that instead of a query
                        finalTableGenerationId = 0,
                    )
                }
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

    private fun existingSchemaMatchesStreamConfig(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        existingTable: TableDefinition
    ): Boolean {
        val alterTableReport = buildAlterTableReport(stream, columnNameMapping, existingTable)
        var tableClusteringMatches = false
        var tablePartitioningMatches = false
        if (existingTable is StandardTableDefinition) {
            tableClusteringMatches = clusteringMatches(stream, columnNameMapping, existingTable)
            tablePartitioningMatches = partitioningMatches(existingTable)
        }
        logger.info {
            "Alter Table Report ${alterTableReport.columnsToAdd} ${alterTableReport.columnsToRemove} ${alterTableReport.columnsToChangeType}; Clustering $tableClusteringMatches; Partitioning $tablePartitioningMatches"
        }

        return alterTableReport.isNoOp && tableClusteringMatches && tablePartitioningMatches
    }

    internal fun buildAlterTableReport(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        existingTable: TableDefinition,
    ): AlterTableReport {
        val pks = getPks(stream, columnNameMapping)

        val streamSchema: Map<String, StandardSQLTypeName> =
            stream.schema.asColumns().entries.associate {
                columnNameMapping[it.key]!! to BigQuerySqlGenerator.toDialectType(it.value.type)
            }

        val existingSchema =
            existingTable.schema!!.fields.associate { it.name to it.type.standardType }

        // Columns in the StreamConfig that don't exist in the TableDefinition
        val columnsToAdd =
            streamSchema.keys
                .stream()
                .filter { name: String -> !containsIgnoreCase(existingSchema.keys, name) }
                .collect(Collectors.toSet())

        // Columns in the current schema that are no longer in the StreamConfig
        val columnsToRemove =
            existingSchema.keys
                .stream()
                .filter { name: String ->
                    !containsIgnoreCase(streamSchema.keys, name) &&
                        !containsIgnoreCase(Meta.COLUMN_NAMES, name)
                }
                .collect(Collectors.toSet())

        // Columns that are typed differently than the StreamConfig
        val columnsToChangeType =
            Stream.concat(
                    streamSchema.keys
                        .stream() // If it's not in the existing schema, it should already be in the
                        // columnsToAdd Set
                        .filter { name: String ->
                            matchingKey(
                                    existingSchema.keys,
                                    name
                                ) // if it does exist, only include it in this set if the type (the
                                // value in each respective map)
                                // is different between the stream and existing schemas
                                .map { key: String ->
                                    existingSchema[key] != streamSchema[name]
                                } // if there is no matching key, then don't include it because it
                                // is probably already in columnsToAdd
                                .orElse(false)
                        }, // OR columns that used to have a non-null constraint and shouldn't
                    // (https://github.com/airbytehq/airbyte/pull/31082)

                    existingTable.schema!!
                        .fields
                        .stream()
                        .filter { pks.contains(it.name) && it.mode == Field.Mode.REQUIRED }
                        .map { obj: Field -> obj.name }
                )
                .collect(Collectors.toSet())

        return AlterTableReport(
            columnsToAdd,
            columnsToRemove,
            columnsToChangeType,
        )
    }

    companion object {
        @VisibleForTesting
        fun clusteringMatches(
            stream: DestinationStream,
            columnNameMapping: ColumnNameMapping,
            existingTable: StandardTableDefinition,
        ): Boolean {
            return (existingTable.clustering != null &&
                containsAllIgnoreCase(
                    HashSet<String>(existingTable.clustering!!.fields),
                    BigQuerySqlGenerator.clusteringColumns(stream, columnNameMapping)
                ))
        }

        @VisibleForTesting
        fun partitioningMatches(existingTable: StandardTableDefinition): Boolean {
            return existingTable.timePartitioning != null &&
                existingTable.timePartitioning!!
                    .field
                    .equals("_airbyte_extracted_at", ignoreCase = true) &&
                TimePartitioning.Type.DAY == existingTable.timePartitioning!!.type
        }

        private fun getPks(
            stream: DestinationStream,
            columnNameMapping: ColumnNameMapping
        ): Set<String> {
            return when (stream.importType) {
                Append,
                Overwrite -> emptySet()
                is Dedupe ->
                    (stream.importType as Dedupe)
                        .primaryKey
                        .map { pk -> columnNameMapping[pk.first()]!! }
                        .toSet()
                SoftDelete,
                Update -> throw ConfigErrorException("Unsupported sync mode: ${stream.importType}")
            }
        }
    }
}
