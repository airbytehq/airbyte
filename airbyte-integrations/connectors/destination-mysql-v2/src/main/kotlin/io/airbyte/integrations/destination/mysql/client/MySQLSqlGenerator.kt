package io.airbyte.integrations.destination.mysql.client

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

private val log = KotlinLogging.logger {}

fun String.andLog(): String {
    log.info { this.trim() }
    return this
}

@Singleton
class MySQLSqlGenerator(
    private val columnUtils: MySQLColumnUtils,
) {

    fun createNamespace(namespace: String): String {
        // MySQL uses databases as namespaces
        return "CREATE DATABASE IF NOT EXISTS ${namespace.quote()}".andLog()
    }

    fun namespaceExists(namespace: String): String {
        return """
            SELECT SCHEMA_NAME
            FROM information_schema.SCHEMATA
            WHERE SCHEMA_NAME = '${namespace}'
        """.trimIndent().andLog()
    }

    fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnMapping: ColumnNameMapping,
        replace: Boolean
    ): String {
        val columnDeclarations = stream.schema.asColumns()
            .filter { (name, _) -> name !in AIRBYTE_META_COLUMNS }
            .map { (name, type) ->
                val mappedName = columnMapping[name]!!
                columnUtils.formatColumn(mappedName, type.type, type.nullable)
            }
            .joinToString(",\n  ")

        // Note: replace parameter is handled by client (drops then creates)
        // Just return CREATE TABLE statement here
        return """
            CREATE TABLE ${fullyQualifiedName(tableName)} (
              `$COLUMN_NAME_AB_RAW_ID` VARCHAR(255) NOT NULL,
              `$COLUMN_NAME_AB_EXTRACTED_AT` DATETIME(6) NOT NULL,
              `$COLUMN_NAME_AB_META` JSON NOT NULL,
              `$COLUMN_NAME_AB_GENERATION_ID` BIGINT,
              $columnDeclarations
            )
        """.trimIndent().andLog()
    }

    fun dropTable(tableName: TableName): String {
        return "DROP TABLE IF EXISTS ${fullyQualifiedName(tableName)}".andLog()
    }

    fun countTable(tableName: TableName): String {
        return """
            SELECT COUNT(*) AS count
            FROM ${fullyQualifiedName(tableName)}
        """.trimIndent().andLog()
    }

    fun getGenerationId(tableName: TableName): String {
        return """
            SELECT `$COLUMN_NAME_AB_GENERATION_ID` AS generation_id
            FROM ${fullyQualifiedName(tableName)}
            LIMIT 1
        """.trimIndent().andLog()
    }

    fun overwriteTable(source: TableName, target: TableName): List<String> {
        // MySQL doesn't have SWAP or EXCHANGE, use DROP + RENAME
        // RENAME TABLE requires fully qualified name for both source and target
        return listOf(
            "DROP TABLE IF EXISTS ${fullyQualifiedName(target)}".andLog(),
            "RENAME TABLE ${fullyQualifiedName(source)} TO ${fullyQualifiedName(target)}".andLog(),
        )
    }

    fun copyTable(
        columnMapping: ColumnNameMapping,
        source: TableName,
        target: TableName
    ): String {
        // Include Airbyte metadata columns + user columns
        val allColumns = listOf(
            COLUMN_NAME_AB_RAW_ID,
            COLUMN_NAME_AB_EXTRACTED_AT,
            COLUMN_NAME_AB_META,
            COLUMN_NAME_AB_GENERATION_ID
        ) + columnMapping.values

        val columnList = allColumns.joinToString(", ") { "`$it`" }

        return """
            INSERT INTO ${fullyQualifiedName(target)} ($columnList)
            SELECT $columnList
            FROM ${fullyQualifiedName(source)}
        """.trimIndent().andLog()
    }

    fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        source: TableName,
        target: TableName
    ): List<String> {
        val importType = stream.importType as io.airbyte.cdk.load.command.Dedupe
        // Extract primary key column names (only support top-level keys)
        // primaryKey is List<List<String>> - each inner list is a field path
        val pkColumns = importType.primaryKey.map { fieldPath: List<String> ->
            if (fieldPath.size != 1) {
                throw UnsupportedOperationException("Only top-level primary keys are supported, got $fieldPath")
            }
            val fieldName = fieldPath.first()
            columnNameMapping[fieldName] ?: fieldName
        }
        val allColumns = listOf(
            COLUMN_NAME_AB_RAW_ID,
            COLUMN_NAME_AB_EXTRACTED_AT,
            COLUMN_NAME_AB_META,
            COLUMN_NAME_AB_GENERATION_ID
        ) + columnNameMapping.values

        val cursorColumn = if (importType.cursor.isNotEmpty()) {
            // Cursor is List<String>, just a single field name
            val cursorFieldName = importType.cursor.first()
            columnNameMapping[cursorFieldName] ?: COLUMN_NAME_AB_EXTRACTED_AT
        } else {
            COLUMN_NAME_AB_EXTRACTED_AT
        }

        // Temp table for deduplication (keep short due to MySQL 64 char limit)
        val tempTable = "dedup_tmp"
        val tempTableFullName = "`${target.namespace}`.`$tempTable`"

        val statements = mutableListOf<String>()

        // 1. Create temp table with deduped data using window function
        // Note: Using regular table instead of TEMPORARY due to HikariCP connection pooling
        // Check if CDC column exists in the mapping
        val hasCdcColumn = columnNameMapping.containsKey("_ab_cdc_deleted_at")
        val cdcFilter = if (hasCdcColumn) "WHERE `_ab_cdc_deleted_at` IS NULL" else ""

        if (pkColumns.isNotEmpty()) {
            val columnList = allColumns.joinToString(", ") { "`$it`" }
            statements.add("""
                CREATE TABLE $tempTableFullName AS
                SELECT * FROM (
                  SELECT *, ROW_NUMBER() OVER (
                    PARTITION BY ${pkColumns.joinToString(", ") { "`$it`" }}
                    ORDER BY `$cursorColumn` DESC, `$COLUMN_NAME_AB_EXTRACTED_AT` DESC
                  ) AS rn
                  FROM ${fullyQualifiedName(source)}
                  $cdcFilter
                ) AS ranked WHERE rn = 1
            """.trimIndent().andLog())
        } else {
            // No primary key - just copy all (excluding deleted records if CDC enabled)
            statements.add("""
                CREATE TABLE $tempTableFullName AS
                SELECT * FROM ${fullyQualifiedName(source)}
                $cdcFilter
            """.trimIndent().andLog())
        }

        // 2. Delete existing records with matching PKs
        if (pkColumns.isNotEmpty()) {
            val pkMatch = pkColumns.joinToString(" AND ") { pk ->
                "${fullyQualifiedName(target)}.`$pk` = $tempTableFullName.`$pk`"
            }
            statements.add("""
                DELETE ${fullyQualifiedName(target)}
                FROM ${fullyQualifiedName(target)}
                INNER JOIN $tempTableFullName
                ON $pkMatch
            """.trimIndent().andLog())
        }

        // 3. Insert all from deduped temp table
        val columnList = allColumns.filter { it != "rn" }.joinToString(", ") { "`$it`" }
        statements.add("""
            INSERT INTO ${fullyQualifiedName(target)} ($columnList)
            SELECT $columnList FROM $tempTableFullName
        """.trimIndent().andLog())

        // 4. Drop temp table
        statements.add("DROP TABLE IF EXISTS $tempTableFullName".andLog())

        return statements
    }

    private fun String.quote() = "`$this`"  // MySQL uses backticks for identifiers

    private fun fullyQualifiedName(tableName: TableName) =
        "${tableName.namespace.quote()}.${tableName.name.quote()}"

    companion object {
        private val AIRBYTE_META_COLUMNS = setOf(
            COLUMN_NAME_AB_RAW_ID,
            COLUMN_NAME_AB_EXTRACTED_AT,
            COLUMN_NAME_AB_META,
            COLUMN_NAME_AB_GENERATION_ID
        )
    }
}
