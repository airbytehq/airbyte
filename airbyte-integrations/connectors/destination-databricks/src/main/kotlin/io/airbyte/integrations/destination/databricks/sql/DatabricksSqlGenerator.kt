/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.sql

import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.integrations.destination.databricks.schema.DatabricksTableSchemaMapper.Companion.LONG
import io.airbyte.integrations.destination.databricks.schema.DatabricksTableSchemaMapper.Companion.STRING
import io.airbyte.integrations.destination.databricks.schema.DatabricksTableSchemaMapper.Companion.TIMESTAMP
import io.airbyte.integrations.destination.databricks.schema.DatabricksTableSchemaMapper.Companion.TIMESTAMP_NTZ
import io.airbyte.integrations.destination.databricks.spec.CdcDeletionMode
import io.airbyte.integrations.destination.databricks.spec.DatabricksConfiguration
import jakarta.inject.Singleton

@Singleton
class DatabricksSqlGenerator(
    private val config: DatabricksConfiguration,
) {

    fun createNamespace(namespace: String): String =
        "CREATE SCHEMA IF NOT EXISTS ${fullyQualifiedNamespace(namespace)}"

    fun namespaceExists(namespace: String): String =
        """
        |SELECT COUNT(*) > 0 AS schema_exists
        |FROM ${config.database.quote()}.information_schema.schemata
        |WHERE catalog_name = ${config.database.toSqlLiteral()}
        |AND schema_name = ${namespace.toSqlLiteral()}
        """.trimMargin()

    fun tableExists(tableName: TableName): String =
        """
        |SELECT COUNT(*) > 0 AS table_exists
        |FROM ${config.database.quote()}.information_schema.tables
        |WHERE table_catalog = ${config.database.toSqlLiteral()}
        |AND table_schema = ${tableName.namespace.toSqlLiteral()}
        |AND table_name = ${tableName.name.toSqlLiteral()}
        """.trimMargin()

    fun createTable(
        tableName: TableName,
        tableSchema: StreamTableSchema,
        replace: Boolean = false,
    ): String {
        val userColumns = tableSchema.columnSchema.finalSchema

        val columnDeclarations =
            buildList {
                    metaColumns.forEach { (columnName, columnType) ->
                        val nullability = if (columnType.nullable) "" else " NOT NULL"
                        add("${columnName.quote()} ${columnType.type}$nullability")
                    }
                    userColumns.forEach { (columnName, columnType) ->
                        val nullability = if (columnType.nullable) "" else " NOT NULL"
                        add("${columnName.quote()} ${columnType.type}$nullability")
                    }
                }
                .joinToString(",\n    ")

        val allColumnTypes = metaColumns.values + userColumns.values
        val tblProperties =
            if (allColumnTypes.any { it.type == TIMESTAMP_NTZ }) {
                " TBLPROPERTIES ('delta.feature.timestampNtz' = 'supported')"
            } else {
                ""
            }

        val createPrefix = if (replace) "CREATE OR REPLACE TABLE" else "CREATE TABLE IF NOT EXISTS"
        return "$createPrefix ${fullyQualifiedName(tableName)} ( $columnDeclarations)$tblProperties"
    }

    fun dropTable(tableName: TableName): String =
        "DROP TABLE IF EXISTS ${fullyQualifiedName(tableName)}"

    fun overwriteTable(sourceTableName: TableName, targetTableName: TableName): List<String> =
        listOf(
            "CREATE OR REPLACE TABLE ${fullyQualifiedName(targetTableName)} AS SELECT * FROM ${
                fullyQualifiedName(sourceTableName)
            }",
            dropTable(sourceTableName),
        )

    fun copyTable(
        columnNames: Set<String>,
        sourceTableName: TableName,
        targetTableName: TableName,
    ): String {
        val columnList = columnNames.joinToString(", ") { it.quote() }

        return """
            |INSERT INTO ${fullyQualifiedName(targetTableName)} ($columnList)
            |SELECT $columnList
            |FROM ${fullyQualifiedName(sourceTableName)}
        """.trimMargin()
    }

    fun upsertTable(
        tableSchema: StreamTableSchema,
        sourceTableName: TableName,
        targetTableName: TableName,
    ): String {
        val pks = tableSchema.getPrimaryKey().flatten()
        if (pks.isEmpty()) {
            throw IllegalArgumentException("Cannot perform upsert without primary key")
        }

        // Primary key matching
        val pkEquivalent =
            pks.joinToString(" AND ") { columnName ->
                "final.${columnName.quote()} = staging.${columnName.quote()}"
            }

        // Cursor comparison to determine which record is newer
        val cursor = tableSchema.getCursor().firstOrNull()
        val cursorComparison = buildCursorComparison(cursor)

        // Deduped source records
        val selectSource = selectDedupedRecords(tableSchema, sourceTableName)

        // CDC delete handling: only hard-delete when the column exists AND config is HARD_DELETE.
        // In soft-delete mode, the deletion record is upserted as-is (the _ab_cdc_deleted_at
        // column is preserved as a tombstone marker).
        val cdcHardDeleteEnabled =
            tableSchema.columnSchema.finalSchema.containsKey(CDC_DELETED_AT_COLUMN) &&
                config.cdcDeletionMode == CdcDeletionMode.HARD_DELETE

        val cdcDeleteClause =
            if (cdcHardDeleteEnabled) {
                "WHEN MATCHED AND staging.${CDC_DELETED_AT_COLUMN.quote()} IS NOT NULL THEN DELETE"
            } else {
                ""
            }

        val cdcSkipInsertClause =
            if (cdcHardDeleteEnabled) "AND staging.${CDC_DELETED_AT_COLUMN.quote()} IS NULL" else ""

        return """
            |MERGE INTO ${fullyQualifiedName(targetTableName)} AS final
            |USING ($selectSource) AS staging
            |ON $pkEquivalent
            |$cdcDeleteClause
            |WHEN MATCHED AND $cursorComparison THEN UPDATE SET *
            |WHEN NOT MATCHED $cdcSkipInsertClause THEN INSERT *
        """.trimMargin()
    }

    /** Returns a query that counts all rows in the table. */
    fun countTable(tableName: TableName): String =
        "SELECT COUNT(*) FROM ${fullyQualifiedName(tableName)}"

    /** Returns a query that fetches the generation ID from an arbitrary row. */
    fun getGenerationId(tableName: TableName): String =
        """
        |SELECT ${COLUMN_NAME_AB_GENERATION_ID.quote()}
        |FROM ${fullyQualifiedName(tableName)}
        |LIMIT 1
        """.trimMargin()

    /** Uses three-part filtering (catalog, schema, table) for Unity Catalog */
    fun getTableSchema(tableName: TableName): String =
        """
        |SELECT column_name, data_type, is_nullable
        |FROM ${config.database.quote()}.information_schema.columns
        |WHERE table_catalog = ${config.database.toSqlLiteral()}
        |AND table_schema = ${tableName.namespace.toSqlLiteral()}
        |AND table_name = ${tableName.name.toSqlLiteral()}
        |ORDER BY ordinal_position
        """.trimMargin()

    fun alterTable(
        tableName: TableName,
        changeset: ColumnChangeset,
    ): List<String> {
        val hasTypeChanges =
            changeset.columnsToChange.any { (_, typeChange) ->
                typeChange.originalType.type != typeChange.newType.type
            }

        if (hasTypeChanges) {
            return listOf(recreateTableWithCast(tableName, changeset))
        }

        // No type changes — use standard ADD COLUMN statements.
        val fqn = fullyQualifiedName(tableName)
        val statements = mutableListOf<String>()

        // Enable timestampNtz feature if any new column uses TIMESTAMP_NTZ
        if (changeset.columnsToAdd.values.any { it.type == TIMESTAMP_NTZ }) {
            statements.add(
                "ALTER TABLE $fqn SET TBLPROPERTIES ('delta.feature.timestampNtz' = 'supported')",
            )
        }

        changeset.columnsToAdd.forEach { (name, columnType) ->
            statements.add("ALTER TABLE $fqn ADD COLUMN ${name.quote()} ${columnType.type}")
        }

        return statements
    }

    /**
     * Rebuilds the table with type-cast columns using CREATE OR REPLACE TABLE ... AS SELECT. This
     * handles all changeset operations (add, drop, change) in a single atomic statement
     */
    private fun recreateTableWithCast(
        tableName: TableName,
        changeset: ColumnChangeset,
    ): String {
        val fqn = fullyQualifiedName(tableName)

        val selectColumns = buildList {
            // Meta columns — pass through as-is
            metaColumns.forEach { (name, _) -> add(name.quote()) }

            // Retained columns — pass through as-is
            changeset.columnsToRetain.forEach { (name, _) -> add(name.quote()) }

            // Changed columns — CAST to new type
            changeset.columnsToChange.forEach { (name, typeChange) ->
                if (typeChange.originalType.type != typeChange.newType.type) {
                    add("CAST(${name.quote()} AS ${typeChange.newType.type}) AS ${name.quote()}")
                } else {
                    add(name.quote())
                }
            }

            // Added columns — initialize with NULL of the correct type
            changeset.columnsToAdd.forEach { (name, columnType) ->
                add("CAST(NULL AS ${columnType.type}) AS ${name.quote()}")
            }

            // Previously-dropped columns — retained as-is
            changeset.columnsToDrop.forEach { (name, _) -> add(name.quote()) }
        }

        return "CREATE OR REPLACE TABLE $fqn AS SELECT ${selectColumns.joinToString(", ")} FROM $fqn"
    }

    // -- Staging Operations --

    /** Creates a Unity Catalog Volume for staging Avro files. */
    fun createStagingVolume(tableName: TableName): String =
        "CREATE VOLUME IF NOT EXISTS ${fullyQualifiedName(stagingVolumeName(tableName))}"

    /** load a staged Avro file from a Unity Catalog Volume into the target table */
    fun copyIntoFromVolume(
        tableName: TableName,
        stagedFilePath: String,
    ): String =
        """
        |COPY INTO ${fullyQualifiedName(tableName)}
        |FROM '$stagedFilePath'
        |FILEFORMAT = AVRO
        """.trimMargin()

    /** Returns a [TableName] for the staging volume associated with the given table. */
    internal fun stagingVolumeName(tableName: TableName): TableName =
        TableName(namespace = tableName.namespace, name = "${tableName.name}_staging")

    // -- Internal Helpers --

    /** Generates a SELECT query that deduplicates source records using ROW_NUMBER() */
    private fun selectDedupedRecords(
        tableSchema: StreamTableSchema,
        sourceTableName: TableName,
    ): String {
        val pks = tableSchema.getPrimaryKey().flatten()
        val pkList = pks.joinToString(", ") { it.quote() }

        val cursor = tableSchema.getCursor().firstOrNull()
        val cursorOrderClause =
            if (cursor != null) {
                "${cursor.quote()} DESC NULLS LAST,"
            } else {
                ""
            }

        return """
            |  SELECT *
            |  FROM (
            |    SELECT *,
            |      ROW_NUMBER() OVER (
            |        PARTITION BY $pkList
            |        ORDER BY $cursorOrderClause ${COLUMN_NAME_AB_EXTRACTED_AT.quote()} DESC
            |      ) AS row_number
            |    FROM ${fullyQualifiedName(sourceTableName)}
            |  ) AS deduplicated
            |  WHERE row_number = 1
        """.trimMargin()
    }

    /** Builds a SQL comparison to determine if the source record is newer than the target */
    private fun buildCursorComparison(cursor: String?): String {
        val extractedAt = COLUMN_NAME_AB_EXTRACTED_AT.quote()
        if (cursor != null) {
            val targetCursor = "final.${cursor.quote()}"
            val sourceCursor = "staging.${cursor.quote()}"
            val targetExtracted = "final.$extractedAt"
            val sourceExtracted = "staging.$extractedAt"
            return """
                |($targetCursor < $sourceCursor
                |OR ($targetCursor = $sourceCursor AND $targetExtracted < $sourceExtracted)
                |OR ($targetCursor IS NULL AND $sourceCursor IS NOT NULL)
                |OR ($targetCursor IS NULL AND $sourceCursor IS NULL AND $targetExtracted < $sourceExtracted))
            """.trimMargin()
        }
        return "final.$extractedAt < staging.$extractedAt"
    }

    /** Returns the three-part table name for Unity Catalog: `catalog`.`schema`.`table` */
    fun fullyQualifiedName(tableName: TableName): String =
        "${config.database.quote()}.${tableName.namespace.quote()}.${tableName.name.quote()}"

    /** Returns the fully qualified two-part namespace for Unity Catalog: `catalog`.`schema` */
    internal fun fullyQualifiedNamespace(namespace: String): String =
        "${config.database.quote()}.${namespace.quote()}"

    companion object {
        private const val QUOTE: String = "`"

        /** Wraps the string with backtick quotes for use as a Databricks SQL identifier. */
        fun String.quote(): String = "$QUOTE$this$QUOTE"

        /** Escapes and wraps the string as a single-quoted SQL string literal. */
        fun String.toSqlLiteral(): String = "'${this.replace("'", "''")}'"
    }

    private val metaColumns: LinkedHashMap<String, ColumnType> =
        linkedMapOf(
            Meta.COLUMN_NAME_AB_RAW_ID to ColumnType(STRING, false),
            Meta.COLUMN_NAME_AB_EXTRACTED_AT to ColumnType(TIMESTAMP, false),
            Meta.COLUMN_NAME_AB_META to ColumnType(STRING, false),
            Meta.COLUMN_NAME_AB_GENERATION_ID to ColumnType(LONG, true),
        )

    fun getMetaColumnNames(): Set<String> = metaColumns.keys
}
