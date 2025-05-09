/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.Field
import com.google.cloud.bigquery.QueryJobConfiguration
import com.google.cloud.bigquery.StandardSQLTypeName
import com.google.cloud.bigquery.StandardTableDefinition
import com.google.cloud.bigquery.TableDefinition
import com.google.cloud.bigquery.TimePartitioning
import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.Overwrite
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableNativeOperations
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.AlterTableReport
import io.airbyte.cdk.util.CollectionUtils.containsAllIgnoreCase
import io.airbyte.cdk.util.CollectionUtils.containsIgnoreCase
import io.airbyte.cdk.util.CollectionUtils.matchingKey
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.stream.Collectors
import java.util.stream.Stream

private val logger = KotlinLogging.logger {}

class BigqueryDirectLoadNativeTableOperations(private val bigquery: BigQuery) :
    DirectLoadTableNativeOperations {
    override fun ensureSchemaMatches(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping
    ) {
        //        TODO("Not yet implemented")
    }

    override fun getGenerationId(tableName: TableName): Long {
        val result =
            bigquery.query(
                QueryJobConfiguration.of(
                    "SELECT _airbyte_generation_id FROM ${tableName.namespace}.${tableName.name}$ LIMIT 1"
                ),
            )
        val value = result.iterateAll().first().get(Meta.COLUMN_NAME_AB_GENERATION_ID)
        return if (value.isNull) {
            0
        } else {
            value.longValue
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
            (stream.schema as ObjectType).properties.entries.associate {
                columnNameMapping[it.key]!! to
                    BigqueryDirectLoadSqlGenerator.toDialectType(it.value.type)
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

    // TODO this stuff will be useful for ensureSchemaMatches, maybe
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
                    BigqueryDirectLoadSqlGenerator.clusteringColumns(stream, columnNameMapping)
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
            }
        }
    }
}
