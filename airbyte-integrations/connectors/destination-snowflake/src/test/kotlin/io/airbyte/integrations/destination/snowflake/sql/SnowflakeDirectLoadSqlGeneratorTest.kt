/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.sql

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.orchestration.db.CDC_DELETED_AT_COLUMN
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.CdcDeletionMode
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class SnowflakeDirectLoadSqlGeneratorTest {

    private lateinit var columnUtils: SnowflakeColumnUtils
    private lateinit var snowflakeDirectLoadSqlGenerator: SnowflakeDirectLoadSqlGenerator

    @BeforeEach
    fun setUp() {
        columnUtils = mockk()
        snowflakeDirectLoadSqlGenerator =
            SnowflakeDirectLoadSqlGenerator(
                columnUtils = columnUtils,
                cdcDeletionMode = CdcDeletionMode.HARD_DELETE,
            )
    }

    @Test
    fun testGenerateCountTableQuery() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val sql = snowflakeDirectLoadSqlGenerator.countTable(tableName)
        assertEquals(
            "SELECT COUNT(*) AS \"total\" FROM ${tableName.toPrettyString(quote=QUOTE)}",
            sql
        )
    }

    @Test
    fun testGenerateNamespaceStatement() {
        val namespace = "namespace"
        val sql = snowflakeDirectLoadSqlGenerator.createNamespace(namespace)
        assertEquals("CREATE SCHEMA IF NOT EXISTS \"$namespace\"", sql)
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
            "CREATE OR REPLACE TABLE ${tableName.toPrettyString(quote=QUOTE)} (\n    $columnAndType\n)",
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
            "CREATE TABLE ${tableName.toPrettyString(quote=QUOTE)} (\n    $columnAndType\n)",
            sql
        )
    }

    @Test
    fun testGenerateShowColumns() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val sql = snowflakeDirectLoadSqlGenerator.showColumns(tableName)
        assertEquals("SHOW COLUMNS IN TABLE ${tableName.toPrettyString(quote=QUOTE)};", sql)
    }

    @Test
    fun testGenerateCopyTable() {
        val columnName = "column-name"
        val mappedColumnName = "mapped-column-name"
        val columns = mapOf(columnName to mappedColumnName)
        val columnNameMapping = ColumnNameMapping(columns)
        val columnNames =
            DEFAULT_COLUMNS.map { it.columnName }.joinToString(",") { "\"$it\"" } +
                "\"$mappedColumnName\""
        val sourceTableName = TableName(namespace = "namespace", name = "source")
        val destinationTableName = TableName(namespace = "namespace", name = "destination")
        val expected =
            """
            INSERT INTO ${destinationTableName.toPrettyString(quote = QUOTE)}
            (
                $columnNames
            )
            SELECT
                $columnNames
            FROM ${sourceTableName.toPrettyString(quote=QUOTE)}
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

        every { columnUtils.columnsAndTypes(any(), columnNameMapping) } returns DEFAULT_COLUMNS

        val expected =
            """
            MERGE INTO "namespace"."destination" AS target_table
            USING (
              WITH records AS (
  SELECT
    
  FROM "namespace"."source"
), numbered_rows AS (
  SELECT *, ROW_NUMBER() OVER (
    PARTITION BY "primaryKey" ORDER BY "cursor" DESC NULLS LAST, "_airbyte_extracted_at" DESC
  ) AS row_number
  FROM records
)
SELECT 
FROM numbered_rows
WHERE row_number = 1
            ) AS new_record
            ON (target_table."primaryKey" = new_record."primaryKey" OR (target_table."primaryKey" IS NULL AND new_record."primaryKey" IS NULL))
            WHEN MATCHED AND (
  target_table."cursor" < new_record."cursor"
  OR (target_table."cursor" = new_record."cursor" AND target_table."_airbyte_extracted_at" < new_record."_airbyte_extracted_at")
  OR (target_table."cursor" IS NULL AND new_record."cursor" IS NULL AND target_table."_airbyte_extracted_at" < new_record."_airbyte_extracted_at")
  OR (target_table."cursor" IS NULL AND new_record."cursor" IS NOT NULL)
) THEN UPDATE SET
              
            WHEN NOT MATCHED THEN INSERT (
              "_airbyte_raw_id",
"_airbyte_extracted_at",
"_airbyte_meta",
"_airbyte_generation_id"
            ) VALUES (
              new_record."_airbyte_raw_id",
new_record."_airbyte_extracted_at",
new_record."_airbyte_meta",
new_record."_airbyte_generation_id"
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
        assertEquals("DROP TABLE IF EXISTS ${tableName.toPrettyString(QUOTE)}", sql)
    }

    @Test
    fun testGenerateDropStage() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val sql = snowflakeDirectLoadSqlGenerator.dropStage(tableName)
        assertEquals(
            "DROP STAGE IF EXISTS \"${tableName.namespace}\".\"airbyte_stage_${tableName.name}\"",
            sql
        )
    }

    @Test
    fun testGenerateGenerationIdQuery() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val sql = snowflakeDirectLoadSqlGenerator.getGenerationId(tableName = tableName)
        assertEquals(
            "SELECT \"$COLUMN_NAME_AB_GENERATION_ID\" \nFROM ${tableName.toPrettyString(QUOTE)} \nLIMIT 1",
            sql
        )
    }

    @Test
    fun testGenerateGenerationIdQueryWithAlias() {
        val alias = "test-alias"
        val tableName = TableName(namespace = "namespace", name = "name")
        val sql =
            snowflakeDirectLoadSqlGenerator.getGenerationId(tableName = tableName, alias = alias)
        assertEquals(
            "SELECT \"$COLUMN_NAME_AB_GENERATION_ID\" AS $alias \nFROM ${tableName.toPrettyString(QUOTE)} \nLIMIT 1",
            sql
        )
    }

    @Test
    fun testGenerateCreateFileFormat() {
        val namespace = "test-namespace"
        val expected =
            """
            CREATE OR REPLACE FILE FORMAT "${namespace.toSnowflakeCompatibleName()}".$STAGE_FORMAT_NAME
            TYPE = 'CSV'
            FIELD_DELIMITER = '$CSV_FIELD_DELIMITER'
            FIELD_OPTIONALLY_ENCLOSED_BY = '"'
            TRIM_SPACE = TRUE
            ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE
            REPLACE_INVALID_CHARACTERS = TRUE
        """.trimIndent()
        val sql = snowflakeDirectLoadSqlGenerator.createFileFormat(namespace)
        assertEquals(expected, sql)
    }

    @Test
    fun testGenerateCreateStage() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val sql = snowflakeDirectLoadSqlGenerator.createSnowflakeStage(tableName)
        assertEquals(
            "CREATE OR REPLACE STAGE ${buildSnowflakeStageName(tableName)}\n    FILE_FORMAT = $STAGE_FORMAT_NAME;",
            sql
        )
    }

    @Test
    fun testGeneratePutInStage() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val tempFilePath = "/some/file/path.csv"
        val sql = snowflakeDirectLoadSqlGenerator.putInStage(tableName, tempFilePath)
        assertEquals(
            "PUT 'file://$tempFilePath' @${buildSnowflakeStageName(tableName)}\nAUTO_COMPRESS = TRUE\nOVERWRITE = TRUE",
            sql
        )
    }

    @Test
    fun testGenerateCopyFromStage() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val sql = snowflakeDirectLoadSqlGenerator.copyFromStage(tableName)
        assertEquals(
            "COPY INTO ${tableName.toPrettyString(quote=QUOTE)}\nFROM @${buildSnowflakeStageName(tableName)}\nFILE_FORMAT = $STAGE_FORMAT_NAME\nON_ERROR = 'ABORT_STATEMENT'",
            sql
        )
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

        every { columnUtils.columnsAndTypes(any(), columnNameMapping) } returns
            listOf(
                ColumnAndType("id", "VARCHAR"),
                ColumnAndType("name", "VARCHAR"),
                ColumnAndType("updated_at", "TIMESTAMP_TZ"),
                ColumnAndType("_ab_cdc_deleted_at", "TIMESTAMP_TZ")
            ) + DEFAULT_COLUMNS

        val sql =
            snowflakeDirectLoadSqlGenerator.upsertTable(
                stream = stream,
                columnNameMapping = columnNameMapping,
                sourceTableName = sourceTableName,
                targetTableName = targetTableName,
            )

        // Should include the DELETE clause and skip insert clause
        assert(sql.contains("WHEN MATCHED AND new_record.\"_ab_cdc_deleted_at\" IS NOT NULL"))
        assert(sql.contains("THEN DELETE"))
        assert(
            sql.contains(
                "WHEN NOT MATCHED AND new_record.\"_ab_cdc_deleted_at\" IS NULL THEN INSERT"
            )
        )
    }

    @Test
    fun testGenerateUpsertTableWithCdcSoftDelete() {
        // Test with CDC soft delete mode - should NOT add delete clauses
        val softDeleteGenerator =
            SnowflakeDirectLoadSqlGenerator(
                columnUtils = columnUtils,
                cdcDeletionMode = CdcDeletionMode.SOFT_DELETE,
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

        every { columnUtils.columnsAndTypes(any(), columnNameMapping) } returns
            listOf(
                ColumnAndType("id", "VARCHAR"),
                ColumnAndType("name", "VARCHAR"),
                ColumnAndType("updated_at", "TIMESTAMP_TZ"),
                ColumnAndType("_ab_cdc_deleted_at", "TIMESTAMP_TZ")
            ) + DEFAULT_COLUMNS

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
        assert(!sql.contains("AND new_record.\"_ab_cdc_deleted_at\" IS NULL"))
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

        every { columnUtils.columnsAndTypes(any(), columnNameMapping) } returns
            listOf(
                ColumnAndType("id", "VARCHAR"),
                ColumnAndType("name", "VARCHAR"),
                ColumnAndType("updated_at", "TIMESTAMP_TZ")
            ) + DEFAULT_COLUMNS

        val sql =
            snowflakeDirectLoadSqlGenerator.upsertTable(
                stream = stream,
                columnNameMapping = columnNameMapping,
                sourceTableName = sourceTableName,
                targetTableName = targetTableName,
            )

        // Should NOT include any CDC-related clauses
        assert(!sql.contains("_ab_cdc_deleted_at"))
        assert(!sql.contains("THEN DELETE"))
        assert(sql.contains("WHEN NOT MATCHED THEN INSERT"))
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

        every { columnUtils.columnsAndTypes(any(), columnNameMapping) } returns
            listOf(ColumnAndType("id", "VARCHAR"), ColumnAndType("name", "VARCHAR")) +
                DEFAULT_COLUMNS

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
                "target_table.\"_airbyte_extracted_at\" < new_record.\"_airbyte_extracted_at\""
            )
        )
        assert(!sql.contains("target_table.\"cursor\"")) // No cursor field reference
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
            "ALTER TABLE ${sourceTableName.toPrettyString(quote = QUOTE)} SWAP WITH ${targetTableName.toPrettyString(quote = QUOTE)};",
            sql
        )
    }
}
