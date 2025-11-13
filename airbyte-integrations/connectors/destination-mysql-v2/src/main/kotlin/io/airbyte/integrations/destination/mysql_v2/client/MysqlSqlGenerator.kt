package io.airbyte.integrations.destination.mysql_v2.client

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.ColumnTypeChange
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.mysql_v2.spec.MysqlConfiguration
import io.airbyte.integrations.destination.mysql_v2.sql.MysqlColumnUtils
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.UUID

private val log = KotlinLogging.logger {}

fun String.andLog(): String {
    log.info { this.trim() }
    return this
}

@Singleton
class MysqlSqlGenerator(
    private val columnUtils: MysqlColumnUtils,
    private val config: MysqlConfiguration,
) {

    private val AIRBYTE_META_COLUMNS = setOf(
        "_airbyte_raw_id",
        "_airbyte_extracted_at",
        "_airbyte_meta",
        "_airbyte_generation_id"
    )

    /**
     * Generates SQL to create a database/schema.
     */
    fun createNamespace(namespace: String): String {
        return "CREATE DATABASE IF NOT EXISTS `$namespace`".andLog()
    }

    /**
     * Generates SQL to check if a database exists.
     */
    fun namespaceExists(namespace: String): String {
        return """
            SELECT SCHEMA_NAME
            FROM INFORMATION_SCHEMA.SCHEMATA
            WHERE SCHEMA_NAME = '$namespace'
        """.trimIndent().andLog()
    }

    /**
     * Generates SQL to create a table with Airbyte metadata columns and user columns.
     */
    fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnMapping: ColumnNameMapping,
        replace: Boolean
    ): String {
        val replaceClause = if (replace) "OR REPLACE " else ""

        val columnDeclarations = stream.schema
            .asColumns()
            .filter { (name, _) -> name !in AIRBYTE_META_COLUMNS }
            .map { (name, field) ->
                val mappedName = columnMapping[name]!!
                columnUtils.formatColumn(mappedName, field.type, field.nullable)
            }
            .joinToString(",\n  ")

        return """
            CREATE ${replaceClause}TABLE IF NOT EXISTS ${fullyQualifiedName(tableName)} (
              `_airbyte_raw_id` VARCHAR(255) NOT NULL,
              `_airbyte_extracted_at` TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
              `_airbyte_meta` JSON NOT NULL,
              `_airbyte_generation_id` BIGINT NOT NULL,
              $columnDeclarations,
              PRIMARY KEY (`_airbyte_raw_id`)
            )
        """.trimIndent().andLog()
    }

    /**
     * Generates SQL to drop a table.
     */
    fun dropTable(tableName: TableName): String {
        return "DROP TABLE IF EXISTS ${fullyQualifiedName(tableName)}".andLog()
    }

    /**
     * Generates SQL to count rows in a table.
     */
    fun countTable(tableName: TableName): String {
        return """
            SELECT COUNT(*) AS count
            FROM ${fullyQualifiedName(tableName)}
        """.trimIndent().andLog()
    }

    /**
     * Generates SQL to get the generation ID from a table.
     */
    fun getGenerationId(tableName: TableName): String {
        return """
            SELECT `_airbyte_generation_id` AS generation_id
            FROM ${fullyQualifiedName(tableName)}
            LIMIT 1
        """.trimIndent().andLog()
    }

    /**
     * Generates SQL to copy data from one table to another.
     */
    fun copyTable(
        columnMapping: ColumnNameMapping,
        source: TableName,
        target: TableName
    ): String {
        // Include Airbyte metadata columns + user columns
        val airbyteColumns = listOf("_airbyte_raw_id", "_airbyte_extracted_at", "_airbyte_meta", "_airbyte_generation_id")
        val userColumns = columnMapping.values.toList()
        val allColumns = airbyteColumns + userColumns
        val columnList = allColumns.joinToString(", ") { "`$it`" }

        return """
            INSERT INTO ${fullyQualifiedName(target)} ($columnList)
            SELECT $columnList
            FROM ${fullyQualifiedName(source)}
        """.trimIndent().andLog()
    }

    /**
     * Generates SQL to overwrite a target table with a source table (for truncate mode).
     * Uses MySQL's RENAME TABLE for atomic swap.
     */
    fun overwriteTable(source: TableName, target: TableName): List<String> {
        val tempBackup = TableName(target.namespace, "_airbyte_tmp_backup_${UUID.randomUUID()}")

        return listOf(
            // Rename target to backup
            "RENAME TABLE ${fullyQualifiedName(target)} TO ${fullyQualifiedName(tempBackup)}".andLog(),
            // Rename source to target
            "RENAME TABLE ${fullyQualifiedName(source)} TO ${fullyQualifiedName(target)}".andLog(),
            // Drop backup
            "DROP TABLE IF EXISTS ${fullyQualifiedName(tempBackup)}".andLog()
        )
    }

    /**
     * Generates SQL to upsert (dedupe) data from source table into target table.
     * Uses INSERT ... ON DUPLICATE KEY UPDATE (MySQL 5.7+) or MERGE (MySQL 8.0.20+).
     *
     * Steps:
     * 1. Dedupe source table using ROW_NUMBER() window function
     * 2. Upsert deduped records into target
     */
    fun upsertTable(
        stream: DestinationStream,
        columnMapping: ColumnNameMapping,
        source: TableName,
        target: TableName
    ): List<String> {
        val importType = stream.importType as? Dedupe
            ?: throw IllegalArgumentException("upsertTable requires Dedupe import type")

        val pkColumns = importType.primaryKey.map { fieldPath -> columnMapping[fieldPath.first()]!! }
        val allColumns = columnMapping.values.toList()

        // Determine cursor column for ordering
        val cursorColumn: String = if (importType.cursor.isNotEmpty()) {
            val cursorFieldName = importType.cursor.first()
            columnMapping[cursorFieldName] ?: "_airbyte_extracted_at"
        } else {
            "_airbyte_extracted_at"
        }

        // Step 1: Create deduped temp table
        // Note: Use CREATE TEMPORARY TABLE ... SELECT (not AS SELECT) to avoid DEFAULT issues
        val dedupedTable = TableName(source.namespace, "_airbyte_deduped_${UUID.randomUUID()}")

        val createDedupedTableSql = if (pkColumns.isNotEmpty()) {
            """
            CREATE TEMPORARY TABLE ${fullyQualifiedName(dedupedTable)}
            SELECT * FROM (
              SELECT *, ROW_NUMBER() OVER (
                PARTITION BY ${pkColumns.joinToString(", ") { "`$it`" }}
                ORDER BY `$cursorColumn` DESC, `_airbyte_extracted_at` DESC
              ) AS `row_number`
              FROM ${fullyQualifiedName(source)}
            ) AS numbered_rows
            WHERE `row_number` = 1
            """.trimIndent().andLog()
        } else {
            // No primary key - just dedupe by all columns
            """
            CREATE TEMPORARY TABLE ${fullyQualifiedName(dedupedTable)}
            SELECT DISTINCT * FROM ${fullyQualifiedName(source)}
            """.trimIndent().andLog()
        }

        // Step 2: Upsert into target
        // Include Airbyte metadata columns + user columns
        val airbyteColumns = listOf("_airbyte_raw_id", "_airbyte_extracted_at", "_airbyte_meta", "_airbyte_generation_id")
        val allColumnsWithAirbyte = (airbyteColumns + allColumns).distinct()
        val columnList = allColumnsWithAirbyte.joinToString(", ") { "`$it`" }
        val updateAssignments = allColumnsWithAirbyte
            .filter { it !in pkColumns && it !in airbyteColumns } // Don't update PK or Airbyte columns
            .joinToString(", ") { "`$it` = VALUES(`$it`)" }

        val upsertSql = if (pkColumns.isNotEmpty()) {
            """
            INSERT INTO ${fullyQualifiedName(target)} ($columnList)
            SELECT $columnList FROM ${fullyQualifiedName(dedupedTable)}
            ON DUPLICATE KEY UPDATE $updateAssignments
            """.trimIndent().andLog()
        } else {
            // No PK - just insert
            """
            INSERT IGNORE INTO ${fullyQualifiedName(target)} ($columnList)
            SELECT $columnList FROM ${fullyQualifiedName(dedupedTable)}
            """.trimIndent().andLog()
        }

        // Step 3: Cleanup
        val cleanupSql = "DROP TEMPORARY TABLE IF EXISTS ${fullyQualifiedName(dedupedTable)}".andLog()

        return listOf(createDedupedTableSql, upsertSql, cleanupSql)
    }

    /**
     * Generates SQL statements to alter a table (add, drop, or modify columns).
     */
    fun alterTable(
        tableName: TableName,
        columnsToAdd: Map<String, ColumnType>,
        columnsToDrop: Map<String, ColumnType>,
        columnsToChange: Map<String, ColumnTypeChange>,
    ): Set<String> {
        val statements = mutableSetOf<String>()

        // ADD COLUMN
        columnsToAdd.forEach { (name, type) ->
            val nullableDecl = if (type.nullable) "" else " NOT NULL"
            statements.add(
                "ALTER TABLE ${fullyQualifiedName(tableName)} ADD COLUMN `$name` ${type.type}$nullableDecl".andLog()
            )
        }

        // DROP COLUMN
        columnsToDrop.forEach { (name, _) ->
            statements.add(
                "ALTER TABLE ${fullyQualifiedName(tableName)} DROP COLUMN `$name`".andLog()
            )
        }

        // MODIFY COLUMN
        columnsToChange.forEach { (name, typeChange) ->
            when {
                // Safe: NOT NULL → NULL (drop NOT NULL constraint)
                !typeChange.originalType.nullable && typeChange.newType.nullable -> {
                    statements.add(
                        "ALTER TABLE ${fullyQualifiedName(tableName)} MODIFY COLUMN `$name` ${typeChange.newType.type} NULL".andLog()
                    )
                }

                // Type change: Use temp column approach
                typeChange.originalType.type != typeChange.newType.type -> {
                    val tempColumn = "${name}_tmp_${UUID.randomUUID().toString().replace("-", "")}"

                    // 1. Add temp column
                    statements.add(
                        "ALTER TABLE ${fullyQualifiedName(tableName)} ADD COLUMN `$tempColumn` ${typeChange.newType.type}".andLog()
                    )

                    // 2. Copy data (with cast)
                    statements.add(
                        "UPDATE ${fullyQualifiedName(tableName)} SET `$tempColumn` = CAST(`$name` AS ${typeChange.newType.type})".andLog()
                    )

                    // 3. Drop original column
                    statements.add(
                        "ALTER TABLE ${fullyQualifiedName(tableName)} DROP COLUMN `$name`".andLog()
                    )

                    // 4. Rename temp to original
                    statements.add(
                        "ALTER TABLE ${fullyQualifiedName(tableName)} CHANGE COLUMN `$tempColumn` `$name` ${typeChange.newType.type}".andLog()
                    )
                }

                // Unsafe: NULL → NOT NULL (skip - can't enforce if nulls exist)
                else -> {
                    log.info { "Skipping nullable to non-nullable change for column $name" }
                }
            }
        }

        return statements
    }

    private fun fullyQualifiedName(tableName: TableName) =
        columnUtils.fullyQualifiedName(tableName.namespace, tableName.name)
}
