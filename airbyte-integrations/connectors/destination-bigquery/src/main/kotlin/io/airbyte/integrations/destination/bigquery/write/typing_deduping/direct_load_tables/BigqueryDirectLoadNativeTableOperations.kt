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
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.Sql
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
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
import kotlinx.coroutines.runBlocking
import org.apache.commons.codec.digest.DigestUtils

private val logger = KotlinLogging.logger {}

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", "kotlin coroutines")
class BigqueryDirectLoadNativeTableOperations(
    private val bigquery: BigQuery,
    private val sqlOperations: BigqueryDirectLoadSqlTableOperations,
    private val databaseHandler: BigQueryDatabaseHandler,
    private val projectId: String,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : DirectLoadTableNativeOperations {
    override suspend fun ensureSchemaMatches(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
    ) {
        val existingTable =
            bigquery.getTable(tableName.toTableId()).getDefinition<TableDefinition>()
        val shouldRecreateTable = shouldRecreateTable(stream, columnNameMapping, existingTable)
        val alterTableReport = buildAlterTableReport(stream, columnNameMapping, existingTable)
        logger.info {
            "Stream ${stream.mappedDescriptor.toPrettyString()} had alter table report $alterTableReport"
        }
        try {
            if (shouldRecreateTable) {
                logger.info {
                    "Stream ${stream.mappedDescriptor.toPrettyString()} detected change in partitioning/clustering config. Recreating the table."
                }
                recreateTable(
                    stream,
                    columnNameMapping,
                    tableName,
                    alterTableReport.columnsToRetain,
                    alterTableReport.columnsToChangeType,
                )
            } else if (!alterTableReport.isNoOp) {
                logger.info {
                    "Stream ${stream.mappedDescriptor.toPrettyString()} detected schema change. Altering the table."
                }
                runBlocking {
                    alterTable(
                        tableName,
                        columnsToAdd = alterTableReport.columnsToAdd,
                        columnsToRemove = alterTableReport.columnsToRemove,
                        columnsToChange = alterTableReport.columnsToChangeType,
                    )
                }
            } else {
                logger.info {
                    "Stream ${stream.mappedDescriptor.toPrettyString()} has correct schema; no action needed."
                }
            }
        } catch (e: Exception) {
            logger.error(e) {
                "Encountered an error while modifying the schema for stream ${stream.mappedDescriptor.toPrettyString()}. If this error persists, you may need to manually modify the table's schema."
            }
            throw e
        }
    }

    override suspend fun getGenerationId(tableName: TableName): Long {
        val result =
            bigquery.query(
                QueryJobConfiguration.of(
                    "SELECT _airbyte_generation_id FROM `${tableName.namespace}`.`${tableName.name}` LIMIT 1",
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
        if (originalType == StandardSQLTypeName.JSON) {
            // somewhat annoying.
            // TO_JSON_STRING returns string values with double quotes, which is not what we want
            // (i.e. we should unwrap the strings).
            // but JSON_VALUE doesn't handle non-scalar values.
            // so we have to handle both cases explicitly.
            // there's technically some cases where this doesn't round-trip, e.g.
            // JSON'"{\"foo\": 42}"' -> '{"foo":42}' -> JSON'{"foo": 42}'
            // but that seems like a weird enough situation that we shouldn't worry about it.
            return """
                CAST(
                  CASE JSON_TYPE($columnName)
                    WHEN 'object' THEN TO_JSON_STRING($columnName)
                    WHEN 'array' THEN TO_JSON_STRING($columnName)
                    ELSE JSON_VALUE($columnName)
                  END
                  AS $newType
                )
                """.trimIndent()
        } else if (newType == StandardSQLTypeName.JSON) {
            return "TO_JSON($columnName)"
        } else {
            return "CAST($columnName AS $newType)"
        }
    }

    /**
     * roughly:
     * 1. create a temp table
     * 2. copy the existing data into it (casting columns as needed)
     * 3. replace the real table with the temp table
     */
    private suspend fun recreateTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        tableName: TableName,
        columnsToRetain: List<String>,
        columnsToChange: List<ColumnChange<StandardSQLTypeName>>,
    ) {
        // can't just use the base temp table directly, since that could conflict with
        // a truncate-refresh temp table.
        // so add an explicit suffix that this is for schema change.
        val tempTableName =
            tempTableNameGenerator.generate(tableName).let {
                it.copy(name = it.name + "_airbyte_tmp_schema_change")
            }

        val originalTableId = "`$projectId`.`${tableName.namespace}`.`${tableName.name}`"
        val tempTableId = "`$projectId`.`${tempTableName.namespace}`.`${tempTableName.name}`"
        val columnList =
            (columnsToRetain + columnsToChange.map { it.name }).joinToString(",") { "`$it`" }
        val valueList =
            (columnsToRetain.map { "`$it`" } +
                    columnsToChange.map {
                        getColumnCastStatement(
                            columnName = it.name,
                            originalType = it.originalType,
                            newType = it.newType,
                        )
                    })
                .joinToString(",")
        // note: we don't care about columnsToDrop (because they don't exist in the tempTable)
        // and we don't care about columnsToAdd (because they'll just default to null)
        val insertToTempTable =
            Sql.of(
                """
                INSERT INTO $tempTableId
                ($columnList)
                SELECT
                $valueList
                FROM $originalTableId
                """.trimIndent(),
            )

        logger.info {
            "Stream ${stream.mappedDescriptor.toPrettyString()} using temporary table ${tempTableName.toPrettyString()} to recreate table ${tableName.toPrettyString()}."
        }
        sqlOperations.createTable(
            stream,
            tempTableName,
            columnNameMapping,
            replace = true,
        )
        databaseHandler.execute(insertToTempTable)
        sqlOperations.overwriteTable(tempTableName, tableName)
    }

    private suspend fun alterTable(
        tableName: TableName,
        columnsToAdd: List<ColumnAdd<StandardSQLTypeName>>,
        columnsToRemove: List<String>,
        columnsToChange: List<ColumnChange<StandardSQLTypeName>>,
    ) {
        // the bigquery API only supports adding new fields; you can't drop/rename existing fields.
        // so we'll do everything via DDL.
        // We also try to batch operations into a single statement, because bigquery enforces
        // somewhat low rate limits on how many ALTER TABLE operations you can run in a short
        // timeframe.
        val tableId = """`$projectId`.`${tableName.namespace}`.`${tableName.name}`"""

        // bigquery has strict limits on what types can be altered to other types.
        // so instead, we actually add a new column, explicitly cast the old column
        // into the new column, then swap the new column into the old column.
        // this struct contains everything we need to do that.
        // we also need a backup column for safety - see usage of backupColumnName.
        data class ColumnTypeChangePlan(
            val realColumnName: String,
            val tempColumnName: String,
            val backupColumnName: String,
            val originalType: StandardSQLTypeName,
            val newType: StandardSQLTypeName,
        )
        val typeChangePlans: List<ColumnTypeChangePlan> =
            columnsToChange.map { (name, originalType, newType) ->
                // prefix with letter in case the SHA256 starts with a number
                val nameHash = "a" + DigestUtils.sha256Hex(name)
                val tempColumnName = "${nameHash}_airbyte_tmp"
                val backupColumnName = "${nameHash}_airbyte_tmp_to_drop"
                ColumnTypeChangePlan(
                    realColumnName = name,
                    tempColumnName = tempColumnName,
                    backupColumnName = backupColumnName,
                    originalType = originalType,
                    newType = newType,
                )
            }

        // we do two alters initially.
        // the first does the basic alters (drop+add columns).
        // the second alter sets up the _changed_ columns' temp columns.
        // We do this because the temp columns may have been left over from the previous sync
        // (if the schema change failed).
        // And you can't just `alter table drop column foo, add column foo` - those have to be
        // in separate statements.
        val initialAlterations =
            columnsToRemove.map { name -> """DROP COLUMN `$name`""" } +
                columnsToAdd.map { (name, type) -> """ADD COLUMN `$name` $type""" }
        val addTempColumns =
            typeChangePlans.map { plan ->
                """ADD COLUMN `${plan.tempColumnName}` ${plan.newType}"""
            }
        // Need to add explicit checks on both branches.
        // If we have no added/dropped columns, we will skip the first alter table.
        // If we have no changed columns, we will skip the second alter.
        if (initialAlterations.isNotEmpty()) {
            databaseHandler.executeWithRetries(
                """ALTER TABLE $tableId ${initialAlterations.joinToString(",")}"""
            )
        }
        if (addTempColumns.isNotEmpty()) {
            databaseHandler.executeWithRetries(
                """ALTER TABLE $tableId ${addTempColumns.joinToString(",")}"""
            )
        }

        // now we execute the rest of the table alterations.
        // these happen on a per-column basis, so that a failed UPDATE statement in one column
        // doesn't block other schema changes from happening.
        typeChangePlans.forEach {
            (realColumnName, tempColumnName, backupColumnName, originalType, newType) ->
            // first, update the temp column to contain the casted value.
            val castStatement = getColumnCastStatement(realColumnName, originalType, newType)
            try {
                databaseHandler.executeWithRetries(
                    """UPDATE $tableId SET `$tempColumnName` = $castStatement WHERE 1=1"""
                )
            } catch (e: Exception) {
                val message =
                    "Error while updating schema for table ${tableName.toPrettyString()} (attempting to change column $realColumnName from $originalType to $newType). You should manually update the schema for this table, or refresh the stream and remove existing records. Details: ${e.message}"
                logger.warn(e) { message }
                // no rollback logic. On the next sync, we'll see the temp columns in columnsToDrop.
                throw ConfigErrorException(message, e)
            }

            // then, swap the temp column to replace the original column.
            // this is surprisingly nontrivial.
            // bigquery doesn't support DDL in transactions,
            // and also doesn't support having RENAME COLUMN and DROP COLUMN in the same
            // ALTER TABLE statement.
            // so this gives us the safest way to drop the old column:
            // we atomically rename the old column to a holding location
            // and rename the new column to replace it.
            // Then, in a second ALTER TABLE, we drop the old column.
            // this means that there's never a time when the table is completely missing
            // the actual column.
            // If we crash immediately after the RENAME COLUMNs, everything is fine:
            // the next sync will see $backupColumnName as a column to drop,
            // and we'll recover naturally.
            databaseHandler.executeWithRetries(
                """
                ALTER TABLE $tableId
                  RENAME COLUMN `$realColumnName` TO $backupColumnName,
                  RENAME COLUMN `$tempColumnName` TO $realColumnName
                """.trimIndent(),
            )
            databaseHandler.executeWithRetries(
                """ALTER TABLE $tableId DROP COLUMN $backupColumnName""",
            )
        }
    }

    companion object {
        @VisibleForTesting
        fun clusteringMatches(
            stream: DestinationStream,
            columnNameMapping: ColumnNameMapping,
            existingTable: StandardTableDefinition,
        ): Boolean {
            // We always want to set a clustering config, so if the table doesn't have one,
            // then we should fix it.
            if (existingTable.clustering == null) {
                return false
            }

            val existingClusteringFields = HashSet<String>(existingTable.clustering!!.fields)
            // We're OK with a column being in the clustering config that we don't expect
            // (e.g. user set a composite PK, then makes one of those fields no longer a PK).
            // It doesn't really hurt us to have that extra clustering config.
            val clusteringConfigIsSupersetOfExpectedConfig =
                containsAllIgnoreCase(
                    existingClusteringFields,
                    BigqueryDirectLoadSqlGenerator.clusteringColumns(stream, columnNameMapping),
                )
            // We do, however, validate that all the clustering fields actually exist in the
            // intended schema.
            // This is so that we don't try to drop columns that bigquery is clustering against
            // (because bigquery throws an error in that case).
            val clusteringConfigReferencesExistingFields =
                containsAllIgnoreCase(
                    columnNameMapping.values + Meta.COLUMN_NAMES,
                    existingClusteringFields,
                )
            return clusteringConfigIsSupersetOfExpectedConfig &&
                clusteringConfigReferencesExistingFields
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
