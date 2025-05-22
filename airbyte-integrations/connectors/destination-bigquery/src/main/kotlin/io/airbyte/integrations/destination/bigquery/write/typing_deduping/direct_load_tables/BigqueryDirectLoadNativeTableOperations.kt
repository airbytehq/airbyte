/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.QueryJobConfiguration
import com.google.cloud.bigquery.StandardSQLTypeName
import com.google.cloud.bigquery.StandardTableDefinition
import com.google.cloud.bigquery.TableDefinition
import com.google.cloud.bigquery.TimePartitioning
import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.Sql
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.AlterTableReport
import io.airbyte.cdk.load.orchestration.db.direct_load_table.ColumnAdd
import io.airbyte.cdk.load.orchestration.db.direct_load_table.ColumnChange
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableNativeOperations
import io.airbyte.cdk.util.CollectionUtils.containsAllIgnoreCase
import io.airbyte.cdk.util.containsIgnoreCase
import io.airbyte.cdk.util.findIgnoreCase
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.BigQueryDatabaseHandler
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.toTableId
import io.github.oshai.kotlinlogging.KotlinLogging
import org.apache.commons.codec.digest.DigestUtils

private val logger = KotlinLogging.logger {}

class BigqueryDirectLoadNativeTableOperations(
    private val bigquery: BigQuery,
    private val databaseHandler: BigQueryDatabaseHandler,
    private val projectId: String,
) : DirectLoadTableNativeOperations {
    override fun ensureSchemaMatches(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping
    ) {
        val existingTable =
            bigquery.getTable(tableName.toTableId()).getDefinition<TableDefinition>()
        val shouldRecreateTable = shouldRecreateTable(stream, columnNameMapping, existingTable)
        val alterTableReport = buildAlterTableReport(stream, columnNameMapping, existingTable)
        logger.info {
            "Stream ${stream.descriptor.toPrettyString()} had alter table report $alterTableReport"
        }
        if (shouldRecreateTable) {
            // roughly:
            // 1. create a temp table
            // 2. copy the existing data into it (casting columns as needed)
            // 3. replace the real table with the temp table
            TODO()
        } else {
            databaseHandler.execute(
                getAlterTableSql(
                    projectId = projectId,
                    tableName,
                    columnsToAdd = alterTableReport.columnsToAdd,
                    columnsToRemove = alterTableReport.columnsToRemove,
                    columnsToChange = alterTableReport.columnsToChangeType,
                )
            )
        }
    }

    override fun getGenerationId(tableName: TableName): Long {
        val result =
            bigquery.query(
                QueryJobConfiguration.of(
                    "SELECT _airbyte_generation_id FROM ${tableName.namespace}.${tableName.name} LIMIT 1"
                ),
            )
        val value = result.iterateAll().first().get(Meta.COLUMN_NAME_AB_GENERATION_ID)
        return if (value.isNull) {
            0
        } else {
            value.longValue
        }
    }

    /**
     * Bigquery doesn't support changing a table's partitioning / clustering scheme in-place. So
     * check whether we want to change those here.
     */
    private fun shouldRecreateTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        existingTable: TableDefinition
    ): Boolean {
        var tableClusteringMatches = false
        var tablePartitioningMatches = false
        if (existingTable is StandardTableDefinition) {
            tableClusteringMatches = clusteringMatches(stream, columnNameMapping, existingTable)
            tablePartitioningMatches = partitioningMatches(existingTable)
        }
        return !tableClusteringMatches || !tablePartitioningMatches
    }

    internal fun buildAlterTableReport(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        existingTable: TableDefinition,
    ): AlterTableReport<StandardSQLTypeName> {
        val expectedSchema: Map<String, StandardSQLTypeName> =
            stream.schema.asColumns().entries.associate {
                columnNameMapping[it.key]!! to
                    BigqueryDirectLoadSqlGenerator.toDialectType(it.value.type)
            }
        val actualSchema =
            existingTable.schema!!.fields.associate { it.name to it.type.standardType }

        // Columns in the StreamConfig that don't exist in the TableDefinition
        val columnsToAdd =
            expectedSchema
                .filter { (name, _) -> actualSchema.findIgnoreCase(name) == null }
                .map { (name, type) -> ColumnAdd(name, type) }
                .toList()

        // Columns in the current schema that are no longer in the DestinationStream
        val columnsToRemove =
            actualSchema.keys.filter { name ->
                !expectedSchema.keys.containsIgnoreCase(name) &&
                    !Meta.COLUMN_NAMES.containsIgnoreCase(name)
            }

        // Columns that are typed differently than the DestinationStream
        val columnsToChangeType =
            expectedSchema.mapNotNull { (expectedName, expectedType) ->
                actualSchema.findIgnoreCase(expectedName)?.let { actualType ->
                    if (actualType != expectedType) {
                        ColumnChange(
                            name = expectedName,
                            originalType = actualType,
                            newType = expectedType,
                        )
                    } else {
                        null
                    }
                }
            }

        val columnsToRetain =
            actualSchema.mapNotNull { (actualName, _) ->
                if (
                    !columnsToRemove.contains(actualName) &&
                        !columnsToChangeType.any { it.name.equals(actualName, ignoreCase = true) }
                ) {
                    actualName
                } else {
                    null
                }
            }

        return AlterTableReport(
            columnsToAdd = columnsToAdd,
            columnsToRemove = columnsToRemove,
            columnsToChangeType = columnsToChangeType,
            columnsToRetain = columnsToRetain,
        )
    }

    private fun getColumnCastStatement(
        columnName: String,
        originalType: StandardSQLTypeName,
        newType: StandardSQLTypeName,
    ): String {
        // probably something like this, except with special handling for JSON values.
        return "CAST($columnName AS $newType)"
    }

    private fun getAlterTableSql(
        projectId: String,
        tableName: TableName,
        columnsToAdd: List<ColumnAdd<StandardSQLTypeName>>,
        columnsToRemove: List<String>,
        columnsToChange: List<ColumnChange<StandardSQLTypeName>>,
    ): Sql {
        val tableId = """`$projectId`.`${tableName.namespace}`.`${tableName.name}`"""
        val addColumns =
            columnsToAdd.map { (name, type) -> """ALTER TABLE $tableId ADD COLUMN $name $type""" }
        val removeColumns =
            columnsToRemove.map { name -> """ALTER TABLE $tableId DROP COLUMN $name""" }
        val changeColumns =
            columnsToChange.flatMap { (name, originalType, newType) ->
                // prefix with underscore
                val nameHash = "_" + DigestUtils.sha256Hex(name)
                val tempColumnName = "${nameHash}_airbyte_tmp"
                val backupColumnName = "${nameHash}_airbyte_tmp_to_drop"
                val castStatement = getColumnCastStatement(name, originalType, newType)
                listOf(
                    // bigquery has strict limits on what types can be altered to other types.
                    // so instead, we actually add a new column, explicitly cast the old column
                    // into the new column, then swap the new column into the old column.
                    """ALTER TABLE $tableId ADD COLUMN $tempColumnName $newType""",
                    """UPDATE $tableId SET $tempColumnName = $castStatement WHERE 1=1""",
                    // bigquery doesn't support DDL in transactions,
                    // and also doesn't support having RENAME COLUMN and DROP COLUMN in the same
                    // ALTER TABLE statement.
                    // so this gives us the safest way to drop the old column:
                    // we atomically rename the old column to a holding location
                    // and rename the new column to replace it.
                    // (we'd prefer to just DROP the old column, but bigquery disallows that.)
                    // Then, in a second ALTER TABLE, we drop the old column.
                    // this means that there's never a time when the table is completely missing
                    // the actual column.
                    // If we crash immediately after the ALTER TABLE RENAME, everything is fine:
                    // the next sync will see $backupColumnName as a column to drop,
                    // and we'll recover naturally.
                    """
                    ALTER TABLE $tableId
                      RENAME COLUMN $name TO $backupColumnName,
                      RENAME COLUMN $tempColumnName TO $name
                    """.trimIndent(),
                    """ALTER TABLE $tableId DROP COLUMN $backupColumnName"""
                )
            }
        return Sql.separately(addColumns + removeColumns + changeColumns)
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
    }
}
