/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables

import com.google.cloud.bigquery.StandardSQLTypeName
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.orchestration.db.CDC_DELETED_AT_COLUMN
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.Sql
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadSqlGenerator
import java.util.ArrayList
import java.util.stream.Collectors
import org.apache.commons.lang3.StringUtils

class BigqueryDirectLoadSqlGenerator(private val projectId: String?) : DirectLoadSqlGenerator {
    override fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean,
    ): Sql {
        fun columnsAndTypes(
            stream: DestinationStream,
            columnNameMapping: ColumnNameMapping
        ): String =
            stream.schema
                .asColumns()
                .map { (fieldName, type) ->
                    val columnName = columnNameMapping[fieldName]!!
                    val typeName = toDialectType(type.type).name
                    "`$columnName` $typeName"
                }
                .joinToString(",\n")

        val columnDeclarations = columnsAndTypes(stream, columnNameMapping)
        val clusterConfig =
            clusteringColumns(stream, columnNameMapping)
                .stream()
                .map { c: String? -> StringUtils.wrap(c, QUOTE) }
                .collect(Collectors.joining(", "))
        val forceCreateTable = if (replace) "OR REPLACE" else ""
        val finalTableId = tableName.toPrettyString(QUOTE)
        return Sql.of(
            """
            CREATE $forceCreateTable TABLE `$projectId`.$finalTableId (
              _airbyte_raw_id STRING NOT NULL,
              _airbyte_extracted_at TIMESTAMP NOT NULL,
              _airbyte_meta JSON NOT NULL,
              _airbyte_generation_id INTEGER,
              $columnDeclarations
            )
            PARTITION BY (DATE_TRUNC(_airbyte_extracted_at, DAY))
            CLUSTER BY $clusterConfig;
            """.trimIndent()
        )
    }

    override fun overwriteTable(sourceTableName: TableName, targetTableName: TableName): Sql {
        val targetTableId = targetTableName.toPrettyString(QUOTE)
        val sourceTableId = sourceTableName.toPrettyString(QUOTE)
        return Sql.separately(
            "DROP TABLE IF EXISTS `$projectId`.$targetTableId;",
            "ALTER TABLE `$projectId`.$sourceTableId RENAME TO `${targetTableName.name}`;"
        )
    }

    override fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): Sql {
        val columnNames = columnNameMapping.map { (_, actualName) -> actualName }
        return Sql.of(
            """
            INSERT INTO `${targetTableName.namespace}`.`${targetTableName.name}`
            $columnNames
            SELECT $columnNames FROM `${sourceTableName.namespace}`.`${sourceTableName.name}`
            """.trimIndent()
        )
    }

    override fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): Sql {

        val importType = stream.importType as Dedupe
        val pkEquivalent =
            importType.primaryKey.joinToString(" AND ") { fieldPath ->
                val fieldName = fieldPath.first()
                val columnName = columnNameMapping[fieldName]!!
                """(target_table.`$columnName` = new_record.`$columnName` OR (target_table.`$columnName` IS NULL AND new_record.`$columnName` IS NULL))"""
            }

        val columnList: String =
            stream.schema.asColumns().keys.joinToString("\n") { fieldName ->
                val columnName = columnNameMapping[fieldName]!!
                "`$columnName`,"
            }
        val newRecordColumnList: String =
            stream.schema.asColumns().keys.joinToString("\n") { fieldName ->
                val columnName = columnNameMapping[fieldName]!!
                "new_record.`$columnName`,"
            }
        val selectSourceRecords = selectDedupedRecords(stream, sourceTableName, columnNameMapping)

        val cursorComparison: String
        if (importType.cursor.isNotEmpty()) {
            val cursorFieldName = importType.cursor.first()
            val cursorColumnName = columnNameMapping[cursorFieldName]!!
            val cursor = "`$cursorColumnName`"
            // Build a condition for "new_record is more recent than target_table":
            cursorComparison = // First, compare the cursors.
            ("""
             (
               target_table.$cursor < new_record.$cursor
               OR (target_table.$cursor = new_record.$cursor AND target_table._airbyte_extracted_at < new_record._airbyte_extracted_at)
               OR (target_table.$cursor IS NULL AND new_record.$cursor IS NULL AND target_table._airbyte_extracted_at < new_record._airbyte_extracted_at)
               OR (target_table.$cursor IS NULL AND new_record.$cursor IS NOT NULL)
             )
             """.trimIndent())
        } else {
            // If there's no cursor, then we just take the most-recently-emitted record
            cursorComparison =
                "target_table._airbyte_extracted_at < new_record._airbyte_extracted_at"
        }

        val cdcDeleteClause: String
        val cdcSkipInsertClause: String
        if (stream.schema.asColumns().containsKey(CDC_DELETED_AT_COLUMN)) {
            // Execute CDC deletions if there's already a record
            cdcDeleteClause =
                "WHEN MATCHED AND new_record._ab_cdc_deleted_at IS NOT NULL AND $cursorComparison THEN DELETE"
            // And skip insertion entirely if there's no matching record.
            // (This is possible if a single T+D batch contains both an insertion and deletion for
            // the same PK)
            cdcSkipInsertClause = "AND new_record._ab_cdc_deleted_at IS NULL"
        } else {
            cdcDeleteClause = ""
            cdcSkipInsertClause = ""
        }

        val columnAssignments: String =
            stream.schema.asColumns().keys.joinToString("\n") { fieldName ->
                val column = columnNameMapping[fieldName]!!
                "`$column` = new_record.`$column`,"
            }
        val targetTableId = targetTableName.toPrettyString(QUOTE)

        return Sql.of(
            """
               MERGE `$projectId`.$targetTableId target_table
               USING (
                 $selectSourceRecords
               ) new_record
               ON $pkEquivalent
               $cdcDeleteClause
               WHEN MATCHED AND $cursorComparison THEN UPDATE SET
                 $columnAssignments
                 _airbyte_meta = new_record._airbyte_meta,
                 _airbyte_raw_id = new_record._airbyte_raw_id,
                 _airbyte_extracted_at = new_record._airbyte_extracted_at,
                 _airbyte_generation_id = new_record._airbyte_generation_id
               WHEN NOT MATCHED $cdcSkipInsertClause THEN INSERT (
                 $columnList
                 _airbyte_meta,
                 _airbyte_raw_id,
                 _airbyte_extracted_at,
                 _airbyte_generation_id
               ) VALUES (
                 $newRecordColumnList
                 new_record._airbyte_meta,
                 new_record._airbyte_raw_id,
                 new_record._airbyte_extracted_at,
                 new_record._airbyte_generation_id
               );
               """.trimIndent()
        )
    }

    override fun dropTable(tableName: TableName): Sql {
        val tableId = tableName.toPrettyString(QUOTE)
        return Sql.of("""DROP TABLE IF EXISTS `$projectId`.$tableId;""")
    }

    /**
     * A SQL SELECT statement that extracts records from the table and dedupes the records (since we
     * only need the most-recent record to upsert).
     */
    private fun selectDedupedRecords(
        stream: DestinationStream,
        sourceTableName: TableName,
        columnNameMapping: ColumnNameMapping,
    ): String {
        val columnList: String =
            stream.schema.asColumns().keys.joinToString("\n") { fieldName ->
                val columnName = columnNameMapping[fieldName]!!
                "`$columnName`,"
            }

        val importType = stream.importType as Dedupe

        // We need to dedup the records. Note the row_number() invocation in
        // the SQL statement. We only take the most-recent raw record for each PK.
        val pkList =
            importType.primaryKey.joinToString(",") { fieldName ->
                val columnName = columnNameMapping[fieldName.first()]!!
                "`$columnName`"
            }
        val cursorOrderClause =
            if (importType.cursor.isEmpty()) {
                ""
            } else if (importType.cursor.size == 1) {
                val columnName = importType.cursor.first()
                "`$columnName` DESC NULLS LAST"
            } else {
                throw UnsupportedOperationException(
                    "Only top-level cursors are supported, got ${importType.cursor}"
                )
            }

        return """
               WITH records AS (
                 SELECT
                   $columnList
                   _airbyte_meta,
                   _airbyte_raw_id,
                   _airbyte_extracted_at,
                   _airbyte_generation_id
                 FROM `$projectId`.${sourceTableName.toPrettyString(QUOTE)}
               ), numbered_rows AS (
                 SELECT *, row_number() OVER (
                   PARTITION BY $pkList ORDER BY $cursorOrderClause `_airbyte_extracted_at` DESC
                 ) AS row_number
                 FROM records
               )
               SELECT $columnList _airbyte_meta, _airbyte_raw_id, _airbyte_extracted_at, _airbyte_generation_id
               FROM numbered_rows
               WHERE row_number = 1
               """.trimIndent()
    }

    companion object {
        const val QUOTE: String = "`"

        fun toDialectType(type: AirbyteType): StandardSQLTypeName =
            when (type) {
                BooleanType -> StandardSQLTypeName.BOOL
                DateType -> StandardSQLTypeName.DATE
                IntegerType -> StandardSQLTypeName.INT64
                NumberType -> StandardSQLTypeName.NUMERIC
                StringType -> StandardSQLTypeName.STRING
                TimeTypeWithTimezone -> StandardSQLTypeName.STRING
                TimeTypeWithoutTimezone -> StandardSQLTypeName.TIME
                TimestampTypeWithTimezone -> StandardSQLTypeName.TIMESTAMP
                TimestampTypeWithoutTimezone -> StandardSQLTypeName.DATETIME
                is ArrayType,
                ArrayTypeWithoutSchema,
                is ObjectType,
                ObjectTypeWithEmptySchema,
                ObjectTypeWithoutSchema -> StandardSQLTypeName.JSON
                is UnionType ->
                    if (type.isLegacyUnion) {
                        toDialectType(type.chooseType())
                    } else {
                        StandardSQLTypeName.JSON
                    }
                is UnknownType -> StandardSQLTypeName.JSON
            }

        fun clusteringColumns(
            stream: DestinationStream,
            columnNameMapping: ColumnNameMapping
        ): List<String> {
            val clusterColumns: MutableList<String> = ArrayList()
            if (stream.importType is Dedupe) {
                // We're doing de-duping, therefore we have a primary key.
                // Cluster on the first 3 PK columns since BigQuery only allows up to 4 clustering
                // columns,
                // and we're always clustering on _airbyte_extracted_at
                (stream.importType as Dedupe).primaryKey.stream().limit(3).forEach {
                    pk: List<String> ->
                    clusterColumns.add(columnNameMapping[pk.first()]!!)
                }
            }
            clusterColumns.add("_airbyte_extracted_at")
            return clusterColumns
        }
    }
}
