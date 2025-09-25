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
import io.airbyte.cdk.load.util.UUIDGenerator
import io.airbyte.integrations.destination.snowflake.db.ColumnDefinition
import io.airbyte.integrations.destination.snowflake.spec.CdcDeletionMode
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.write.load.CSV_FORMAT
import io.mockk.every
import io.mockk.mockk
import java.util.UUID
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
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
        columnUtils = mockk()
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
            "SELECT COUNT(*) AS \"total\" FROM ${snowflakeSqlNameUtils.fullyQualifiedName(tableName)}",
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
                "\"$it\""
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

        every { columnUtils.columnsAndTypes(any(), columnNameMapping) } returns DEFAULT_COLUMNS

        val expected =
            """
            MERGE INTO "test_database"."namespace"."destination" AS target_table
            USING (
                          WITH records AS (
              SELECT
                "_airbyte_raw_id",
"_airbyte_extracted_at",
"_airbyte_meta",
"_airbyte_generation_id"
              FROM "test_database"."namespace"."source"
            ), numbered_rows AS (
              SELECT *, ROW_NUMBER() OVER (
                PARTITION BY "primaryKey" ORDER BY "cursor" DESC NULLS LAST, "_airbyte_extracted_at" DESC
              ) AS row_number
              FROM records
            )
            SELECT "_airbyte_raw_id",
"_airbyte_extracted_at",
"_airbyte_meta",
"_airbyte_generation_id"
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
              "_airbyte_raw_id" = new_record."_airbyte_raw_id",
"_airbyte_extracted_at" = new_record."_airbyte_extracted_at",
"_airbyte_meta" = new_record."_airbyte_meta",
"_airbyte_generation_id" = new_record."_airbyte_generation_id"
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
        assertEquals(
            "DROP TABLE IF EXISTS ${snowflakeSqlNameUtils.fullyQualifiedName(tableName)}",
            sql
        )
    }

    @Test
    fun testGenerateDropStage() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val sql = snowflakeDirectLoadSqlGenerator.dropStage(tableName)
        assertEquals(
            "DROP STAGE IF EXISTS ${snowflakeSqlNameUtils.fullyQualifiedStageName(tableName)}",
            sql
        )
    }

    @Test
    fun testGenerateGenerationIdQuery() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val sql = snowflakeDirectLoadSqlGenerator.getGenerationId(tableName = tableName)
        assertEquals(
            "SELECT \"$COLUMN_NAME_AB_GENERATION_ID\"\nFROM ${snowflakeSqlNameUtils.fullyQualifiedName(tableName)} \nLIMIT 1",
            sql
        )
    }

    @Test
    fun testGenerateCreateFileFormat() {
        val namespace = "test-namespace"
        val fileFormatName = snowflakeSqlNameUtils.fullyQualifiedFormatName(namespace)
        val expected =
            """
            CREATE OR REPLACE FILE FORMAT $fileFormatName
            TYPE = 'CSV'
            FIELD_DELIMITER = '${CSV_FORMAT.delimiterString}'
            RECORD_DELIMITER = '${CSV_FORMAT.recordSeparator}'
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
        val stagingTableName = snowflakeSqlNameUtils.fullyQualifiedStageName(tableName)
        val fileFormat = snowflakeSqlNameUtils.fullyQualifiedFormatName(tableName.namespace)
        val sql = snowflakeDirectLoadSqlGenerator.createSnowflakeStage(tableName)
        assertEquals(
            "CREATE OR REPLACE STAGE $stagingTableName\n    FILE_FORMAT = $fileFormat;",
            sql
        )
    }

    @Test
    fun testGeneratePutInStage() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val tempFilePath = "/some/file/path.csv"
        val stagingTableName = snowflakeSqlNameUtils.fullyQualifiedStageName(tableName)
        val sql = snowflakeDirectLoadSqlGenerator.putInStage(tableName, tempFilePath)
        assertEquals(
            "PUT 'file://$tempFilePath' @$stagingTableName\nAUTO_COMPRESS = TRUE\nOVERWRITE = TRUE",
            sql
        )
    }

    @Test
    fun testGenerateCopyFromStage() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val targetTableName = snowflakeSqlNameUtils.fullyQualifiedName(tableName)
        val stagingTableName = snowflakeSqlNameUtils.fullyQualifiedStageName(tableName)
        val fileFormat = snowflakeSqlNameUtils.fullyQualifiedFormatName(tableName.namespace)
        val sql = snowflakeDirectLoadSqlGenerator.copyFromStage(tableName)
        assertEquals(
            "COPY INTO $targetTableName\nFROM @$stagingTableName\nFILE_FORMAT = $fileFormat\nON_ERROR = 'ABORT_STATEMENT'\nPURGE = TRUE;",
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
            "ALTER TABLE ${snowflakeSqlNameUtils.fullyQualifiedName(sourceTableName)} SWAP WITH ${snowflakeSqlNameUtils.fullyQualifiedName(targetTableName)}",
            sql
        )
    }

    @Test
    fun testAlterTable() {
        val uuid = UUID.randomUUID()
        every { uuidGenerator.v4() } returns uuid
        val tableName = TableName(namespace = "namespace", name = "name")
        val addedColumns = setOf(ColumnDefinition("col1", "TEXT", false))
        val deletedColumns = setOf(ColumnDefinition("col2", "TEXT", false))
        val modifiedColumns = setOf(ColumnDefinition("col3", "TEXT", false))
        val sql =
            snowflakeDirectLoadSqlGenerator.alterTable(
                tableName,
                addedColumns,
                deletedColumns,
                modifiedColumns
            )

        assertEquals(
            setOf(
                """ALTER TABLE "test_database"."namespace"."name" ADD COLUMN "col1" TEXT;""",
                """ALTER TABLE "test_database"."namespace"."name" DROP COLUMN "col2";""",
                """ALTER TABLE "test_database"."namespace"."name" ADD COLUMN "col3_${uuid}" TEXT;""",
                """UPDATE "test_database"."namespace"."name" SET "col3_${uuid}" = CAST("col3" AS TEXT);""",
                """ALTER TABLE "test_database"."namespace"."name"
                RENAME COLUMN "col3" TO "col3_${uuid}_backup";""".trimIndent(),
                """ALTER TABLE "test_database"."namespace"."name"
                RENAME COLUMN "col3_${uuid}" TO "col3";""".trimIndent(),
                """ALTER TABLE "test_database"."namespace"."name" DROP COLUMN "col3_${uuid}_backup";"""
            ),
            sql
        )
    }

    @Test
    fun testDescribeTable() {
        val schemaName = "namespace"
        val tableName = "name"
        val sql = snowflakeDirectLoadSqlGenerator.describeTable(schemaName, tableName)

        assertEquals("""DESCRIBE TABLE "test_database"."namespace"."name"""", sql)
    }

    @Test
    fun testRenameTable() {
        val sourceTableName = TableName(namespace = "namespace", name = "old_name")
        val targetTableName = TableName(namespace = "namespace", name = "new_name")
        val sql = snowflakeDirectLoadSqlGenerator.renameTable(sourceTableName, targetTableName)

        assertEquals(
            """ALTER TABLE "test_database"."namespace"."old_name" RENAME TO "test_database"."namespace"."new_name"""",
            sql
        )
    }

    @Test
    fun testRenameTableWithSpecialCharacters() {
        val sourceTableName = TableName(namespace = "namespace", name = "table-with-dashes")
        val targetTableName = TableName(namespace = "namespace", name = "table_with_underscores")
        val sql = snowflakeDirectLoadSqlGenerator.renameTable(sourceTableName, targetTableName)

        assertEquals(
            "ALTER TABLE \"test_database\".\"namespace\".\"table_with_dashes\" RENAME TO \"test_database\".\"namespace\".\"table_with_underscores\"",
            sql
        )
    }

    @Test
    fun testDescribeTableWithSpecialCharacters() {
        val schemaName = "namespace-with-dash"
        val tableName = "table.with.dots"
        val sql = snowflakeDirectLoadSqlGenerator.describeTable(schemaName, tableName)

        assertEquals(
            "DESCRIBE TABLE \"test_database\".\"namespace_with_dash\".\"table_with_dots\"",
            sql
        )
    }

    @Test
    fun testCreateTableWithSQLInjectionAttemptInTableName() {
        val tableName = TableName(namespace = "namespace", name = "table\"; DROP TABLE users; --")
        val stream = mockk<DestinationStream>(relaxed = true)
        val columnNameMapping = mockk<ColumnNameMapping>(relaxed = true)

        every { columnUtils.columnsAndTypes(any(), columnNameMapping) } returns emptyList()

        val sql =
            snowflakeDirectLoadSqlGenerator.createTable(stream, tableName, columnNameMapping, false)

        // The dangerous SQL characters should be sanitized to underscores
        assertEquals(
            "CREATE TABLE \"test_database\".\"namespace\".\"table___DROP_TABLE_users____\" (\n    \n)",
            sql
        )
    }

    @Test
    fun testCreateTableWithSQLInjectionAttemptInNamespace() {
        val tableName = TableName(namespace = "namespace\"; DROP SCHEMA test; --", name = "table")
        val stream = mockk<DestinationStream>(relaxed = true)
        val columnNameMapping = mockk<ColumnNameMapping>(relaxed = true)

        every { columnUtils.columnsAndTypes(any(), columnNameMapping) } returns emptyList()

        val sql =
            snowflakeDirectLoadSqlGenerator.createTable(stream, tableName, columnNameMapping, false)

        // The dangerous SQL characters should be sanitized to underscores
        assertEquals(
            "CREATE TABLE \"test_database\".\"namespace___DROP_SCHEMA_test____\".\"table\" (\n    \n)",
            sql
        )
    }

    @Test
    fun testDropTableWithSQLInjectionAttempt() {
        val tableName =
            TableName(namespace = "namespace", name = "table'; DELETE FROM users WHERE '1'='1")
        val sql = snowflakeDirectLoadSqlGenerator.dropTable(tableName)

        // The dangerous SQL characters should be sanitized to underscores
        assertEquals(
            """DROP TABLE IF EXISTS "test_database"."namespace"."table___DELETE_FROM_users_WHERE__1___1"""",
            sql
        )
    }

    @Test
    fun testRenameTableWithSQLInjectionAttempt() {
        val sourceTableName = TableName(namespace = "namespace", name = "table")
        val targetTableName =
            TableName(namespace = "namespace", name = "new_table\"; DROP TABLE important; --")
        val sql = snowflakeDirectLoadSqlGenerator.renameTable(sourceTableName, targetTableName)

        // The dangerous SQL characters should be sanitized to underscores
        assertEquals(
            """ALTER TABLE "test_database"."namespace"."table" RENAME TO "test_database"."namespace"."new_table___DROP_TABLE_important____"""",
            sql
        )
    }

    @Test
    fun testCountTableWithSQLInjectionAttempt() {
        val tableName =
            TableName(
                namespace = "namespace",
                name = "table\" UNION SELECT * FROM sensitive_data --"
            )
        val sql = snowflakeDirectLoadSqlGenerator.countTable(tableName)

        // The dangerous SQL characters should be sanitized to underscores
        assertEquals(
            """SELECT COUNT(*) AS "total" FROM "test_database"."namespace"."table__UNION_SELECT___FROM_sensitive_data___"""",
            sql
        )
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

        // Reserved keywords should be properly quoted
        assertEquals("CREATE TABLE \"test_database\".\"SELECT\".\"WHERE\" (\n    \n)", sql)
    }

    @Test
    fun testDropTableWithReservedKeywords() {
        val tableName = TableName(namespace = "GROUP", name = "ORDER")
        val sql = snowflakeDirectLoadSqlGenerator.dropTable(tableName)

        // Reserved keywords should be properly quoted
        assertEquals("""DROP TABLE IF EXISTS "test_database"."GROUP"."ORDER"""", sql)
    }

    @Test
    fun testRenameTableWithReservedKeywords() {
        val sourceTableName = TableName(namespace = "FROM", name = "JOIN")
        val targetTableName = TableName(namespace = "FROM", name = "UNION")
        val sql = snowflakeDirectLoadSqlGenerator.renameTable(sourceTableName, targetTableName)

        // Reserved keywords should be properly quoted
        assertEquals(
            """ALTER TABLE "test_database"."FROM"."JOIN" RENAME TO "test_database"."FROM"."UNION"""",
            sql
        )
    }

    @Test
    fun testCreateNamespaceWithReservedKeyword() {
        val sql = snowflakeDirectLoadSqlGenerator.createNamespace("TABLE")

        // Reserved keyword should be properly quoted
        assertEquals("""CREATE SCHEMA IF NOT EXISTS "test_database"."TABLE"""", sql)
    }

    @Test
    fun testDescribeTableWithReservedKeywords() {
        val schemaName = "DATABASE"
        val tableName = "SCHEMA"
        val sql = snowflakeDirectLoadSqlGenerator.describeTable(schemaName, tableName)

        // Reserved keywords should be properly quoted
        assertEquals("""DESCRIBE TABLE "test_database"."DATABASE"."SCHEMA"""", sql)
    }
}
