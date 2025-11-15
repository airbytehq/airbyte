/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.sql

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.ColumnTypeChange
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_DATA
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.cdk.load.util.UUIDGenerator
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.CdcDeletionMode
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.write.load.CSV_FIELD_SEPARATOR
import io.airbyte.integrations.destination.snowflake.write.load.CSV_LINE_DELIMITER
import io.mockk.every
import io.mockk.mockk
import java.util.UUID
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class SnowflakeDirectLoadSqlGeneratorTest {

    private lateinit var columnUtils: SnowflakeColumnUtils
    private lateinit var snowflakeDirectLoadSqlGenerator: SnowflakeDirectLoadSqlGenerator
    private val uuidGenerator: UUIDGenerator = mockk()
    private val snowflakeConfiguration: SnowflakeConfiguration = mockk()
    private lateinit var snowflakeSqlNameUtils: SnowflakeSqlNameUtils

    @BeforeEach
    fun setUp() {
        every { snowflakeConfiguration.cdcDeletionMode } returns CdcDeletionMode.HARD_DELETE
        every { snowflakeConfiguration.database } returns "test-database"
        every { snowflakeConfiguration.legacyRawTablesOnly } returns false
        columnUtils = mockk {
            every { formatColumnName(any()) } answers
                {
                    val columnName = firstArg<String>()
                    if (columnName == COLUMN_NAME_DATA) columnName
                    else columnName.toSnowflakeCompatibleName()
                }
            every { getGenerationIdColumnName() } returns
                COLUMN_NAME_AB_GENERATION_ID.toSnowflakeCompatibleName()
        }
        snowflakeSqlNameUtils = SnowflakeSqlNameUtils(snowflakeConfiguration)
        snowflakeDirectLoadSqlGenerator =
            SnowflakeDirectLoadSqlGenerator(
                columnUtils = columnUtils,
                uuidGenerator = uuidGenerator,
                snowflakeConfiguration = snowflakeConfiguration,
                snowflakeSqlNameUtils = snowflakeSqlNameUtils,
            )
    }

    @Test
    fun testGenerateCountTableQuery() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val sql = snowflakeDirectLoadSqlGenerator.countTable(tableName)
        assertEquals(
            "SELECT COUNT(*) AS TOTAL FROM ${snowflakeSqlNameUtils.fullyQualifiedName(tableName)}",
            sql
        )
    }

    @Test
    fun testGenerateNamespaceStatement() {
        val namespace = "namespace"
        val sql = snowflakeDirectLoadSqlGenerator.createNamespace(namespace)
        assertEquals(
            "CREATE SCHEMA IF NOT EXISTS ${snowflakeSqlNameUtils.fullyQualifiedNamespace(namespace)}",
            sql
        )
    }

    @Test
    fun testGenerateCreateTableStatement() {
        val columnAndType =
            ColumnAndType(columnName = "column-name", columnType = "VARCHAR NOT NULL")
        val columnNameMapping = mockk<ColumnNameMapping>(relaxed = true)
        val stream = mockk<DestinationStream>(relaxed = true)
        val tableName = TableName(namespace = "namespace", name = "name")

        every { columnUtils.columnsAndTypes(any(), columnNameMapping) } returns
            listOf(columnAndType)

        val sql =
            snowflakeDirectLoadSqlGenerator.createTable(
                stream = stream,
                tableName = tableName,
                columnNameMapping = columnNameMapping,
                replace = true
            )
        assertEquals(
            "CREATE OR REPLACE TABLE ${snowflakeSqlNameUtils.fullyQualifiedName(tableName)} (\n    $columnAndType\n)",
            sql
        )
    }

    @Test
    fun testGenerateCreateTableStatementNoReplace() {
        val columnAndType =
            ColumnAndType(columnName = "column-name", columnType = "VARCHAR NOT NULL")
        val columnNameMapping = mockk<ColumnNameMapping>(relaxed = true)
        val stream = mockk<DestinationStream>(relaxed = true)
        val tableName = TableName(namespace = "namespace", name = "name")

        every { columnUtils.columnsAndTypes(any(), columnNameMapping) } returns
            listOf(columnAndType)

        val sql =
            snowflakeDirectLoadSqlGenerator.createTable(
                stream = stream,
                tableName = tableName,
                columnNameMapping = columnNameMapping,
                replace = false
            )
        assertEquals(
            "CREATE TABLE ${snowflakeSqlNameUtils.fullyQualifiedName(tableName)} (\n    $columnAndType\n)",
            sql
        )
    }

    @Test
    fun testGenerateShowColumns() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val sql = snowflakeDirectLoadSqlGenerator.showColumns(tableName)
        assertEquals(
            "SHOW COLUMNS IN TABLE ${snowflakeSqlNameUtils.fullyQualifiedName(tableName)}",
            sql
        )
    }

    @Test
    fun testGenerateCopyTable() {
        val columnName = "column-name"
        val mappedColumnName = "mapped-column-name"
        val columns = mapOf(columnName to mappedColumnName)
        val columnNameMapping = ColumnNameMapping(columns)
        val columnNames =
            (DEFAULT_COLUMNS.map { it.columnName } + "mappedColumnName").joinToString(",") {
                it.toSnowflakeCompatibleName().quote()
            }
        val sourceTableName = TableName(namespace = "namespace", name = "source")
        val destinationTableName = TableName(namespace = "namespace", name = "destination")

        every { columnUtils.getColumnNames(columnNameMapping) } returns columnNames

        val expected =
            """
            INSERT INTO ${snowflakeSqlNameUtils.fullyQualifiedName(destinationTableName)} 
            (
                $columnNames
            )
            SELECT
                $columnNames
            FROM ${snowflakeSqlNameUtils.fullyQualifiedName(sourceTableName)}
            """.trimIndent()
        val sql =
            snowflakeDirectLoadSqlGenerator.copyTable(
                columnNameMapping = columnNameMapping,
                sourceTableName = sourceTableName,
                targetTableName = destinationTableName,
            )
        assertEquals(expected, sql)
    }

    @Test
    fun testGenerateUpsertTable() {
        val primaryKey = listOf(listOf("primaryKey"))
        val cursor = listOf("cursor")
        val stream =
            mockk<DestinationStream> {
                every { importType } returns
                    Dedupe(
                        primaryKey = primaryKey,
                        cursor = cursor,
                    )
                every { schema } returns StringType
            }
        val columnNameMapping = ColumnNameMapping(emptyMap())
        val sourceTableName = TableName(namespace = "namespace", name = "source")
        val destinationTableName = TableName(namespace = "namespace", name = "destination")
        val expectedColumns = DEFAULT_COLUMNS.map { it.columnName.toSnowflakeCompatibleName() }

        every { columnUtils.getFormattedColumnNames(any(), columnNameMapping) } returns
            expectedColumns.map { it.quote() }
        every { columnUtils.getFormattedColumnNames(any(), columnNameMapping, false) } returns
            expectedColumns

        val expectedDestinationTable =
            "${snowflakeConfiguration.database.toSnowflakeCompatibleName().quote()}.${destinationTableName.namespace.quote()}.${destinationTableName.name.quote()}"
        val expectedSourceTable =
            "${snowflakeConfiguration.database.toSnowflakeCompatibleName().quote()}.${sourceTableName.namespace.quote()}.${sourceTableName.name.quote()}"
        val expected =
            """
            MERGE INTO $expectedDestinationTable AS target_table
            USING (
                          WITH records AS (
              SELECT
                ${expectedColumns.joinToString(",\n") { it.quote() } }
              FROM $expectedSourceTable
            ), numbered_rows AS (
              SELECT *, ROW_NUMBER() OVER (
                PARTITION BY "primaryKey" ORDER BY "cursor" DESC NULLS LAST, "_AIRBYTE_EXTRACTED_AT" DESC
              ) AS row_number
              FROM records
            )
            SELECT ${expectedColumns.joinToString(",\n") { it.quote() } }
            FROM numbered_rows
            WHERE row_number = 1
            ) AS new_record
            ON (target_table."primaryKey" = new_record."primaryKey" OR (target_table."primaryKey" IS NULL AND new_record."primaryKey" IS NULL))
            WHEN MATCHED AND (
  target_table."cursor" < new_record."cursor"
  OR (target_table."cursor" = new_record."cursor" AND target_table."_AIRBYTE_EXTRACTED_AT" < new_record."_AIRBYTE_EXTRACTED_AT")
  OR (target_table."cursor" IS NULL AND new_record."cursor" IS NULL AND target_table."_AIRBYTE_EXTRACTED_AT" < new_record."_AIRBYTE_EXTRACTED_AT")
  OR (target_table."cursor" IS NULL AND new_record."cursor" IS NOT NULL)
) THEN UPDATE SET
              "_AIRBYTE_RAW_ID" = new_record."_AIRBYTE_RAW_ID",
"_AIRBYTE_EXTRACTED_AT" = new_record."_AIRBYTE_EXTRACTED_AT",
"_AIRBYTE_META" = new_record."_AIRBYTE_META",
"_AIRBYTE_GENERATION_ID" = new_record."_AIRBYTE_GENERATION_ID"
            WHEN NOT MATCHED THEN INSERT (
              ${expectedColumns.joinToString(",\n") { it.quote() } }
            ) VALUES (
              new_record."_AIRBYTE_RAW_ID",
new_record."_AIRBYTE_EXTRACTED_AT",
new_record."_AIRBYTE_META",
new_record."_AIRBYTE_GENERATION_ID"
            )
        """.trimIndent()

        val sql =
            snowflakeDirectLoadSqlGenerator.upsertTable(
                stream = stream,
                columnNameMapping = columnNameMapping,
                sourceTableName = sourceTableName,
                targetTableName = destinationTableName,
            )
        assertEquals(expected, sql)
    }

    @Test
    fun testGenerateDropTable() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val sql = snowflakeDirectLoadSqlGenerator.dropTable(tableName)
        assertEquals(
            "DROP TABLE IF EXISTS ${snowflakeSqlNameUtils.fullyQualifiedName(tableName)}",
            sql
        )
    }

    @Test
    fun testGenerateGenerationIdQuery() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val sql = snowflakeDirectLoadSqlGenerator.getGenerationId(tableName = tableName)
        val expectedSql =
            """
            SELECT "${COLUMN_NAME_AB_GENERATION_ID.toSnowflakeCompatibleName()}"
            FROM ${snowflakeSqlNameUtils.fullyQualifiedName(tableName)}
            LIMIT 1
        """.trimIndent()
        assertEquals(expectedSql, sql)
    }

    @Test
    fun testGenerateCreateStage() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val stagingTableName = snowflakeSqlNameUtils.fullyQualifiedStageName(tableName)
        val sql = snowflakeDirectLoadSqlGenerator.createSnowflakeStage(tableName)
        assertEquals("CREATE STAGE IF NOT EXISTS $stagingTableName", sql)
    }

    @Test
    fun testGeneratePutInStage() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val tempFilePath = "/some/file/path.csv"
        val stagingTableName = snowflakeSqlNameUtils.fullyQualifiedStageName(tableName)
        val sql = snowflakeDirectLoadSqlGenerator.putInStage(tableName, tempFilePath)
        val expectedSql =
            """
            PUT 'file://$tempFilePath' '@$stagingTableName'
            AUTO_COMPRESS = FALSE
            SOURCE_COMPRESSION = GZIP
            OVERWRITE = TRUE
        """.trimIndent()
        assertEquals(expectedSql, sql)
    }

    @Test
    fun testGenerateCopyFromStage() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val targetTableName = snowflakeSqlNameUtils.fullyQualifiedName(tableName)
        val stagingTableName = snowflakeSqlNameUtils.fullyQualifiedStageName(tableName)
        val sql = snowflakeDirectLoadSqlGenerator.copyFromStage(tableName, "test.csv.gz")
        val expectedSql =
            """
            COPY INTO $targetTableName
            FROM '@$stagingTableName'
            FILE_FORMAT = (
                TYPE = 'CSV'
                COMPRESSION = GZIP
                FIELD_DELIMITER = '$CSV_FIELD_SEPARATOR'
                RECORD_DELIMITER = '$CSV_LINE_DELIMITER'
                FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                TRIM_SPACE = TRUE
                ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE
                REPLACE_INVALID_CHARACTERS = TRUE
                ESCAPE = NONE
                ESCAPE_UNENCLOSED_FIELD = NONE
            )
            ON_ERROR = 'ABORT_STATEMENT'
            PURGE = TRUE
            files = ('test.csv.gz')
        """.trimIndent()
        assertEquals(expectedSql, sql)
    }

    @Test
    fun testGenerateUpsertTableWithCdcHardDelete() {
        // Test with CDC hard delete mode when _ab_cdc_deleted_at column is present
        val primaryKey = listOf(listOf("id"))
        val cursor = listOf("updated_at")

        // Create schema with CDC deletion column
        val schemaWithCdc =
            ObjectType(
                properties =
                    linkedMapOf(
                        "id" to FieldType(StringType, nullable = false),
                        "name" to FieldType(StringType, nullable = true),
                        "updated_at" to FieldType(TimestampTypeWithTimezone, nullable = true),
                        CDC_DELETED_AT_COLUMN to
                            FieldType(TimestampTypeWithTimezone, nullable = true)
                    )
            )

        val stream =
            mockk<DestinationStream> {
                every { importType } returns
                    Dedupe(
                        primaryKey = primaryKey,
                        cursor = cursor,
                    )
                every { schema } returns schemaWithCdc
            }

        val columnNameMapping =
            ColumnNameMapping(
                mapOf(
                    "id" to "id",
                    "name" to "name",
                    "updated_at" to "updated_at",
                    CDC_DELETED_AT_COLUMN to "_ab_cdc_deleted_at"
                )
            )
        val sourceTableName = TableName(namespace = "test_ns", name = "source")
        val targetTableName = TableName(namespace = "test_ns", name = "target")

        every { columnUtils.getFormattedColumnNames(any(), columnNameMapping, any()) } returns
            listOf(
                    "id",
                    "name",
                    "updated_at",
                    CDC_DELETED_AT_COLUMN,
                )
                .map { it.toSnowflakeCompatibleName().quote() } +
                DEFAULT_COLUMNS.map { it.columnName.toSnowflakeCompatibleName().quote() }

        val sql =
            snowflakeDirectLoadSqlGenerator.upsertTable(
                stream = stream,
                columnNameMapping = columnNameMapping,
                sourceTableName = sourceTableName,
                targetTableName = targetTableName,
            )

        // Should include the DELETE clause and skip insert clause
        assert(
            sql.contains(
                "WHEN MATCHED AND new_record.${CDC_DELETED_AT_COLUMN.toSnowflakeCompatibleName().quote()} IS NOT NULL"
            )
        )
        assert(sql.contains("THEN DELETE"))
        assert(
            sql.contains(
                "WHEN NOT MATCHED AND new_record.${CDC_DELETED_AT_COLUMN.toSnowflakeCompatibleName().quote()} IS NULL THEN INSERT"
            )
        )
    }

    @Test
    fun testGenerateUpsertTableWithCdcSoftDelete() {
        // Test with CDC soft delete mode - should NOT add delete clauses
        every { snowflakeConfiguration.cdcDeletionMode } returns CdcDeletionMode.SOFT_DELETE
        val softDeleteGenerator =
            SnowflakeDirectLoadSqlGenerator(
                columnUtils = columnUtils,
                uuidGenerator = uuidGenerator,
                snowflakeConfiguration = snowflakeConfiguration,
                snowflakeSqlNameUtils = snowflakeSqlNameUtils,
            )

        val primaryKey = listOf(listOf("id"))
        val cursor = listOf("updated_at")

        // Create schema with CDC deletion column
        val schemaWithCdc =
            ObjectType(
                properties =
                    linkedMapOf(
                        "id" to FieldType(StringType, nullable = false),
                        "name" to FieldType(StringType, nullable = true),
                        "updated_at" to FieldType(TimestampTypeWithTimezone, nullable = true),
                        CDC_DELETED_AT_COLUMN to
                            FieldType(TimestampTypeWithTimezone, nullable = true)
                    )
            )

        val stream =
            mockk<DestinationStream> {
                every { importType } returns
                    Dedupe(
                        primaryKey = primaryKey,
                        cursor = cursor,
                    )
                every { schema } returns schemaWithCdc
            }

        val columnNameMapping =
            ColumnNameMapping(
                mapOf(
                    "id" to "id",
                    "name" to "name",
                    "updated_at" to "updated_at",
                    CDC_DELETED_AT_COLUMN to "_ab_cdc_deleted_at"
                )
            )
        val sourceTableName = TableName(namespace = "test_ns", name = "source")
        val targetTableName = TableName(namespace = "test_ns", name = "target")

        every { columnUtils.getFormattedColumnNames(any(), columnNameMapping, any()) } returns
            listOf(
                    "id",
                    "name",
                    "updated_at",
                    CDC_DELETED_AT_COLUMN.toSnowflakeCompatibleName(),
                )
                .map { it.quote() } + DEFAULT_COLUMNS.map { it.columnName.quote() }
        every { columnUtils.formatColumnName(any()) } answers { firstArg<String>() }

        val sql =
            softDeleteGenerator.upsertTable(
                stream = stream,
                columnNameMapping = columnNameMapping,
                sourceTableName = sourceTableName,
                targetTableName = targetTableName,
            )

        // Should NOT include DELETE clause in soft delete mode
        assert(!sql.contains("THEN DELETE"))
        assert(sql.contains("WHEN NOT MATCHED THEN INSERT"))
        assert(!sql.contains("AND new_record.${CDC_DELETED_AT_COLUMN.quote()} IS NULL"))
    }

    @Test
    fun testGenerateUpsertTableWithoutCdcColumn() {
        // Test that CDC deletion logic is NOT applied when column is absent
        val primaryKey = listOf(listOf("id"))
        val cursor = listOf("updated_at")

        // Schema without CDC deletion column
        val schemaWithoutCdc =
            ObjectType(
                properties =
                    linkedMapOf(
                        "id" to FieldType(StringType, nullable = false),
                        "name" to FieldType(StringType, nullable = true),
                        "updated_at" to FieldType(TimestampTypeWithTimezone, nullable = true)
                    )
            )

        val stream =
            mockk<DestinationStream> {
                every { importType } returns
                    Dedupe(
                        primaryKey = primaryKey,
                        cursor = cursor,
                    )
                every { schema } returns schemaWithoutCdc
            }

        val columnNameMapping =
            ColumnNameMapping(mapOf("id" to "id", "name" to "name", "updated_at" to "updated_at"))
        val sourceTableName = TableName(namespace = "test_ns", name = "source")
        val targetTableName = TableName(namespace = "test_ns", name = "target")

        every { columnUtils.getFormattedColumnNames(any(), columnNameMapping, any()) } returns
            listOf(
                    "id",
                    "name",
                    "updated_at",
                )
                .map { it.quote() } + DEFAULT_COLUMNS.map { it.columnName.quote() }
        every { columnUtils.formatColumnName(any()) } answers { firstArg<String>() }

        val sql =
            snowflakeDirectLoadSqlGenerator.upsertTable(
                stream = stream,
                columnNameMapping = columnNameMapping,
                sourceTableName = sourceTableName,
                targetTableName = targetTableName,
            )

        // Should NOT include any CDC-related clauses
        assertFalse(sql.contains("_ab_cdc_deleted_at"))
        assertFalse(sql.contains("THEN DELETE"))
        assertTrue(sql.contains("WHEN NOT MATCHED THEN INSERT"))
    }

    @Test
    fun testGenerateUpsertTableWithNoCursor() {
        // Test upsert with no cursor field
        val primaryKey = listOf(listOf("id"))

        val schemaWithoutCursor =
            ObjectType(
                properties =
                    linkedMapOf(
                        "id" to FieldType(StringType, nullable = false),
                        "name" to FieldType(StringType, nullable = true)
                    )
            )

        val stream =
            mockk<DestinationStream> {
                every { importType } returns
                    Dedupe(
                        primaryKey = primaryKey,
                        cursor = emptyList(), // No cursor
                    )
                every { schema } returns schemaWithoutCursor
            }

        val columnNameMapping = ColumnNameMapping(mapOf("id" to "id", "name" to "name"))
        val sourceTableName = TableName(namespace = "test_ns", name = "source")
        val targetTableName = TableName(namespace = "test_ns", name = "target")

        every { columnUtils.getFormattedColumnNames(any(), columnNameMapping, any()) } returns
            listOf(
                    "id",
                    "name",
                    CDC_DELETED_AT_COLUMN.toSnowflakeCompatibleName(),
                )
                .map { it.quote() } + DEFAULT_COLUMNS.map { it.columnName.quote() }
        every { columnUtils.formatColumnName(any()) } answers { firstArg<String>() }

        val sql =
            snowflakeDirectLoadSqlGenerator.upsertTable(
                stream = stream,
                columnNameMapping = columnNameMapping,
                sourceTableName = sourceTableName,
                targetTableName = targetTableName,
            )

        // Should use only _airbyte_extracted_at for comparison when no cursor
        assert(
            sql.contains(
                "target_table.${COLUMN_NAME_AB_EXTRACTED_AT.toSnowflakeCompatibleName().quote()} < new_record.${COLUMN_NAME_AB_EXTRACTED_AT.toSnowflakeCompatibleName().quote()}"
            )
        )
        assert(!sql.contains("target_table.${QUOTE}cursor${QUOTE}")) // No cursor field reference
    }

    @Test
    fun testGenerateUpsertTableWithoutPrimaryKeyThrowsException() {
        // Test that upsert without primary key throws an exception
        val stream =
            mockk<DestinationStream> {
                every { importType } returns
                    Dedupe(
                        primaryKey = emptyList(), // No primary key
                        cursor = listOf("updated_at"),
                    )
                every { schema } returns StringType
            }

        val columnNameMapping = ColumnNameMapping(emptyMap())
        val sourceTableName = TableName(namespace = "test_ns", name = "source")
        val targetTableName = TableName(namespace = "test_ns", name = "target")

        val exception =
            assertThrows(IllegalArgumentException::class.java) {
                snowflakeDirectLoadSqlGenerator.upsertTable(
                    stream = stream,
                    columnNameMapping = columnNameMapping,
                    sourceTableName = sourceTableName,
                    targetTableName = targetTableName,
                )
            }

        assertEquals("Cannot perform upsert without primary key", exception.message)
    }

    @Test
    fun testGenerateSwapTable() {
        val sourceTableName = TableName(namespace = "namespace", name = "source")
        val targetTableName = TableName(namespace = "namespace", name = "target")
        val sql = snowflakeDirectLoadSqlGenerator.swapTableWith(sourceTableName, targetTableName)
        assertEquals(
            "ALTER TABLE ${snowflakeSqlNameUtils.fullyQualifiedName(sourceTableName)} SWAP WITH ${snowflakeSqlNameUtils.fullyQualifiedName(targetTableName)}",
            sql
        )
    }

    @Test
    fun testAlterTable() {
        val uuid = UUID.randomUUID()
        every { uuidGenerator.v4() } returns uuid
        val tableName = TableName(namespace = "namespace", name = "name")
        val addedColumns = mapOf("COL1" to ColumnType("TEXT", true))
        val deletedColumns = mapOf("COL2" to ColumnType("TEXT", true))
        val modifiedColumns =
            mapOf("COL3" to ColumnTypeChange(ColumnType("NUMBER", true), ColumnType("TEXT", true)))
        val sql =
            snowflakeDirectLoadSqlGenerator.alterTable(
                tableName,
                addedColumns,
                deletedColumns,
                modifiedColumns
            )
        val expectedTableName =
            "${snowflakeConfiguration.database.toSnowflakeCompatibleName().quote()}.${tableName.namespace.quote()}.${tableName.name.quote()}"

        assertEquals(
            setOf(
                """ALTER TABLE $expectedTableName ADD COLUMN "COL1" TEXT;""",
                """ALTER TABLE $expectedTableName DROP COLUMN "COL2";""",
                """ALTER TABLE $expectedTableName ADD COLUMN "COL3_${uuid}" TEXT;""",
                """UPDATE $expectedTableName SET "COL3_${uuid}" = CAST("COL3" AS TEXT);""",
                """
                ALTER TABLE $expectedTableName
                RENAME COLUMN "COL3" TO "COL3_${uuid}_backup";""".trimIndent(),
                """
                ALTER TABLE $expectedTableName
                RENAME COLUMN "COL3_${uuid}" TO "COL3";""".trimIndent(),
                """ALTER TABLE $expectedTableName DROP COLUMN "COL3_${uuid}_backup";"""
            ),
            sql
        )
    }

    @Test
    fun testDescribeTable() {
        val schemaName = "namespace"
        val tableName = "name"
        val sql = snowflakeDirectLoadSqlGenerator.describeTable(schemaName, tableName)
        val expectedTableName =
            "${snowflakeConfiguration.database.toSnowflakeCompatibleName().quote()}.${schemaName.quote()}.${tableName.quote()}"

        assertEquals("""DESCRIBE TABLE $expectedTableName""", sql)
    }

    @Test
    fun testRenameTable() {
        val sourceTableName = TableName(namespace = "namespace", name = "old_name")
        val targetTableName = TableName(namespace = "namespace", name = "new_name")
        val sql = snowflakeDirectLoadSqlGenerator.renameTable(sourceTableName, targetTableName)
        val expectedSourceTableName =
            "${snowflakeConfiguration.database.toSnowflakeCompatibleName().quote()}.${sourceTableName.namespace.quote()}.${sourceTableName.name.quote()}"
        val expectedTargetTableName =
            "${snowflakeConfiguration.database.toSnowflakeCompatibleName().quote()}.${targetTableName.namespace.quote()}.${targetTableName.name.quote()}"
        val expectedSql =
            """
            ALTER TABLE $expectedSourceTableName RENAME TO $expectedTargetTableName
        """.trimIndent()

        assertEquals(expectedSql, sql)
    }

    @Test
    fun testRenameTableWithSpecialCharacters() {
        val sourceTableName = TableName(namespace = "namespace", name = "table-with-dashes")
        val targetTableName = TableName(namespace = "namespace", name = "table_with_underscores")
        val sql = snowflakeDirectLoadSqlGenerator.renameTable(sourceTableName, targetTableName)
        val expectedSourceTableName =
            "${snowflakeConfiguration.database.toSnowflakeCompatibleName().quote()}.${sourceTableName.namespace.quote()}.${sourceTableName.name.quote()}"
        val expectedTargetTableName =
            "${snowflakeConfiguration.database.toSnowflakeCompatibleName().quote()}.${targetTableName.namespace.quote()}.${targetTableName.name.quote()}"
        val expectedSql =
            """
            ALTER TABLE $expectedSourceTableName RENAME TO $expectedTargetTableName
        """.trimIndent()

        assertEquals(expectedSql, sql)
    }

    @Test
    fun testCreateTableWithSQLInjectionAttemptInTableName() {
        val tableName =
            TableName(namespace = "namespace", name = "table$QUOTE; DROP TABLE users; --")
        val stream = mockk<DestinationStream>(relaxed = true)
        val columnNameMapping = mockk<ColumnNameMapping>(relaxed = true)

        every { columnUtils.columnsAndTypes(any(), columnNameMapping) } returns emptyList()

        val sql =
            snowflakeDirectLoadSqlGenerator.createTable(stream, tableName, columnNameMapping, false)
        val expectedTableName =
            "${snowflakeConfiguration.database.toSnowflakeCompatibleName().quote()}.${tableName.namespace.quote()}.${tableName.name.quote()}"
        val expectedSql =
            """
            CREATE TABLE $expectedTableName (
                
            )
        """.trimIndent()

        // The dangerous SQL characters should be sanitized to underscores
        assertEquals(expectedSql, sql)
    }

    @Test
    fun testCreateTableWithSQLInjectionAttemptInNamespace() {
        val tableName =
            TableName(namespace = "namespace$QUOTE; DROP SCHEMA test; --", name = "table")
        val stream = mockk<DestinationStream>(relaxed = true)
        val columnNameMapping = mockk<ColumnNameMapping>(relaxed = true)

        every { columnUtils.columnsAndTypes(any(), columnNameMapping) } returns emptyList()

        val sql =
            snowflakeDirectLoadSqlGenerator.createTable(stream, tableName, columnNameMapping, false)
        val expectedTableName =
            "${snowflakeConfiguration.database.toSnowflakeCompatibleName().quote()}.${tableName.namespace.quote()}.${tableName.name.quote()}"
        val expectedSql =
            """
            CREATE TABLE $expectedTableName (
                
            )
        """.trimIndent()

        // The dangerous SQL characters should be sanitized to underscores
        assertEquals(expectedSql, sql)
    }

    @Test
    fun testCreateTableWithReservedKeywordsAsNames() {
        // Test with Snowflake reserved keywords as table/namespace names
        val tableName = TableName(namespace = "SELECT", name = "WHERE")
        val stream = mockk<DestinationStream>(relaxed = true)
        val columnNameMapping = mockk<ColumnNameMapping>(relaxed = true)

        every { columnUtils.columnsAndTypes(any(), columnNameMapping) } returns emptyList()

        val sql =
            snowflakeDirectLoadSqlGenerator.createTable(stream, tableName, columnNameMapping, false)
        val expectedTableName =
            "${snowflakeConfiguration.database.toSnowflakeCompatibleName().quote()}.${tableName.namespace.quote()}.${tableName.name.quote()}"

        // Reserved keywords should be properly quoted
        assertEquals("CREATE TABLE $expectedTableName (\n    \n)", sql)
    }
}
