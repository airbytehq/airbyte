/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.sql

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.ColumnTypeChange
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.cdk.load.util.UUIDGenerator
import io.airbyte.integrations.destination.snowflake.schema.SnowflakeColumnManager
import io.airbyte.integrations.destination.snowflake.schema.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.CdcDeletionMode
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.write.load.CSV_FIELD_SEPARATOR
import io.airbyte.integrations.destination.snowflake.write.load.CSV_LINE_DELIMITER
import io.mockk.every
import io.mockk.mockk
import java.util.UUID
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

/** TODO: These tests are somewhat dubious. */
internal class SnowflakeDirectLoadSqlGeneratorTest {

    private lateinit var snowflakeDirectLoadSqlGenerator: SnowflakeDirectLoadSqlGenerator
    private val uuidGenerator: UUIDGenerator = mockk()
    private val snowflakeConfiguration: SnowflakeConfiguration = mockk()
    private val snowflakeColumnManager: SnowflakeColumnManager = mockk()

    @BeforeEach
    fun setUp() {
        every { snowflakeConfiguration.cdcDeletionMode } returns CdcDeletionMode.HARD_DELETE
        every { snowflakeConfiguration.database } returns "test-database"
        every { snowflakeConfiguration.legacyRawTablesOnly } returns false

        every { snowflakeColumnManager.getMetaColumns() } returns
            linkedMapOf(
                SNOWFLAKE_AB_RAW_ID to ColumnType("VARCHAR", false),
                SNOWFLAKE_AB_EXTRACTED_AT to ColumnType("TIMESTAMP_TZ", false),
                SNOWFLAKE_AB_META to ColumnType("VARIANT", false),
                SNOWFLAKE_AB_GENERATION_ID to ColumnType("NUMBER", true),
            )

        every { snowflakeColumnManager.getGenerationIdColumnName() } returns
            SNOWFLAKE_AB_GENERATION_ID

        snowflakeDirectLoadSqlGenerator =
            SnowflakeDirectLoadSqlGenerator(
                uuidGenerator = uuidGenerator,
                config = snowflakeConfiguration,
                columnManager = snowflakeColumnManager,
            )
    }

    @Test
    fun testGenerateCountTableQuery() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val sql = snowflakeDirectLoadSqlGenerator.countTable(tableName)
        assertEquals(
            "SELECT COUNT(*) AS TOTAL FROM ${snowflakeDirectLoadSqlGenerator.fullyQualifiedName(tableName)}",
            sql
        )
    }

    @Test
    fun testGenerateNamespaceStatement() {
        val namespace = "namespace"
        val sql = snowflakeDirectLoadSqlGenerator.createNamespace(namespace)
        assertEquals(
            "CREATE SCHEMA IF NOT EXISTS ${snowflakeDirectLoadSqlGenerator.fullyQualifiedNamespace(namespace)}",
            sql
        )
    }

    @Test
    fun testGenerateCreateTableStatement() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val tableSchema =
            StreamTableSchema(
                tableNames = TableNames(finalTableName = tableName, tempTableName = tableName),
                columnSchema =
                    ColumnSchema(
                        inputToFinalColumnNames = mapOf("column" to "COLUMN_NAME"),
                        finalSchema = mapOf("COLUMN_NAME" to ColumnType("VARCHAR", false)),
                        inputSchema = mapOf("column" to FieldType(StringType, nullable = false))
                    ),
                importType = Append
            )

        val sql =
            snowflakeDirectLoadSqlGenerator.createTable(
                tableName = tableName,
                tableSchema = tableSchema,
                replace = true
            )

        // The expected SQL should match the exact format
        val expectedTableName = snowflakeDirectLoadSqlGenerator.fullyQualifiedName(tableName)
        val expectedSql =
            """
            CREATE OR REPLACE TABLE $expectedTableName (
                "_AIRBYTE_RAW_ID" VARCHAR NOT NULL,
                "_AIRBYTE_EXTRACTED_AT" TIMESTAMP_TZ NOT NULL,
                "_AIRBYTE_META" VARIANT NOT NULL,
                "_AIRBYTE_GENERATION_ID" NUMBER,
                "COLUMN_NAME" VARCHAR NOT NULL
            )
            """.trimIndent()
        assertEquals(expectedSql, sql)
    }

    @Test
    fun testGenerateCreateTableStatementNoReplace() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val tableSchema =
            StreamTableSchema(
                tableNames = TableNames(finalTableName = tableName, tempTableName = tableName),
                columnSchema =
                    ColumnSchema(
                        inputToFinalColumnNames = mapOf("column" to "COLUMN_NAME"),
                        finalSchema = mapOf("COLUMN_NAME" to ColumnType("VARCHAR", false)),
                        inputSchema = mapOf("column" to FieldType(StringType, nullable = false))
                    ),
                importType = Append
            )

        val sql =
            snowflakeDirectLoadSqlGenerator.createTable(
                tableName = tableName,
                tableSchema = tableSchema,
                replace = false
            )

        val expectedTableName = snowflakeDirectLoadSqlGenerator.fullyQualifiedName(tableName)
        val expectedSql =
            """
            CREATE TABLE $expectedTableName (
                "_AIRBYTE_RAW_ID" VARCHAR NOT NULL,
                "_AIRBYTE_EXTRACTED_AT" TIMESTAMP_TZ NOT NULL,
                "_AIRBYTE_META" VARIANT NOT NULL,
                "_AIRBYTE_GENERATION_ID" NUMBER,
                "COLUMN_NAME" VARCHAR NOT NULL
            )
            """.trimIndent()
        assertEquals(expectedSql, sql)
    }

    @Test
    fun testGenerateShowColumns() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val sql = snowflakeDirectLoadSqlGenerator.showColumns(tableName)
        assertEquals(
            "SHOW COLUMNS IN TABLE ${snowflakeDirectLoadSqlGenerator.fullyQualifiedName(tableName)}",
            sql
        )
    }

    @Test
    fun testGenerateCopyTable() {
        val columnNames =
            setOf(
                "_AIRBYTE_RAW_ID",
                "_AIRBYTE_EXTRACTED_AT",
                "_AIRBYTE_META",
                "_AIRBYTE_GENERATION_ID",
                "MAPPED_COLUMN_NAME"
            )
        val sourceTableName = TableName(namespace = "namespace", name = "source")
        val destinationTableName = TableName(namespace = "namespace", name = "destination")

        val sql =
            snowflakeDirectLoadSqlGenerator.copyTable(
                columnNames = columnNames,
                sourceTableName = sourceTableName,
                targetTableName = destinationTableName,
            )

        val columnList = columnNames.joinToString(", ") { "\"$it\"" }
        val expected =
            """
            INSERT INTO ${snowflakeDirectLoadSqlGenerator.fullyQualifiedName(destinationTableName)} 
            (
                $columnList
            )
            SELECT
                $columnList
            FROM ${snowflakeDirectLoadSqlGenerator.fullyQualifiedName(sourceTableName)}
            """.trimIndent()
        assertEquals(expected, sql)
    }

    @Test
    fun testGenerateDropTable() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val sql = snowflakeDirectLoadSqlGenerator.dropTable(tableName)
        assertEquals(
            "DROP TABLE IF EXISTS ${snowflakeDirectLoadSqlGenerator.fullyQualifiedName(tableName)}",
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
            FROM ${snowflakeDirectLoadSqlGenerator.fullyQualifiedName(tableName)}
            LIMIT 1
        """.trimIndent()
        assertEquals(expectedSql, sql)
    }

    @Test
    fun testGenerateCreateStage() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val stagingTableName = snowflakeDirectLoadSqlGenerator.fullyQualifiedStageName(tableName)
        val sql = snowflakeDirectLoadSqlGenerator.createSnowflakeStage(tableName)
        assertEquals("CREATE STAGE IF NOT EXISTS $stagingTableName", sql)
    }

    @Test
    fun testGeneratePutInStage() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val tempFilePath = "/some/file/path.csv"
        val stagingTableName = snowflakeDirectLoadSqlGenerator.fullyQualifiedStageName(tableName)
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
        val targetTableName = snowflakeDirectLoadSqlGenerator.fullyQualifiedName(tableName)
        val stagingTableName = snowflakeDirectLoadSqlGenerator.fullyQualifiedStageName(tableName)
        val sql = snowflakeDirectLoadSqlGenerator.copyFromStage(tableName, "test.csv.gz")
        val expectedSql =
            """
            |COPY INTO $targetTableName
            |FROM '@$stagingTableName'
            |FILE_FORMAT = (
            |    TYPE = 'CSV'
            |    COMPRESSION = GZIP
            |    FIELD_DELIMITER = '$CSV_FIELD_SEPARATOR'
            |    RECORD_DELIMITER = '$CSV_LINE_DELIMITER'
            |    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
            |    TRIM_SPACE = TRUE
            |    ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE
            |    REPLACE_INVALID_CHARACTERS = TRUE
            |    ESCAPE = NONE
            |    ESCAPE_UNENCLOSED_FIELD = NONE
            |)
            |ON_ERROR = 'ABORT_STATEMENT'
            |PURGE = TRUE
            |files = ('test.csv.gz')
        """.trimMargin()
        assertEquals(expectedSql, sql)
    }

    @Test
    fun testGenerateCopyFromStageWithColumnList() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val targetTableName = snowflakeDirectLoadSqlGenerator.fullyQualifiedName(tableName)
        val stagingTableName = snowflakeDirectLoadSqlGenerator.fullyQualifiedStageName(tableName)
        // Test with uppercase column names (schema mode)
        val schemaColumns =
            listOf(
                "_AIRBYTE_RAW_ID",
                "_AIRBYTE_EXTRACTED_AT",
                "_AIRBYTE_META",
                "_AIRBYTE_GENERATION_ID",
                "COL1",
                "COL2"
            )
        val sql =
            snowflakeDirectLoadSqlGenerator.copyFromStage(tableName, "test.csv.gz", schemaColumns)
        val expectedSql =
            """
            |COPY INTO $targetTableName("_AIRBYTE_RAW_ID", "_AIRBYTE_EXTRACTED_AT", "_AIRBYTE_META", "_AIRBYTE_GENERATION_ID", "COL1", "COL2")
            |FROM '@$stagingTableName'
            |FILE_FORMAT = (
            |    TYPE = 'CSV'
            |    COMPRESSION = GZIP
            |    FIELD_DELIMITER = '$CSV_FIELD_SEPARATOR'
            |    RECORD_DELIMITER = '$CSV_LINE_DELIMITER'
            |    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
            |    TRIM_SPACE = TRUE
            |    ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE
            |    REPLACE_INVALID_CHARACTERS = TRUE
            |    ESCAPE = NONE
            |    ESCAPE_UNENCLOSED_FIELD = NONE
            |)
            |ON_ERROR = 'ABORT_STATEMENT'
            |PURGE = TRUE
            |files = ('test.csv.gz')
        """.trimMargin()
        assertEquals(expectedSql, sql)
    }

    @Test
    fun testGenerateCopyFromStageWithRawModeColumns() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val targetTableName = snowflakeDirectLoadSqlGenerator.fullyQualifiedName(tableName)
        val stagingTableName = snowflakeDirectLoadSqlGenerator.fullyQualifiedStageName(tableName)
        // Test with lowercase column names (raw mode)
        val rawColumns =
            listOf(
                "_airbyte_raw_id",
                "_airbyte_extracted_at",
                "_airbyte_meta",
                "_airbyte_generation_id",
                "_airbyte_loaded_at",
                "_airbyte_data"
            )
        val sql =
            snowflakeDirectLoadSqlGenerator.copyFromStage(tableName, "test.csv.gz", rawColumns)
        val expectedSql =
            """
            |COPY INTO $targetTableName("_airbyte_raw_id", "_airbyte_extracted_at", "_airbyte_meta", "_airbyte_generation_id", "_airbyte_loaded_at", "_airbyte_data")
            |FROM '@$stagingTableName'
            |FILE_FORMAT = (
            |    TYPE = 'CSV'
            |    COMPRESSION = GZIP
            |    FIELD_DELIMITER = '$CSV_FIELD_SEPARATOR'
            |    RECORD_DELIMITER = '$CSV_LINE_DELIMITER'
            |    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
            |    TRIM_SPACE = TRUE
            |    ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE
            |    REPLACE_INVALID_CHARACTERS = TRUE
            |    ESCAPE = NONE
            |    ESCAPE_UNENCLOSED_FIELD = NONE
            |)
            |ON_ERROR = 'ABORT_STATEMENT'
            |PURGE = TRUE
            |files = ('test.csv.gz')
        """.trimMargin()
        assertEquals(expectedSql, sql)
    }

    @Test
    fun testGenerateSwapTable() {
        val sourceTableName = TableName(namespace = "namespace", name = "source")
        val targetTableName = TableName(namespace = "namespace", name = "target")
        val sql = snowflakeDirectLoadSqlGenerator.swapTableWith(sourceTableName, targetTableName)
        assertEquals(
            "ALTER TABLE ${snowflakeDirectLoadSqlGenerator.fullyQualifiedName(sourceTableName)} SWAP WITH ${snowflakeDirectLoadSqlGenerator.fullyQualifiedName(targetTableName)}",
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
        val tableName = TableName(namespace = "namespace", name = "table'; DROP TABLE users; --")

        // Create a minimal table schema for testing
        val tableSchema =
            StreamTableSchema(
                tableNames = TableNames(finalTableName = tableName, tempTableName = tableName),
                columnSchema =
                    ColumnSchema(
                        inputToFinalColumnNames = emptyMap(),
                        finalSchema = emptyMap(),
                        inputSchema = emptyMap()
                    ),
                importType = Append
            )

        val sql = snowflakeDirectLoadSqlGenerator.createTable(tableName, tableSchema, false)

        // The SQL injection attempt should be properly escaped with quotes
        val expectedTableName = snowflakeDirectLoadSqlGenerator.fullyQualifiedName(tableName)
        val expectedSql =
            """
            CREATE TABLE $expectedTableName (
                "_AIRBYTE_RAW_ID" VARCHAR NOT NULL,
                "_AIRBYTE_EXTRACTED_AT" TIMESTAMP_TZ NOT NULL,
                "_AIRBYTE_META" VARIANT NOT NULL,
                "_AIRBYTE_GENERATION_ID" NUMBER
            )
            """.trimIndent()

        assertEquals(expectedSql, sql)
    }

    @Test
    fun testCreateTableWithSQLInjectionAttemptInNamespace() {
        val tableName = TableName(namespace = "namespace'; DROP SCHEMA test; --", name = "table")

        // Create a minimal table schema for testing
        val tableSchema =
            StreamTableSchema(
                tableNames = TableNames(finalTableName = tableName, tempTableName = tableName),
                columnSchema =
                    ColumnSchema(
                        inputToFinalColumnNames = emptyMap(),
                        finalSchema = emptyMap(),
                        inputSchema = emptyMap()
                    ),
                importType = Append
            )

        val sql = snowflakeDirectLoadSqlGenerator.createTable(tableName, tableSchema, false)

        // The SQL injection attempt should be properly escaped with quotes
        val expectedTableName = snowflakeDirectLoadSqlGenerator.fullyQualifiedName(tableName)
        val expectedSql =
            """
            CREATE TABLE $expectedTableName (
                "_AIRBYTE_RAW_ID" VARCHAR NOT NULL,
                "_AIRBYTE_EXTRACTED_AT" TIMESTAMP_TZ NOT NULL,
                "_AIRBYTE_META" VARIANT NOT NULL,
                "_AIRBYTE_GENERATION_ID" NUMBER
            )
            """.trimIndent()

        assertEquals(expectedSql, sql)
    }

    @Test
    fun testCreateTableWithReservedKeywordsAsNames() {
        // Test with Snowflake reserved keywords as table/namespace names
        val tableName = TableName(namespace = "SELECT", name = "WHERE")

        // Create a minimal table schema for testing
        val tableSchema =
            StreamTableSchema(
                tableNames = TableNames(finalTableName = tableName, tempTableName = tableName),
                columnSchema =
                    ColumnSchema(
                        inputToFinalColumnNames = emptyMap(),
                        finalSchema = emptyMap(),
                        inputSchema = emptyMap()
                    ),
                importType = Append
            )

        val sql = snowflakeDirectLoadSqlGenerator.createTable(tableName, tableSchema, false)

        // Reserved keywords should be properly quoted
        val expectedTableName = snowflakeDirectLoadSqlGenerator.fullyQualifiedName(tableName)
        val expectedSql =
            """
            CREATE TABLE $expectedTableName (
                "_AIRBYTE_RAW_ID" VARCHAR NOT NULL,
                "_AIRBYTE_EXTRACTED_AT" TIMESTAMP_TZ NOT NULL,
                "_AIRBYTE_META" VARIANT NOT NULL,
                "_AIRBYTE_GENERATION_ID" NUMBER
            )
            """.trimIndent()

        assertEquals(expectedSql, sql)
    }

    @Test
    fun testGenerateUpsertTableWithCdcHardDelete() {
        // Test with CDC hard delete mode when _ab_cdc_deleted_at column is present
        every { snowflakeConfiguration.cdcDeletionMode } returns CdcDeletionMode.HARD_DELETE

        val sourceTableName = TableName(namespace = "test_ns", name = "source")
        val targetTableName = TableName(namespace = "test_ns", name = "target")

        // Create table schema with CDC deletion column
        val tableSchema =
            StreamTableSchema(
                tableNames =
                    TableNames(finalTableName = targetTableName, tempTableName = sourceTableName),
                columnSchema =
                    ColumnSchema(
                        inputToFinalColumnNames =
                            mapOf(
                                "id" to "ID",
                                "name" to "NAME",
                                "updated_at" to "UPDATED_AT",
                                "_ab_cdc_deleted_at" to "_AB_CDC_DELETED_AT"
                            ),
                        finalSchema =
                            mapOf(
                                "ID" to ColumnType("VARCHAR", false),
                                "NAME" to ColumnType("VARCHAR", true),
                                "UPDATED_AT" to ColumnType("TIMESTAMP_TZ", true),
                                "_AB_CDC_DELETED_AT" to ColumnType("TIMESTAMP_TZ", true)
                            ),
                        inputSchema =
                            mapOf(
                                "id" to FieldType(StringType, nullable = false),
                                "name" to FieldType(StringType, nullable = true),
                                "updated_at" to FieldType(StringType, nullable = true),
                                "_ab_cdc_deleted_at" to FieldType(StringType, nullable = true)
                            )
                    ),
                importType =
                    Dedupe(primaryKey = listOf(listOf("id")), cursor = listOf("updated_at"))
            )

        val sql =
            snowflakeDirectLoadSqlGenerator.upsertTable(
                tableSchema,
                sourceTableName,
                targetTableName
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

        val sourceTableName = TableName(namespace = "test_ns", name = "source")
        val targetTableName = TableName(namespace = "test_ns", name = "target")

        // Create table schema with CDC deletion column
        val tableSchema =
            StreamTableSchema(
                tableNames =
                    TableNames(finalTableName = targetTableName, tempTableName = sourceTableName),
                columnSchema =
                    ColumnSchema(
                        inputToFinalColumnNames =
                            mapOf(
                                "id" to "ID",
                                "name" to "NAME",
                                "updated_at" to "UPDATED_AT",
                                "_ab_cdc_deleted_at" to "_AB_CDC_DELETED_AT"
                            ),
                        finalSchema =
                            mapOf(
                                "ID" to ColumnType("VARCHAR", false),
                                "NAME" to ColumnType("VARCHAR", true),
                                "UPDATED_AT" to ColumnType("TIMESTAMP_TZ", true),
                                "_AB_CDC_DELETED_AT" to ColumnType("TIMESTAMP_TZ", true)
                            ),
                        inputSchema =
                            mapOf(
                                "id" to FieldType(StringType, nullable = false),
                                "name" to FieldType(StringType, nullable = true),
                                "updated_at" to FieldType(StringType, nullable = true),
                                "_ab_cdc_deleted_at" to FieldType(StringType, nullable = true)
                            )
                    ),
                importType =
                    Dedupe(primaryKey = listOf(listOf("id")), cursor = listOf("updated_at"))
            )

        val sql =
            snowflakeDirectLoadSqlGenerator.upsertTable(
                tableSchema,
                sourceTableName,
                targetTableName
            )

        // Should NOT include DELETE clause in soft delete mode
        assert(!sql.contains("THEN DELETE"))
        assert(sql.contains("WHEN NOT MATCHED THEN INSERT"))
        assert(!sql.contains("AND new_record.${CDC_DELETED_AT_COLUMN.quote()} IS NULL"))
    }

    @Test
    fun testGenerateUpsertTableWithoutCdc() {
        // Configure for no CDC
        every { snowflakeConfiguration.cdcDeletionMode } returns CdcDeletionMode.SOFT_DELETE

        val sourceTableName = TableName(namespace = "namespace", name = "source")
        val targetTableName = TableName(namespace = "namespace", name = "target")

        // Create a table schema with primary key and cursor but no CDC column
        val tableSchema =
            StreamTableSchema(
                tableNames =
                    TableNames(finalTableName = targetTableName, tempTableName = sourceTableName),
                columnSchema =
                    ColumnSchema(
                        inputToFinalColumnNames = mapOf("id" to "ID", "updated_at" to "UPDATED_AT"),
                        finalSchema =
                            mapOf(
                                "ID" to ColumnType("VARCHAR", false),
                                "UPDATED_AT" to ColumnType("TIMESTAMP_TZ", true)
                            ),
                        inputSchema =
                            mapOf(
                                "id" to FieldType(StringType, nullable = false),
                                "updated_at" to FieldType(StringType, nullable = true)
                            )
                    ),
                importType =
                    Dedupe(primaryKey = listOf(listOf("id")), cursor = listOf("updated_at"))
            )

        val sql =
            snowflakeDirectLoadSqlGenerator.upsertTable(
                tableSchema,
                sourceTableName,
                targetTableName
            )

        // Print the actual SQL for debugging
        println("Generated SQL (without CDC):\n$sql")

        // Verify the SQL contains the expected components for non-CDC upsert
        assertTrue(sql.contains("MERGE INTO"))
        assertTrue(sql.contains("WITH records AS"))
        assertTrue(sql.contains("numbered_rows AS"))
        assertTrue(sql.contains("ROW_NUMBER() OVER"))
        assertTrue(sql.contains("PARTITION BY \"ID\""))
        assertTrue(sql.contains("ORDER BY \"UPDATED_AT\" DESC NULLS LAST"))
        // No CDC DELETE clause
        assertFalse(sql.contains("_AB_CDC_DELETED_AT"))
        assertTrue(sql.contains("WHEN MATCHED AND"))
        assertTrue(sql.contains("THEN UPDATE SET"))
        assertTrue(sql.contains("WHEN NOT MATCHED"))
        assertTrue(sql.contains("THEN INSERT"))
    }

    @Test
    fun testGenerateUpsertTableNoCursor() {
        val sourceTableName = TableName(namespace = "namespace", name = "source")
        val targetTableName = TableName(namespace = "namespace", name = "target")

        // Create a table schema with primary key but no cursor
        val tableSchema =
            StreamTableSchema(
                tableNames =
                    TableNames(finalTableName = targetTableName, tempTableName = sourceTableName),
                columnSchema =
                    ColumnSchema(
                        inputToFinalColumnNames = mapOf("id" to "ID", "data" to "DATA"),
                        finalSchema =
                            mapOf(
                                "ID" to ColumnType("VARCHAR", false),
                                "DATA" to ColumnType("VARCHAR", true)
                            ),
                        inputSchema =
                            mapOf(
                                "id" to FieldType(StringType, nullable = false),
                                "data" to FieldType(StringType, nullable = true)
                            )
                    ),
                importType = Dedupe(primaryKey = listOf(listOf("id")), cursor = emptyList())
            )

        val sql =
            snowflakeDirectLoadSqlGenerator.upsertTable(
                tableSchema,
                sourceTableName,
                targetTableName
            )

        // Print the actual SQL for debugging
        println("Generated SQL (no cursor):\n$sql")

        // Verify the SQL contains the expected components for no-cursor upsert
        assertTrue(sql.contains("MERGE INTO"))
        assertTrue(sql.contains("WITH records AS"))
        assertTrue(sql.contains("numbered_rows AS"))
        assertTrue(sql.contains("ROW_NUMBER() OVER"))
        assertTrue(sql.contains("PARTITION BY \"ID\""))
        // No cursor ordering, just _AIRBYTE_EXTRACTED_AT (may have extra space)
        assertTrue(sql.contains("\"_AIRBYTE_EXTRACTED_AT\" DESC"))
        assertFalse(sql.contains("UPDATED_AT"))
        // Simple extracted_at comparison in WHEN MATCHED
        assertTrue(
            sql.contains(
                "target_table.\"_AIRBYTE_EXTRACTED_AT\" < new_record.\"_AIRBYTE_EXTRACTED_AT\""
            )
        )
        assertTrue(sql.contains("THEN UPDATE SET"))
        assertTrue(sql.contains("WHEN NOT MATCHED"))
        assertTrue(sql.contains("THEN INSERT"))
    }

    @Test
    fun testGenerateOverwriteTable() {
        // Test overwrite functionality using copyTable with empty destination
        val sourceTableName = TableName(namespace = "namespace", name = "source")
        val targetTableName = TableName(namespace = "namespace", name = "target")

        val columnNames =
            setOf(
                "_AIRBYTE_RAW_ID",
                "_AIRBYTE_EXTRACTED_AT",
                "_AIRBYTE_META",
                "_AIRBYTE_GENERATION_ID",
                "DATA_COL"
            )

        val sql =
            snowflakeDirectLoadSqlGenerator.copyTable(
                columnNames = columnNames,
                sourceTableName = sourceTableName,
                targetTableName = targetTableName
            )

        val expectedSourceTable =
            snowflakeDirectLoadSqlGenerator.fullyQualifiedName(sourceTableName)
        val expectedTargetTable =
            snowflakeDirectLoadSqlGenerator.fullyQualifiedName(targetTableName)

        val columnList = columnNames.joinToString(", ") { "\"$it\"" }
        val expectedSql =
            """
            INSERT INTO $expectedTargetTable 
            (
                $columnList
            )
            SELECT
                $columnList
            FROM $expectedSourceTable
        """.trimIndent()

        assertEquals(expectedSql, sql)
    }

    @Test
    fun testGenerateUpdateTable() {
        // Test update functionality is part of the MERGE statement
        val sourceTableName = TableName(namespace = "namespace", name = "source")
        val targetTableName = TableName(namespace = "namespace", name = "target")

        // Create a table schema with multiple columns to update
        val tableSchema =
            StreamTableSchema(
                tableNames =
                    TableNames(finalTableName = targetTableName, tempTableName = sourceTableName),
                columnSchema =
                    ColumnSchema(
                        inputToFinalColumnNames =
                            mapOf(
                                "id" to "ID",
                                "name" to "NAME",
                                "value" to "VALUE",
                                "updated_at" to "UPDATED_AT"
                            ),
                        finalSchema =
                            mapOf(
                                "ID" to ColumnType("VARCHAR", false),
                                "NAME" to ColumnType("VARCHAR", true),
                                "VALUE" to ColumnType("NUMBER", true),
                                "UPDATED_AT" to ColumnType("TIMESTAMP_TZ", true)
                            ),
                        inputSchema =
                            mapOf(
                                "id" to FieldType(StringType, nullable = false),
                                "name" to FieldType(StringType, nullable = true),
                                "value" to FieldType(StringType, nullable = true),
                                "updated_at" to FieldType(StringType, nullable = true)
                            )
                    ),
                importType =
                    Dedupe(primaryKey = listOf(listOf("id")), cursor = listOf("updated_at"))
            )

        val sql =
            snowflakeDirectLoadSqlGenerator.upsertTable(
                tableSchema,
                sourceTableName,
                targetTableName
            )

        // The MERGE statement should include UPDATE SET clause for all columns
        val expectedSourceTable =
            snowflakeDirectLoadSqlGenerator.fullyQualifiedName(sourceTableName)
        val expectedTargetTable =
            snowflakeDirectLoadSqlGenerator.fullyQualifiedName(targetTableName)

        val expectedSql =
            """
                |MERGE INTO $expectedTargetTable AS target_table
                |USING (
                |  WITH records AS (
                |    SELECT
                |      "_AIRBYTE_RAW_ID",
                |      "_AIRBYTE_EXTRACTED_AT",
                |      "_AIRBYTE_META",
                |      "_AIRBYTE_GENERATION_ID",
                |      "ID",
                |      "NAME",
                |      "VALUE",
                |      "UPDATED_AT"
                |    FROM $expectedSourceTable
                |  ), numbered_rows AS (
                |    SELECT *, ROW_NUMBER() OVER (
                |      PARTITION BY "ID" ORDER BY "UPDATED_AT" DESC NULLS LAST, "_AIRBYTE_EXTRACTED_AT" DESC
                |    ) AS row_number
                |    FROM records
                |  )
                |  SELECT "_AIRBYTE_RAW_ID",
                |      "_AIRBYTE_EXTRACTED_AT",
                |      "_AIRBYTE_META",
                |      "_AIRBYTE_GENERATION_ID",
                |      "ID",
                |      "NAME",
                |      "VALUE",
                |      "UPDATED_AT"
                |  FROM numbered_rows
                |  WHERE row_number = 1
                |) AS new_record
                |ON (target_table."ID" = new_record."ID" OR (target_table."ID" IS NULL AND new_record."ID" IS NULL))
                |WHEN MATCHED AND (
                |  target_table."UPDATED_AT" < new_record."UPDATED_AT"
                |  OR (target_table."UPDATED_AT" = new_record."UPDATED_AT" AND target_table."_AIRBYTE_EXTRACTED_AT" < new_record."_AIRBYTE_EXTRACTED_AT")
                |  OR (target_table."UPDATED_AT" IS NULL AND new_record."UPDATED_AT" IS NULL AND target_table."_AIRBYTE_EXTRACTED_AT" < new_record."_AIRBYTE_EXTRACTED_AT")
                |  OR (target_table."UPDATED_AT" IS NULL AND new_record."UPDATED_AT" IS NOT NULL)
                |) THEN UPDATE SET
                |  "_AIRBYTE_RAW_ID" = new_record."_AIRBYTE_RAW_ID",
                |  "_AIRBYTE_EXTRACTED_AT" = new_record."_AIRBYTE_EXTRACTED_AT",
                |  "_AIRBYTE_META" = new_record."_AIRBYTE_META",
                |  "_AIRBYTE_GENERATION_ID" = new_record."_AIRBYTE_GENERATION_ID",
                |  "ID" = new_record."ID",
                |  "NAME" = new_record."NAME",
                |  "VALUE" = new_record."VALUE",
                |  "UPDATED_AT" = new_record."UPDATED_AT"
                |WHEN NOT MATCHED THEN INSERT (
                |  "_AIRBYTE_RAW_ID",
                |  "_AIRBYTE_EXTRACTED_AT",
                |  "_AIRBYTE_META",
                |  "_AIRBYTE_GENERATION_ID",
                |  "ID",
                |  "NAME",
                |  "VALUE",
                |  "UPDATED_AT"
                |) VALUES (
                |  new_record."_AIRBYTE_RAW_ID",
                |  new_record."_AIRBYTE_EXTRACTED_AT",
                |  new_record."_AIRBYTE_META",
                |  new_record."_AIRBYTE_GENERATION_ID",
                |  new_record."ID",
                |  new_record."NAME",
                |  new_record."VALUE",
                |  new_record."UPDATED_AT"
                |)
        """.trimMargin()

        assertEquals(expectedSql, sql)
    }

    // Tests moved from SnowflakeSqlNameUtilsTest
    @Test
    fun testFullyQualifiedNameInCountTable() {
        val databaseName = "test-database"
        val namespace = "test-namespace"
        val name = "test=name"
        val tableName = TableName(namespace = namespace, name = name)
        every { snowflakeConfiguration.database } returns databaseName

        val sql = snowflakeDirectLoadSqlGenerator.countTable(tableName)

        val expected =
            "SELECT COUNT(*) AS TOTAL FROM ${snowflakeDirectLoadSqlGenerator.fullyQualifiedName(tableName)}"
        assertEquals(expected, sql)
    }

    @Test
    fun testFullyQualifiedNamespaceInCreateNamespace() {
        val databaseName = "test-database"
        val namespace = "test-namespace"
        every { snowflakeConfiguration.database } returns databaseName

        val sql = snowflakeDirectLoadSqlGenerator.createNamespace(namespace)

        val expected =
            "CREATE SCHEMA IF NOT EXISTS ${snowflakeDirectLoadSqlGenerator.fullyQualifiedNamespace(namespace)}"
        assertEquals(expected, sql)
    }

    @Test
    fun testFullyQualifiedStageNameInCreateStage() {
        val databaseName = "test-database"
        val namespace = "test-namespace"
        val name = "test=name"
        val tableName = TableName(namespace = namespace, name = name)
        every { snowflakeConfiguration.database } returns databaseName

        val sql = snowflakeDirectLoadSqlGenerator.createSnowflakeStage(tableName)

        val expected =
            "CREATE STAGE IF NOT EXISTS ${snowflakeDirectLoadSqlGenerator.fullyQualifiedStageName(tableName)}"
        assertEquals(expected, sql)
    }

    @Test
    fun testFullyQualifiedStageNameWithEscapeInPutInStage() {
        val databaseName = "test-database"
        val namespace = "test-namespace"
        val name = "test=\"\"\'name"
        val tableName = TableName(namespace = namespace, name = name)
        every { snowflakeConfiguration.database } returns databaseName

        val sql = snowflakeDirectLoadSqlGenerator.putInStage(tableName, "/tmp/test.csv")

        val expectedStageName =
            snowflakeDirectLoadSqlGenerator.fullyQualifiedStageName(tableName, true)
        val expected =
            """
            PUT 'file:///tmp/test.csv' '@$expectedStageName'
            AUTO_COMPRESS = FALSE
            SOURCE_COMPRESSION = GZIP
            OVERWRITE = TRUE
        """.trimIndent()
        assertEquals(expected, sql)
    }
}
