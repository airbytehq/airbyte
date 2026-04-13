/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.sql

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.ColumnTypeChange
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.integrations.destination.redshift2.schema.RedshiftColumnManager
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

internal class RedshiftSqlGeneratorTest {

    private lateinit var generator: RedshiftSqlGenerator
    private lateinit var columnManager: RedshiftColumnManager

    @BeforeEach
    fun setUp() {
        columnManager = RedshiftColumnManager()
        generator = RedshiftSqlGenerator(columnManager)
    }

    // ================================================================
    // Helpers
    // ================================================================

    /** Normalizes whitespace for comparison: trims each line and removes blank lines. */
    private fun normalize(sql: String): String =
        sql.lines().map { it.trim() }.filter { it.isNotEmpty() }.joinToString("\n")

    private fun assertSqlEquals(expected: String, actual: String) {
        assertEquals(normalize(expected), normalize(actual))
    }

    private fun buildStream(
        finalSchema: Map<String, ColumnType>,
        importType: ImportType = Append,
        primaryKey: List<List<String>> = emptyList(),
        cursor: List<String> = emptyList(),
        inputSchema: Map<String, FieldType> = emptyMap(),
    ): DestinationStream {
        val columnSchema = ColumnSchema(inputSchema, emptyMap(), finalSchema)
        val streamTableSchema =
            mockk<StreamTableSchema> {
                every { this@mockk.columnSchema } returns columnSchema
                every { this@mockk.importType } returns importType
                every { getPrimaryKey() } returns primaryKey
                every { getCursor() } returns cursor
            }
        return mockk { every { tableSchema } returns streamTableSchema }
    }

    // ================================================================
    // createNamespace
    // ================================================================

    @Test
    fun `createNamespace generates CREATE SCHEMA IF NOT EXISTS`() {
        val sql = generator.createNamespace("my_schema")
        assertSqlEquals("""CREATE SCHEMA IF NOT EXISTS "my_schema";""", sql)
    }

    // ================================================================
    // createTable
    // ================================================================

    @Test
    fun `createTable with replace drops then creates`() {
        val stream =
            buildStream(
                finalSchema =
                    mapOf(
                        "user_name" to ColumnType("varchar(65535)", false),
                        "age" to ColumnType("bigint", true),
                    )
            )
        val tableName = TableName(namespace = "public", name = "users")

        val sql = generator.createTable(stream, tableName, replace = true)

        assertTrue(normalize(sql).contains("DROP TABLE IF EXISTS"))
        assertTrue(normalize(sql).contains("CREATE TABLE IF NOT EXISTS"))
        assertTrue(normalize(sql).contains("\"_airbyte_raw_id\""))
        assertTrue(normalize(sql).contains("\"user_name\" varchar(65535) NOT NULL"))
        assertTrue(normalize(sql).contains("\"age\" bigint"))
        assertTrue(normalize(sql).contains("BEGIN TRANSACTION"))
        assertTrue(normalize(sql).contains("COMMIT"))
    }

    @Test
    fun `createTable without replace omits DROP`() {
        val stream = buildStream(finalSchema = mapOf("col" to ColumnType("varchar(65535)", true)))
        val tableName = TableName(namespace = "public", name = "test")

        val sql = generator.createTable(stream, tableName, replace = false)

        assertTrue(!normalize(sql).contains("DROP TABLE"))
        assertTrue(normalize(sql).contains("CREATE TABLE IF NOT EXISTS"))
    }

    @Test
    fun `createTable includes all meta columns`() {
        val stream = buildStream(finalSchema = emptyMap())
        val tableName = TableName(namespace = "ns", name = "t")

        val sql = generator.createTable(stream, tableName, replace = false)

        assertTrue(sql.contains("\"_airbyte_raw_id\" varchar(36) NOT NULL"))
        assertTrue(sql.contains("\"_airbyte_extracted_at\" timestamptz NOT NULL"))
        assertTrue(sql.contains("\"_airbyte_meta\" super NOT NULL"))
        assertTrue(sql.contains("\"_airbyte_generation_id\" bigint NOT NULL"))
    }

    // ================================================================
    // createTableForCheck
    // ================================================================

    @Test
    fun `createTableForCheck generates DDL from StreamTableSchema`() {
        val tableName = TableName(namespace = "public", name = "check_test")
        val tableSchema =
            mockk<StreamTableSchema> {
                every { columnSchema } returns
                    ColumnSchema(
                        emptyMap(),
                        emptyMap(),
                        mapOf("test_key" to ColumnType("varchar(65535)", true)),
                    )
            }

        val sql = generator.createTableForCheck(tableName, tableSchema)

        assertTrue(sql.contains("CREATE TABLE IF NOT EXISTS"))
        assertTrue(sql.contains("\"test_key\" varchar(65535)"))
        assertTrue(sql.contains("\"_airbyte_raw_id\""))
        // Should NOT contain DROP or transaction (simple check table)
        assertTrue(!sql.contains("DROP TABLE"))
    }

    // ================================================================
    // dropTable
    // ================================================================

    @Test
    fun `dropTable generates DROP TABLE IF EXISTS`() {
        val tableName = TableName(namespace = "public", name = "old_table")
        val sql = generator.dropTable(tableName)
        assertSqlEquals("""DROP TABLE IF EXISTS "public"."old_table";""", sql)
    }

    // ================================================================
    // countTable
    // ================================================================

    @Test
    fun `countTable generates SELECT COUNT with alias`() {
        val tableName = TableName(namespace = "public", name = "my_table")
        val sql = generator.countTable(tableName)
        assertSqlEquals(
            """SELECT COUNT(*) AS "total" FROM "public"."my_table";""",
            sql,
        )
    }

    // ================================================================
    // getGenerationId
    // ================================================================

    @Test
    fun `getGenerationId generates correct SELECT`() {
        val tableName = TableName(namespace = "public", name = "my_table")
        val sql = generator.getGenerationId(tableName)
        assertTrue(sql.contains("\"_airbyte_generation_id\""))
        assertTrue(sql.contains("LIMIT 1"))
    }

    // ================================================================
    // deleteByRawId
    // ================================================================

    @Test
    fun `deleteByRawId generates parameterized DELETE`() {
        val tableName = TableName(namespace = "public", name = "my_table")
        val sql = generator.deleteByRawId(tableName)
        assertTrue(sql.contains("DELETE FROM"))
        assertTrue(sql.contains("\"_airbyte_raw_id\" = ?"))
    }

    // ================================================================
    // copyTable
    // ================================================================

    @Test
    fun `copyTable generates INSERT INTO SELECT`() {
        val source = TableName(namespace = "public", name = "source")
        val target = TableName(namespace = "public", name = "target")

        val sql = generator.copyTable(listOf("col_a", "col_b"), source, target)

        assertTrue(sql.contains("INSERT INTO \"public\".\"target\""))
        assertTrue(sql.contains("\"col_a\", \"col_b\""))
        assertTrue(sql.contains("FROM \"public\".\"source\""))
    }

    // ================================================================
    // overwriteTable
    // ================================================================

    @Test
    fun `overwriteTable generates rename-based swap`() {
        val source = TableName(namespace = "public", name = "tmp_table")
        val target = TableName(namespace = "public", name = "final_table")

        val sql = generator.overwriteTable(source, target)

        assertTrue(sql.contains("BEGIN TRANSACTION"))
        assertTrue(sql.contains("DROP TABLE IF EXISTS \"public\".\"final_table\""))
        assertTrue(sql.contains("RENAME TO \"final_table\""))
        assertTrue(sql.contains("COMMIT"))
        // Same schema -- no SET SCHEMA
        assertTrue(!sql.contains("SET SCHEMA"))
    }

    @Test
    fun `overwriteTable handles cross-schema rename`() {
        val source = TableName(namespace = "staging", name = "tmp_table")
        val target = TableName(namespace = "public", name = "final_table")

        val sql = generator.overwriteTable(source, target)

        assertTrue(sql.contains("SET SCHEMA \"public\""))
    }

    // ================================================================
    // upsertTable
    // ================================================================

    @Test
    fun `upsertTable generates CTE-based dedup update insert`() {
        val importType = Dedupe(primaryKey = listOf(listOf("id")), cursor = listOf("updated_at"))
        val stream =
            buildStream(
                finalSchema =
                    mapOf(
                        "id" to ColumnType("bigint", false),
                        "updated_at" to ColumnType("timestamptz", true),
                        "name" to ColumnType("varchar(65535)", true),
                    ),
                importType = importType,
                primaryKey = listOf(listOf("id")),
                cursor = listOf("updated_at"),
            )

        val source = TableName(namespace = "public", name = "tmp")
        val target = TableName(namespace = "public", name = "final")

        val sql = generator.upsertTable(stream, source, target)

        // Verify CTE structure
        assertTrue(sql.contains("WITH deduped_source AS"))
        assertTrue(sql.contains("ROW_NUMBER() OVER"))
        assertTrue(sql.contains("PARTITION BY \"id\""))
        assertTrue(sql.contains("ORDER BY"))
        assertTrue(sql.contains("\"updated_at\" DESC NULLS LAST"))

        // Verify UPDATE
        assertTrue(sql.contains("updates AS"))
        assertTrue(sql.contains("UPDATE \"public\".\"final\""))

        // Verify INSERT
        assertTrue(sql.contains("INSERT INTO \"public\".\"final\""))
        assertTrue(sql.contains("NOT EXISTS"))
    }

    @Test
    fun `upsertTable with CDC hard delete includes delete CTE`() {
        val importType = Dedupe(primaryKey = listOf(listOf("id")), cursor = listOf("updated_at"))
        val stream =
            buildStream(
                finalSchema =
                    mapOf(
                        "id" to ColumnType("bigint", false),
                        "updated_at" to ColumnType("timestamptz", true),
                    ),
                importType = importType,
                primaryKey = listOf(listOf("id")),
                cursor = listOf("updated_at"),
                inputSchema = mapOf(CDC_DELETED_AT_COLUMN to FieldType(StringType, true)),
            )

        val source = TableName(namespace = "public", name = "tmp")
        val target = TableName(namespace = "public", name = "final")

        val sql = generator.upsertTable(stream, source, target)

        // Should contain CDC delete CTE
        assertTrue(sql.contains("deleted AS"))
        assertTrue(sql.contains("DELETE FROM"))
        assertTrue(sql.contains("_ab_cdc_deleted_at"))
        assertTrue(sql.contains("IS NOT NULL"))

        // Update and insert should filter out CDC-deleted rows
        assertTrue(sql.contains("IS NULL"))
    }

    @Test
    fun `upsertTable without cursor uses extracted_at only`() {
        val importType = Dedupe(primaryKey = listOf(listOf("id")), cursor = emptyList())
        val stream =
            buildStream(
                finalSchema = mapOf("id" to ColumnType("bigint", false)),
                importType = importType,
                primaryKey = listOf(listOf("id")),
                cursor = emptyList(),
            )

        val source = TableName(namespace = "public", name = "tmp")
        val target = TableName(namespace = "public", name = "final")

        val sql = generator.upsertTable(stream, source, target)

        // Cursor comparison should only use extracted_at
        assertTrue(sql.contains("\"_airbyte_extracted_at\""))
        // Should NOT contain NULLS LAST (no cursor ordering)
        assertTrue(!sql.contains("NULLS LAST"))
    }

    @Test
    fun `upsertTable throws on empty primary key`() {
        val importType = Dedupe(primaryKey = emptyList(), cursor = emptyList())
        val stream =
            buildStream(
                finalSchema = mapOf("col" to ColumnType("varchar(65535)", true)),
                importType = importType,
                primaryKey = emptyList(),
            )

        val source = TableName(namespace = "public", name = "tmp")
        val target = TableName(namespace = "public", name = "final")

        assertThrows<IllegalArgumentException> { generator.upsertTable(stream, source, target) }
    }

    @Test
    fun `upsertTable with composite primary key`() {
        val importType =
            Dedupe(
                primaryKey = listOf(listOf("tenant_id"), listOf("user_id")),
                cursor = listOf("ts"),
            )
        val stream =
            buildStream(
                finalSchema =
                    mapOf(
                        "tenant_id" to ColumnType("bigint", false),
                        "user_id" to ColumnType("bigint", false),
                        "ts" to ColumnType("timestamptz", true),
                    ),
                importType = importType,
                primaryKey = listOf(listOf("tenant_id"), listOf("user_id")),
                cursor = listOf("ts"),
            )

        val source = TableName(namespace = "public", name = "tmp")
        val target = TableName(namespace = "public", name = "final")

        val sql = generator.upsertTable(stream, source, target)

        assertTrue(sql.contains("PARTITION BY \"tenant_id\", \"user_id\""))
        assertTrue(sql.contains("\"tenant_id\""))
        assertTrue(sql.contains("\"user_id\""))
    }

    // ================================================================
    // matchSchemas (schema evolution)
    // ================================================================

    @Test
    fun `matchSchemas generates ADD COLUMN`() {
        val tableName = TableName(namespace = "public", name = "my_table")
        val sql =
            generator.matchSchemas(
                tableName = tableName,
                columnsToAdd = mapOf("new_col" to ColumnType("varchar(65535)", true)),
                columnsToRemove = emptyMap(),
                columnsToModify = emptyMap(),
            )

        assertTrue(
            sql.contains(
                "ALTER TABLE \"public\".\"my_table\" ADD COLUMN \"new_col\" varchar(65535)"
            )
        )
        assertTrue(sql.contains("BEGIN TRANSACTION"))
        assertTrue(sql.contains("COMMIT"))
    }

    @Test
    fun `matchSchemas generates DROP COLUMN`() {
        val tableName = TableName(namespace = "public", name = "my_table")
        val sql =
            generator.matchSchemas(
                tableName = tableName,
                columnsToAdd = emptyMap(),
                columnsToRemove = mapOf("old_col" to ColumnType("varchar(65535)", true)),
                columnsToModify = emptyMap(),
            )

        assertTrue(sql.contains("DROP COLUMN \"old_col\""))
    }

    @Test
    fun `matchSchemas generates 4-step type change with CAST`() {
        val tableName = TableName(namespace = "public", name = "my_table")
        val sql =
            generator.matchSchemas(
                tableName = tableName,
                columnsToAdd = emptyMap(),
                columnsToRemove = emptyMap(),
                columnsToModify =
                    mapOf(
                        "amount" to
                            ColumnTypeChange(
                                originalType = ColumnType("bigint", true),
                                newType = ColumnType("numeric(38,9)", true),
                            )
                    ),
            )

        val normalized = normalize(sql)
        // Step 1: add temp column
        assertTrue(normalized.contains("ADD COLUMN \"_airbyte_tmp_amount\" numeric(38,9)"))
        // Step 2: cast data
        assertTrue(
            normalized.contains("SET \"_airbyte_tmp_amount\" = CAST(\"amount\" AS numeric(38,9))")
        )
        // Step 3: drop original
        assertTrue(normalized.contains("DROP COLUMN \"amount\""))
        // Step 4: rename temp to original
        assertTrue(normalized.contains("RENAME COLUMN \"_airbyte_tmp_amount\" TO \"amount\""))
    }

    @Test
    fun `matchSchemas uses JSON_SERIALIZE for SUPER to VARCHAR`() {
        val tableName = TableName(namespace = "public", name = "t")
        val sql =
            generator.matchSchemas(
                tableName = tableName,
                columnsToAdd = emptyMap(),
                columnsToRemove = emptyMap(),
                columnsToModify =
                    mapOf(
                        "data" to
                            ColumnTypeChange(
                                originalType = ColumnType("super", true),
                                newType = ColumnType("varchar(65535)", true),
                            )
                    ),
            )

        assertTrue(sql.contains("JSON_SERIALIZE(\"data\")"))
    }

    @Test
    fun `matchSchemas uses JSON_PARSE for VARCHAR to SUPER`() {
        val tableName = TableName(namespace = "public", name = "t")
        val sql =
            generator.matchSchemas(
                tableName = tableName,
                columnsToAdd = emptyMap(),
                columnsToRemove = emptyMap(),
                columnsToModify =
                    mapOf(
                        "data" to
                            ColumnTypeChange(
                                originalType = ColumnType("varchar(65535)", true),
                                newType = ColumnType("super", true),
                            )
                    ),
            )

        assertTrue(sql.contains("JSON_PARSE(\"data\")"))
    }

    // ================================================================
    // getTableSchema
    // ================================================================

    @Test
    fun `getTableSchema queries information_schema`() {
        val tableName = TableName(namespace = "my_schema", name = "my_table")
        val sql = generator.getTableSchema(tableName)

        assertTrue(sql.contains("information_schema.columns"))
        assertTrue(sql.contains("table_schema = 'my_schema'"))
        assertTrue(sql.contains("table_name = 'my_table'"))
        assertTrue(sql.contains("ORDER BY ordinal_position"))
    }

    @Test
    fun `getTableSchema escapes single quotes in identifiers`() {
        val tableName = TableName(namespace = "O'Brien", name = "user's_table")
        val sql = generator.getTableSchema(tableName)

        assertTrue(sql.contains("O''Brien"))
        assertTrue(sql.contains("user''s_table"))
    }

    // ================================================================
    // copyFromS3
    // ================================================================

    @Test
    fun `copyFromS3 generates COPY command with all options`() {
        val tableName = TableName(namespace = "public", name = "my_table")
        val sql =
            generator.copyFromS3(
                tableName = tableName,
                s3Path = "s3://my-bucket/data/file.csv.gz",
                accessKeyId = "AKIA123",
                secretAccessKey = "secret456",
                region = "us-east-1",
            )

        assertTrue(sql.contains("COPY \"public\".\"my_table\""))
        assertTrue(sql.contains("FROM 's3://my-bucket/data/file.csv.gz'"))
        assertTrue(sql.contains("aws_access_key_id=AKIA123"))
        assertTrue(sql.contains("aws_secret_access_key=secret456"))
        assertTrue(sql.contains("CSV GZIP"))
        assertTrue(sql.contains("REGION 'us-east-1'"))
        assertTrue(sql.contains("TIMEFORMAT 'auto'"))
        assertTrue(sql.contains("STATUPDATE OFF"))
        assertTrue(sql.contains("IGNOREHEADER 1"))
    }

    // ================================================================
    // Namespace fallback
    // ================================================================

    @Test
    fun `fully qualified name defaults to public for blank namespace`() {
        val tableName = TableName(namespace = "", name = "my_table")
        val sql = generator.dropTable(tableName)
        assertTrue(sql.contains("\"public\".\"my_table\""))
    }
}
