/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.sql

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
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlin.collections.forEach

internal const val COUNT_TOTAL_ALIAS = "total"

private val log = KotlinLogging.logger {}

@Singleton
class PostgresDirectLoadSqlGenerator {
    companion object {
        internal val DEFAULT_COLUMNS =
            listOf(
                Column(
                    columnName = COLUMN_NAME_AB_RAW_ID,
                    columnTypeName = PostgresDataType.VARCHAR.typeName,
                    nullable = false

                ),
                Column(
                    columnName = COLUMN_NAME_AB_EXTRACTED_AT,
                    columnTypeName = PostgresDataType.TIMESTAMP_WITH_TIMEZONE.typeName,
                    nullable = false
                ),
                Column(
                    columnName = COLUMN_NAME_AB_META,
                    columnTypeName = PostgresDataType.JSONB.typeName,
                    nullable = false
                ),
                Column(
                    columnName = COLUMN_NAME_AB_GENERATION_ID,
                    columnTypeName = PostgresDataType.BIGINT.typeName,
                    nullable = false
                ),
            )

        /**
         * This extension is here to avoid writing `.also { log.info { it }}` for every returned string
         * we want to log
         */
        fun String.andLog(): String {
            log.info { this.trim() }
            return this
        }
    }

    fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean,
        isFinalTable: Boolean
    ): String {
        val columnDeclarations = columnsAndTypes(stream, columnNameMapping).joinToString(",\n")
        val dropTableIfExistsStatement = if (replace) "DROP TABLE IF EXISTS ${getFullyQualifiedName(tableName)};" else ""
        val setPrimaryKeysStatement = if (extractPks(stream, columnNameMapping).isNotEmpty()) {
            val primaryKeys = extractPks(stream, columnNameMapping).joinToString(", ")
            if(isFinalTable) "ALTER TABLE ${getFullyQualifiedName(tableName)} ADD PRIMARY KEY ($primaryKeys);"
            else "CREATE INDEX ON ${getFullyQualifiedName(tableName)} ($primaryKeys);"
        } else {
            ""
        }
        return """
            BEGIN TRANSACTION;
            $dropTableIfExistsStatement
            CREATE TABLE ${getFullyQualifiedName(tableName)} (
                $columnDeclarations
            );
            $setPrimaryKeysStatement
            CREATE INDEX ON ${getFullyQualifiedName(tableName)} ("$COLUMN_NAME_AB_EXTRACTED_AT");
            COMMIT;
            """
            .trimIndent()
            .andLog()
    }

    fun columnsAndTypes(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): List<Column> {
        val targetColumns = stream.schema
            .asColumns()
            .map { (columnName, columnType) ->
                val targetColumnName = getTargetColumnName(columnName, columnNameMapping)
                val typeName = columnType.type.toDialectType()
                Column(
                    columnName = targetColumnName,
                    columnTypeName = typeName,
                )
            }
            .toList()

        return (DEFAULT_COLUMNS + targetColumns)
    }

    fun overwriteTable(
        sourceTableName: TableName,
        targetTableName: TableName
    ): String {
        return """
            BEGIN TRANSACTION;
            DROP TABLE IF EXISTS ${getFullyQualifiedName(targetTableName)};
            ALTER TABLE ${getFullyQualifiedName(sourceTableName)} RENAME TO ${getName(targetTableName)};
            COMMIT;
            """
            .trimIndent()
            .andLog()
    }

    fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): String {
        val columnNames = getTargetColumnNames(columnNameMapping).joinToString(",")
        return """
            INSERT INTO ${getFullyQualifiedName(targetTableName)} ($columnNames)
            SELECT $columnNames
            FROM ${getFullyQualifiedName(sourceTableName)};
            """
            .trimIndent()
            .andLog()

    }

    private fun getTargetColumnNames(columnNameMapping: ColumnNameMapping): List<String> =
        getDefaultColumnNames() + columnNameMapping.map { (_, targetName) -> "\"${targetName}\"" }

    private fun getTargetColumnName(streamColumnName : String, columnNameMapping: ColumnNameMapping): String =
        columnNameMapping[streamColumnName] ?: streamColumnName


    //TODO: this is out of place, move to its own column class
    fun getDefaultColumnNames(): List<String> =
        DEFAULT_COLUMNS.map { "\"${it.columnName}\"" }

    /***
     *   - Validates that a primary key exists (required for ON CONFLICT)
     *   - Builds a list of primary key columns for the conflict clause
     *   - Calls selectDedupedRecords to get the deduplicated source data
     *   - Creates UPDATE assignments using EXCLUDED.column_name syntax
     *   - Adds a WHERE clause to only update when the new record is newer (based on cursor + extraction timestamp)
     *   - Generates the final INSERT ... ON CONFLICT statement
     *
     *
     */
    fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): String {
        val importType = stream.importType as Dedupe

        // Validate primary key exists
        if (importType.primaryKey.isEmpty()) {
            throw IllegalArgumentException("Cannot perform upsert without primary key")
        }

        // Build primary key column list
        val primaryKeyTargetColumns =
            importType.primaryKey.map { fieldPath ->
                val primaryKeyColumnName = fieldPath.first() //only at the root level for Postgres
                val targetColumnName = getTargetColumnName(primaryKeyColumnName, columnNameMapping)
                "\"$targetColumnName\""
            }

        // Get deduped records from source
        val selectSourceRecords = selectDedupedRecords(primaryKeyTargetColumns, importType.cursor, sourceTableName, columnNameMapping)

        // Build all column names (default + user columns)
        val allColumnNames = getTargetColumnNames(columnNameMapping)

        // Build column assignments for UPDATE
        val updateAssignments =
            allColumnNames.joinToString(",\n") { columnName ->
                "$columnName = EXCLUDED.$columnName"
            }

        // Build cursor comparison for determining which record is newer
        val whereClause =
            if (importType.cursor.isNotEmpty()) {
                val cursorFieldName = importType.cursor.first()
                val cursorColumn = columnNameMapping[cursorFieldName] ?: cursorFieldName
                val quotedCursorColumn = "\"$cursorColumn\""
                val extractedAtColumn = "\"$COLUMN_NAME_AB_EXTRACTED_AT\""
                """
                WHERE (
                  ${getFullyQualifiedName(targetTableName)}.$quotedCursorColumn < EXCLUDED.$quotedCursorColumn 
                  OR (${getFullyQualifiedName(targetTableName)}.$quotedCursorColumn = EXCLUDED.$quotedCursorColumn AND ${getFullyQualifiedName(targetTableName)}.$extractedAtColumn < EXCLUDED.$extractedAtColumn)
                  OR (${getFullyQualifiedName(targetTableName)}.$quotedCursorColumn IS NULL AND EXCLUDED.$quotedCursorColumn IS NOT NULL)
                  OR (${getFullyQualifiedName(targetTableName)}.$quotedCursorColumn IS NULL AND EXCLUDED.$quotedCursorColumn IS NULL AND ${getFullyQualifiedName(targetTableName)}.$extractedAtColumn < EXCLUDED.$extractedAtColumn)
                )
                """.trimIndent()
            } else {
                // No cursor - use extraction timestamp only
                val extractedAtColumn = "\"$COLUMN_NAME_AB_EXTRACTED_AT\""
                "WHERE ${getFullyQualifiedName(targetTableName)}.$extractedAtColumn < EXCLUDED.$extractedAtColumn"
            }

        // Build the INSERT ... ON CONFLICT statement
        val upsertStatement =
            """
            INSERT INTO ${getFullyQualifiedName(targetTableName)} (
              ${allColumnNames.joinToString(",\n  ")}
            )
            $selectSourceRecords
            ON CONFLICT (${primaryKeyTargetColumns.joinToString(", ")})
            DO UPDATE SET
              $updateAssignments
            $whereClause;
            """.trimIndent()

        return upsertStatement.andLog()
    }

    private fun extractPks(stream: DestinationStream, columnNameMapping: ColumnNameMapping): Set<String> {
        when (stream.importType) {
            is Dedupe -> return extractPks((stream.importType as Dedupe), columnNameMapping)
            else -> return setOf()
        }
    }

    private fun extractPks(
        importType: Dedupe,
        columnNameMapping: ColumnNameMapping
    ): Set<String> {
        return importType.primaryKey.map { fieldPath ->
            val primaryKeyColumnName = fieldPath.first() //only at the root level for Postgres
            val targetColumnName = getTargetColumnName(primaryKeyColumnName, columnNameMapping)
            "\"$targetColumnName\""
        }.toSet()
    }


    // this looks good!

    /**
     * Generates a SQL SELECT statement that extracts and deduplicates records from the source
     * table. Uses ROW_NUMBER() window function to select the most recent record per primary key.
     *
     *
     *   - Uses ROW_NUMBER() window function to partition by primary key
     *   - Orders by cursor (if present) and extraction timestamp
     *   - Returns only the most recent record for each primary key (row_number = 1)
     *
     */
    private fun selectDedupedRecords(
        primaryKeyTargetColumns: List<String>,
        cursor: List<String> = emptyList(), //TODO: pass it in already mapped to target column names.
        sourceTableName: TableName,
        columnNameMapping: ColumnNameMapping,

        ): String {
        val allColumnNames = getTargetColumnNames(columnNameMapping)


        // Build cursor order clause for sorting within each partition
        val cursorOrderClause =
            if (cursor.isNotEmpty()) {
                val cursorFieldName = cursor.first()
                val columnName = getTargetColumnName(cursorFieldName, columnNameMapping)
                "\"$columnName\" DESC NULLS LAST,"
            } else {
                ""
            }

        return """
            SELECT ${allColumnNames.joinToString(", ")}
            FROM (
              SELECT *,
                ROW_NUMBER() OVER (
                  PARTITION BY ${primaryKeyTargetColumns.joinToString( ", " )}
                  ORDER BY $cursorOrderClause "$COLUMN_NAME_AB_EXTRACTED_AT" DESC
                ) AS row_number
              FROM ${getFullyQualifiedName(sourceTableName)}
            ) AS deduplicated
            WHERE row_number = 1
        """.trimIndent()
    }

    fun dropTable(tableName: TableName): String =
        "DROP TABLE IF EXISTS ${getFullyQualifiedName(tableName)};".andLog()

    fun countTable(tableName: TableName): String {
        return "SELECT COUNT(*) AS \"$COUNT_TOTAL_ALIAS\" FROM ${getFullyQualifiedName(tableName)};".andLog()
    }

    fun createNamespace(namespace: String): String {
        return "CREATE SCHEMA IF NOT EXISTS \"$namespace\";".andLog()
    }

    fun getGenerationId(tableName: TableName): String =
        "SELECT \"${COLUMN_NAME_AB_GENERATION_ID}\" FROM ${getFullyQualifiedName(tableName)} LIMIT 1;".andLog()

    fun getTableSchema(tableName: TableName): String =
        """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = '${tableName.namespace}'
        AND table_name = '${tableName.name}';
        """.trimIndent().andLog()

    fun copyFromCsv(tableName: TableName): String =
        """
        COPY "${tableName.namespace}"."${tableName.name}"
        FROM STDIN
        WITH (FORMAT csv)
        """.trimIndent()

    //should all alters happen in one same tx? probably
    fun matchSchemas(
        tableName: TableName,
        columnsToAdd: Set<Column>,
        columnsToRemove: Set<Column>,
        columnsToModify: Set<Column>,
    ): Set<String> {
        val clauses = mutableSetOf<String>()
        val fullyQualifiedTableName = getFullyQualifiedName(tableName)
        columnsToAdd.forEach {
            clauses.add(
                "ALTER TABLE $fullyQualifiedTableName ADD COLUMN ${getName(it)} ${it.columnTypeName};".andLog()
            )
        }
        columnsToRemove.forEach {
            clauses.add("ALTER TABLE $fullyQualifiedTableName DROP COLUMN ${getName(it)};".andLog())
        }

        columnsToModify.forEach {
            clauses.add("ALTER TABLE $fullyQualifiedTableName ALTER COLUMN ${getName(it)} SET DATA TYPE ${it.columnTypeName};".andLog())
        }
        return clauses
    }

    private fun getFullyQualifiedName(tableName: TableName): String =
        "${getNamespace(tableName)}.${getName(tableName)}"

    private fun getNamespace(tableName: TableName): String =
        "\"${tableName.namespace}\""

    private fun getName(tableName: TableName): String =
        "\"${tableName.name}\""

    private fun getName(column: Column): String =
        "\"${column.columnName}\""

    fun AirbyteType.toDialectType(): String =
        when (this) {
            BooleanType -> PostgresDataType.BOOLEAN.typeName
            DateType -> PostgresDataType.DATE.typeName
            IntegerType -> PostgresDataType.BIGINT.typeName
            NumberType -> PostgresDataType.DECIMAL.typeName
            StringType -> PostgresDataType.VARCHAR.typeName
            TimeTypeWithTimezone -> PostgresDataType.TIME_WITH_TIMEZONE.typeName
            TimeTypeWithoutTimezone -> PostgresDataType.TIME.typeName
            TimestampTypeWithTimezone -> PostgresDataType.TIMESTAMP_WITH_TIMEZONE.typeName
            TimestampTypeWithoutTimezone -> PostgresDataType.TIMESTAMP.typeName
            is ArrayType,
            ArrayTypeWithoutSchema,
            is ObjectType,
            ObjectTypeWithEmptySchema,
            ObjectTypeWithoutSchema,
            is UnknownType,
            is UnionType -> PostgresDataType.JSONB.typeName
        }
}

data class Column(val columnName: String, val columnTypeName: String, val nullable: Boolean = true) {
    override fun toString(): String {
        val isNullableSuffix = if (nullable) "" else "NOT NULL"
        return "\"$columnName\" $columnTypeName $isNullableSuffix".trim()
    }
}
