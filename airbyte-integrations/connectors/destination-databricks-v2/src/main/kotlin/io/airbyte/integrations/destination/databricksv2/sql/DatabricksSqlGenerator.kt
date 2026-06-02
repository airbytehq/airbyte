/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.sql

import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.integrations.destination.databricksv2.schema.DatabricksTableSchemaMapper.Companion.LONG
import io.airbyte.integrations.destination.databricksv2.schema.DatabricksTableSchemaMapper.Companion.STRING
import io.airbyte.integrations.destination.databricksv2.schema.DatabricksTableSchemaMapper.Companion.TIMESTAMP
import io.airbyte.integrations.destination.databricksv2.spec.DatabricksV2Configuration
import jakarta.inject.Singleton

@Singleton
class DatabricksSqlGenerator(
    private val config: DatabricksV2Configuration,
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

        val createPrefix = if (replace) "CREATE OR REPLACE TABLE" else "CREATE TABLE IF NOT EXISTS"
        return "$createPrefix ${fullyQualifiedName(tableName)} ( $columnDeclarations)"
    }

    fun dropTable(tableName: TableName): String =
        "DROP TABLE IF EXISTS ${fullyQualifiedName(tableName)}"

    fun overwriteTable(sourceTableName: TableName, targetTableName: TableName): String =
        """
        |BEGIN TRANSACTION
        |CREATE OR REPLACE TABLE ${fullyQualifiedName(targetTableName)}
        |AS SELECT * FROM ${fullyQualifiedName(sourceTableName)};
        |${dropTable(sourceTableName)};
        |COMMIT
        """.trimMargin()

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

        // CDC hard delete handling
        val hasCdcDeleteColumn =
            tableSchema.columnSchema.finalSchema.containsKey(CDC_DELETED_AT_COLUMN)

        val cdcDeleteClause =
            if (hasCdcDeleteColumn) {
                "WHEN MATCHED AND staging.${CDC_DELETED_AT_COLUMN.quote()} IS NOT NULL THEN DELETE"
            } else {
                ""
            }

        val cdcSkipInsertClause =
            if (hasCdcDeleteColumn) {
                "AND staging.${CDC_DELETED_AT_COLUMN.quote()} IS NULL"
            } else {
                ""
            }

        return """
            |MERGE INTO ${fullyQualifiedName(targetTableName)} AS final
            |USING ($selectSource) AS staging
            |ON $pkEquivalent
            |$cdcDeleteClause
            |WHEN MATCHED AND $cursorComparison THEN UPDATE SET *
            |WHEN NOT MATCHED $cdcSkipInsertClause THEN INSERT *
        """.trimMargin()
    }

    // -- Query Operations --

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

    // -- Schema Evolution --

    fun alterTable(
        tableName: TableName,
        changeset: ColumnChangeset,
    ): String {
        val fqn = fullyQualifiedName(tableName)
        val statements = mutableListOf<String>()

        changeset.columnsToAdd.forEach { (name, columnType) ->
            statements.add("ALTER TABLE $fqn ADD COLUMN ${name.quote()} ${columnType.type}")
        }

        changeset.columnsToDrop.forEach { (name, _) ->
            statements.add("ALTER TABLE $fqn DROP COLUMN ${name.quote()}")
        }

        changeset.columnsToChange.forEach { (name, typeChange) ->
            if (typeChange.originalType.type != typeChange.newType.type) {
                statements.add(
                    "ALTER TABLE $fqn ALTER COLUMN ${name.quote()} TYPE ${typeChange.newType.type}",
                )
            }
        }

        return "BEGIN TRANSACTION\n${statements.joinToString(";\n")};\nCOMMIT;"
    }

    // -- Staging Operations --

    /** Creates a Unity Catalog Volume for staging CSV files */
    fun createStagingVolume(tableName: TableName): String =
        "CREATE VOLUME IF NOT EXISTS ${fullyQualifiedName(stagingVolumeName(tableName))}"

    /**
     * Generates a COPY INTO statement to load a staged CSV file from a Unity Catalog Volume into
     * the target table. Uses `inferSchema=false` so all CSV fields are read as STRING and
     * Databricks implicitly casts them to the target column types. Empty fields are treated as NULL
     * via the `nullValue` option.
     */
    fun copyIntoFromVolume(tableName: TableName, stagedFilePath: String): String =
        """
        |COPY INTO ${fullyQualifiedName(tableName)}
        |FROM '$stagedFilePath'
        |FILEFORMAT = CSV
        |FORMAT_OPTIONS (
        |    'header' = 'true',
        |    'inferSchema' = 'false',
        |    'escape' = '"',
        |    'nullValue' = ''
        |)
        """.trimMargin()

    /** Drops the Unity Catalog Volume used for staging CSV files. */
    fun dropStagingVolume(tableName: TableName): String =
        "DROP VOLUME IF EXISTS ${fullyQualifiedName(stagingVolumeName(tableName))}"

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
    internal fun fullyQualifiedName(tableName: TableName): String =
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
