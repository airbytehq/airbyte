/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.sql

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.ColumnTypeChange
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

internal class RedshiftSqlGeneratorTest {

    private lateinit var sqlGenerator: RedshiftSqlGenerator

    @BeforeEach
    fun setUp() {
        sqlGenerator = RedshiftSqlGenerator()
    }

    // ================================================================
    // Helpers
    // ================================================================

    private fun assertEqualsIgnoreWhitespace(expected: String, actual: String) {
        assertEquals(dropWhitespace(expected), dropWhitespace(actual))
    }

    private fun dropWhitespace(text: String) =
        text.lines().map { it.trim() }.filter { it.isNotEmpty() }.joinToString("\n") { it.trim() }

    private fun mockStream(
        finalSchema: Map<String, ColumnType>,
        inputSchema: Map<String, FieldType> = emptyMap(),
        primaryKey: List<List<String>> = emptyList(),
        cursor: List<String> = emptyList(),
    ): DestinationStream {
        val columnSchema = ColumnSchema(inputSchema, emptyMap(), finalSchema)
        val streamTableSchema =
            mockk<StreamTableSchema> {
                every { this@mockk.columnSchema } returns columnSchema
                every { getPrimaryKey() } returns primaryKey
                every { getCursor() } returns cursor
                every { importType } returns Dedupe(primaryKey = primaryKey, cursor = cursor)
            }
        return mockk<DestinationStream> { every { tableSchema } returns streamTableSchema }
    }

    // ================================================================
    // DDL: Namespace & Table lifecycle
    // ================================================================

    @Test
    fun `createNamespace generates CREATE SCHEMA`() {
        val sql = sqlGenerator.createNamespace("my_schema")
        assertEquals("""CREATE SCHEMA IF NOT EXISTS "my_schema";""", sql)
    }

    @Test
    fun `createTable with replace drops and recreates`() {
        val finalSchema =
            mapOf(
                "id" to ColumnType("bigint", false),
                "name" to ColumnType("varchar(65535)", true),
            )
        val stream = mockStream(finalSchema)
        val tableName = TableName(namespace = "public", name = "users")

        val sql = sqlGenerator.createTable(stream, tableName, replace = true)

        assertTrue(sql.contains("BEGIN TRANSACTION;"))
        assertTrue(sql.contains("""DROP TABLE IF EXISTS "public"."users";"""))
        assertTrue(sql.contains("""CREATE TABLE IF NOT EXISTS "public"."users""""))
        assertTrue(sql.contains(""""_airbyte_raw_id" varchar(36) NOT NULL"""))
        assertTrue(sql.contains(""""_airbyte_extracted_at" timestamptz NOT NULL"""))
        assertTrue(sql.contains(""""_airbyte_meta" super NOT NULL"""))
        assertTrue(sql.contains(""""_airbyte_generation_id" bigint NOT NULL"""))
        assertTrue(sql.contains(""""id" bigint NOT NULL"""))
        assertTrue(sql.contains(""""name" varchar(65535)"""))
        assertTrue(sql.contains("COMMIT;"))
    }

    @Test
    fun `createTable without replace skips drop`() {
        val finalSchema = mapOf("id" to ColumnType("bigint", false))
        val stream = mockStream(finalSchema)
        val tableName = TableName(namespace = "public", name = "users")

        val sql = sqlGenerator.createTable(stream, tableName, replace = false)

        assertFalse(sql.contains("DROP TABLE"))
        assertTrue(sql.contains("BEGIN TRANSACTION;"))
        assertTrue(sql.contains("CREATE TABLE IF NOT EXISTS"))
        assertTrue(sql.contains("COMMIT;"))
    }

    @Test
    fun `dropTable generates DROP TABLE IF EXISTS`() {
        val sql = sqlGenerator.dropTable(TableName(namespace = "ns", name = "tbl"))
        assertEquals("""DROP TABLE IF EXISTS "ns"."tbl";""", sql)
    }

    @Test
    fun `addColumn generates ALTER TABLE ADD COLUMN`() {
        val sql =
            sqlGenerator.addColumn(
                TableName(namespace = "ns", name = "tbl"),
                "new_col",
                "varchar(65535)",
            )
        assertEquals(
            """ALTER TABLE "ns"."tbl" ADD COLUMN "new_col" varchar(65535);""",
            sql,
        )
    }

    // ================================================================
    // DML: Simple queries
    // ================================================================

    @Test
    fun `countTable generates SELECT COUNT`() {
        val sql = sqlGenerator.countTable(TableName(namespace = "ns", name = "tbl"))
        assertEquals("""SELECT COUNT(*) AS "total" FROM "ns"."tbl";""", sql)
    }

    @Test
    fun `getGenerationId generates SELECT with LIMIT 1`() {
        val sql = sqlGenerator.getGenerationId(TableName(namespace = "ns", name = "tbl"))
        assertEquals(
            """SELECT "_airbyte_generation_id" FROM "ns"."tbl" LIMIT 1;""",
            sql,
        )
    }

    @Test
    fun `deleteByRawId generates parameterized DELETE`() {
        val sql = sqlGenerator.deleteByRawId(TableName(namespace = "ns", name = "tbl"))
        assertEquals(
            """DELETE FROM "ns"."tbl" WHERE "_airbyte_raw_id" = ?;""",
            sql,
        )
    }

    // ================================================================
    // Table operations: copy, overwrite
    // ================================================================

    @Test
    fun `copyTable generates INSERT INTO SELECT`() {
        val source = TableName(namespace = "ns", name = "src")
        val target = TableName(namespace = "ns", name = "tgt")

        val sql = sqlGenerator.copyTable(listOf("col_a", "col_b"), source, target)

        val expected =
            """
            INSERT INTO "ns"."tgt" ("col_a", "col_b")
            SELECT "col_a", "col_b"
            FROM "ns"."src";
            """
        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun `overwriteTable same schema generates DROP and RENAME`() {
        val source = TableName(namespace = "ns", name = "tmp")
        val target = TableName(namespace = "ns", name = "final")

        val sql = sqlGenerator.overwriteTable(source, target)

        assertTrue(sql.contains("BEGIN TRANSACTION;"))
        assertTrue(sql.contains("""DROP TABLE IF EXISTS "ns"."final""""))
        assertTrue(sql.contains("""ALTER TABLE "ns"."tmp" RENAME TO "final""""))
        assertFalse(sql.contains("SET SCHEMA"))
        assertTrue(sql.contains("COMMIT;"))
    }

    @Test
    fun `overwriteTable cross schema includes SET SCHEMA`() {
        val source = TableName(namespace = "staging", name = "tmp")
        val target = TableName(namespace = "public", name = "final")

        val sql = sqlGenerator.overwriteTable(source, target)

        assertTrue(sql.contains("""DROP TABLE IF EXISTS "public"."final""""))
        assertTrue(sql.contains("""ALTER TABLE "staging"."tmp" RENAME TO "final""""))
        assertTrue(sql.contains("""SET SCHEMA "public""""))
    }

    // ================================================================
    // Upsert: internal methods
    // ================================================================

    @Test
    fun `selectDeduped with cursor orders by cursor then extracted_at`() {
        val sql =
            sqlGenerator.selectDeduped(
                primaryKeyTargetColumns = listOf(""""id""""),
                cursorTargetColumn = """"updated_at"""",
                allTargetColumns = listOf(""""id"""", """"name"""", """"updated_at""""),
                sourceTableName = TableName(namespace = "ns", name = "staging"),
            )

        val expected =
            """
            SELECT "id", "name", "updated_at"
            FROM (
              SELECT *,
                ROW_NUMBER() OVER (
                  PARTITION BY "id"
                  ORDER BY
                    "updated_at" DESC NULLS LAST, "_airbyte_extracted_at" DESC
                ) AS row_number
              FROM "ns"."staging"
            ) AS deduplicated
            WHERE row_number = 1
            """
        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun `selectDeduped without cursor orders by extracted_at only`() {
        val sql =
            sqlGenerator.selectDeduped(
                primaryKeyTargetColumns = listOf(""""id""""),
                cursorTargetColumn = null,
                allTargetColumns = listOf(""""id"""", """"name""""),
                sourceTableName = TableName(namespace = "ns", name = "staging"),
            )

        assertTrue(sql.contains(""""_airbyte_extracted_at" DESC"""))
        assertFalse(sql.contains("NULLS LAST"))
    }

    @Test
    fun `cdcDelete enabled generates DELETE CTE with cursor comparison`() {
        val target = TableName(namespace = "ns", name = "final")
        val sql =
            sqlGenerator.cdcDelete(
                dedupTableAlias = "deduped_source",
                cursorTargetColumn = """"updated_at"""",
                targetTableName = target,
                primaryKeyTargetColumns = listOf(""""id""""),
                cdcHardDeleteEnabled = true,
            )

        assertTrue(sql.contains("deleted AS ("))
        assertTrue(sql.contains("""DELETE FROM "ns"."final""""))
        assertTrue(sql.contains("USING deduped_source"))
        assertTrue(sql.contains(""""_ab_cdc_deleted_at" IS NOT NULL"""))
        assertTrue(sql.contains(""""updated_at" < deduped_source."updated_at""""))
    }

    @Test
    fun `cdcDelete disabled returns empty string`() {
        val sql =
            sqlGenerator.cdcDelete(
                dedupTableAlias = "deduped_source",
                cursorTargetColumn = """"updated_at"""",
                targetTableName = TableName(namespace = "ns", name = "final"),
                primaryKeyTargetColumns = listOf(""""id""""),
                cdcHardDeleteEnabled = false,
            )

        assertEquals("", sql)
    }

    @Test
    fun `updateExistingRows excludes PK from SET assignments`() {
        val target = TableName(namespace = "ns", name = "final")
        val sql =
            sqlGenerator.updateExistingRows(
                dedupTableAlias = "deduped_source",
                targetTableName = target,
                allTargetColumns = listOf(""""id"""", """"name"""", """"updated_at""""),
                primaryKeyTargetColumns = listOf(""""id""""),
                cursorTargetColumn = """"updated_at"""",
                cdcHardDeleteEnabled = false,
            )

        // Extract the SET section (between "SET" and "FROM")
        val setSection = sql.substringAfter("SET").substringBefore("FROM")
        // PK should NOT appear in SET assignments
        assertFalse(setSection.contains(""""id" = deduped_source."id""""))
        // Non-PK columns should be in SET
        assertTrue(setSection.contains(""""name" = deduped_source."name""""))
        assertTrue(setSection.contains(""""updated_at" = deduped_source."updated_at""""))
        // PK should be in WHERE
        assertTrue(sql.contains(""""ns"."final"."id" = deduped_source."id""""))
    }

    @Test
    fun `updateExistingRows with CDC adds deleted_at IS NULL clause`() {
        val target = TableName(namespace = "ns", name = "final")
        val sql =
            sqlGenerator.updateExistingRows(
                dedupTableAlias = "deduped_source",
                targetTableName = target,
                allTargetColumns = listOf(""""id"""", """"name""""),
                primaryKeyTargetColumns = listOf(""""id""""),
                cursorTargetColumn = """"updated_at"""",
                cdcHardDeleteEnabled = true,
            )

        assertTrue(sql.contains(""""_ab_cdc_deleted_at" IS NULL"""))
    }

    @Test
    fun `updateExistingRows without cursor uses extracted_at comparison only`() {
        val target = TableName(namespace = "ns", name = "final")
        val sql =
            sqlGenerator.updateExistingRows(
                dedupTableAlias = "deduped_source",
                targetTableName = target,
                allTargetColumns = listOf(""""id"""", """"name""""),
                primaryKeyTargetColumns = listOf(""""id""""),
                cursorTargetColumn = null,
                cdcHardDeleteEnabled = false,
            )

        assertTrue(
            sql.contains(
                """"ns"."final"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at""""
            )
        )
        // Should NOT have the 4-way cursor comparison
        assertFalse(sql.contains("IS NULL AND deduped_source."))
    }

    @Test
    fun `insertNewRows without CDC has no deleted_at clause`() {
        val target = TableName(namespace = "ns", name = "final")
        val sql =
            sqlGenerator.insertNewRows(
                dedupTableAlias = "deduped_source",
                targetTableName = target,
                allTargetColumns = listOf(""""id"""", """"name""""),
                primaryKeyTargetColumns = listOf(""""id""""),
                cdcHardDeleteEnabled = false,
            )

        assertTrue(sql.contains("INSERT INTO"))
        assertTrue(sql.contains("NOT EXISTS"))
        assertFalse(sql.contains("_ab_cdc_deleted_at"))
    }

    @Test
    fun `insertNewRows with CDC adds deleted_at IS NULL clause`() {
        val target = TableName(namespace = "ns", name = "final")
        val sql =
            sqlGenerator.insertNewRows(
                dedupTableAlias = "deduped_source",
                targetTableName = target,
                allTargetColumns = listOf(""""id"""", """"name""""),
                primaryKeyTargetColumns = listOf(""""id""""),
                cdcHardDeleteEnabled = true,
            )

        assertTrue(sql.contains(""""_ab_cdc_deleted_at" IS NULL"""))
    }

    // ================================================================
    // Upsert: integration-level
    // ================================================================

    @Test
    fun `upsertTable with cursor and CDC generates full CTE chain`() {
        val finalSchema =
            mapOf(
                "id" to ColumnType("bigint", false),
                "name" to ColumnType("varchar(65535)", true),
                "updated_at" to ColumnType("timestamptz", true),
                CDC_DELETED_AT_COLUMN to ColumnType("timestamptz", true),
            )
        val inputSchema = mapOf(CDC_DELETED_AT_COLUMN to FieldType(TimestampTypeWithTimezone, true))
        val stream =
            mockStream(
                finalSchema = finalSchema,
                inputSchema = inputSchema,
                primaryKey = listOf(listOf("id")),
                cursor = listOf("updated_at"),
            )

        val source = TableName(namespace = "ns", name = "staging")
        val target = TableName(namespace = "ns", name = "final")

        val sql = sqlGenerator.upsertTable(stream, source, target)

        val expected =
            """
            WITH deduped_source AS (
              SELECT "_airbyte_raw_id", "_airbyte_extracted_at", "_airbyte_meta", "_airbyte_generation_id", "id", "name", "updated_at", "_ab_cdc_deleted_at"
              FROM (
                SELECT *,
                  ROW_NUMBER() OVER (
                    PARTITION BY "id"
                    ORDER BY
                      "updated_at" DESC NULLS LAST, "_airbyte_extracted_at" DESC
                  ) AS row_number
                FROM "ns"."staging"
              ) AS deduplicated
              WHERE row_number = 1
            ),

            deleted AS (
              DELETE FROM "ns"."final"
              USING deduped_source
              WHERE "ns"."final"."id" = deduped_source."id"
                AND deduped_source."_ab_cdc_deleted_at" IS NOT NULL
                AND ("ns"."final"."updated_at" < deduped_source."updated_at"
                OR ("ns"."final"."updated_at" = deduped_source."updated_at" AND "ns"."final"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at")
                OR ("ns"."final"."updated_at" IS NULL AND deduped_source."updated_at" IS NOT NULL)
                OR ("ns"."final"."updated_at" IS NULL AND deduped_source."updated_at" IS NULL AND "ns"."final"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at"))
            ),

            updates AS (
              UPDATE "ns"."final"
              SET
                "_airbyte_raw_id" = deduped_source."_airbyte_raw_id",
                "_airbyte_extracted_at" = deduped_source."_airbyte_extracted_at",
                "_airbyte_meta" = deduped_source."_airbyte_meta",
                "_airbyte_generation_id" = deduped_source."_airbyte_generation_id",
                "name" = deduped_source."name",
                "updated_at" = deduped_source."updated_at",
                "_ab_cdc_deleted_at" = deduped_source."_ab_cdc_deleted_at"
              FROM deduped_source
              WHERE "ns"."final"."id" = deduped_source."id"
                AND deduped_source."_ab_cdc_deleted_at" IS NULL
                AND ("ns"."final"."updated_at" < deduped_source."updated_at"
                OR ("ns"."final"."updated_at" = deduped_source."updated_at" AND "ns"."final"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at")
                OR ("ns"."final"."updated_at" IS NULL AND deduped_source."updated_at" IS NOT NULL)
                OR ("ns"."final"."updated_at" IS NULL AND deduped_source."updated_at" IS NULL AND "ns"."final"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at"))
            )

            INSERT INTO "ns"."final" (
              "_airbyte_raw_id",
              "_airbyte_extracted_at",
              "_airbyte_meta",
              "_airbyte_generation_id",
              "id",
              "name",
              "updated_at",
              "_ab_cdc_deleted_at"
            )
            SELECT
              "_airbyte_raw_id",
              "_airbyte_extracted_at",
              "_airbyte_meta",
              "_airbyte_generation_id",
              "id",
              "name",
              "updated_at",
              "_ab_cdc_deleted_at"
            FROM deduped_source
            WHERE
              NOT EXISTS (
                SELECT 1
                FROM "ns"."final"
                WHERE "ns"."final"."id" = deduped_source."id"
              )
              AND deduped_source."_ab_cdc_deleted_at" IS NULL
            """
        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun `upsertTable without CDC omits deleted CTE`() {
        val finalSchema =
            mapOf(
                "id" to ColumnType("bigint", false),
                "name" to ColumnType("varchar(65535)", true),
                "updated_at" to ColumnType("timestamptz", true),
            )
        val stream =
            mockStream(
                finalSchema = finalSchema,
                primaryKey = listOf(listOf("id")),
                cursor = listOf("updated_at"),
            )

        val source = TableName(namespace = "ns", name = "staging")
        val target = TableName(namespace = "ns", name = "final")

        val sql = sqlGenerator.upsertTable(stream, source, target)

        assertTrue(sql.contains("WITH deduped_source AS"))
        assertFalse(sql.contains("deleted AS"))
        assertTrue(sql.contains("updates AS"))
        assertTrue(sql.contains("INSERT INTO"))
        assertFalse(sql.contains("_ab_cdc_deleted_at"))
    }

    @Test
    fun `upsertTable without primary key throws IllegalArgumentException`() {
        val streamTableSchema =
            mockk<StreamTableSchema> {
                every { importType } returns Dedupe(primaryKey = emptyList(), cursor = emptyList())
            }
        val stream = mockk<DestinationStream> { every { tableSchema } returns streamTableSchema }

        val exception =
            assertThrows<IllegalArgumentException> {
                sqlGenerator.upsertTable(
                    stream,
                    TableName(namespace = "ns", name = "src"),
                    TableName(namespace = "ns", name = "tgt"),
                )
            }

        assertEquals("Cannot perform upsert without primary key", exception.message)
    }

    // ================================================================
    // Schema evolution: matchSchemas
    // ================================================================

    @Test
    fun `matchSchemas adds columns`() {
        val tableName = TableName(namespace = "ns", name = "tbl")
        val sql =
            sqlGenerator.matchSchemas(
                tableName,
                columnsToAdd =
                    mapOf(
                        "new_col" to ColumnType("varchar(65535)", true),
                        "another_col" to ColumnType("bigint", false),
                    ),
                columnsToRemove = emptyMap(),
                columnsToModify = emptyMap(),
            )

        assertTrue(sql.contains("BEGIN TRANSACTION;"))
        assertTrue(sql.contains("""ALTER TABLE "ns"."tbl" ADD COLUMN "new_col" varchar(65535);"""))
        assertTrue(sql.contains("""ALTER TABLE "ns"."tbl" ADD COLUMN "another_col" bigint;"""))
        assertTrue(sql.contains("COMMIT;"))
    }

    @Test
    fun `matchSchemas removes columns`() {
        val tableName = TableName(namespace = "ns", name = "tbl")
        val sql =
            sqlGenerator.matchSchemas(
                tableName,
                columnsToAdd = emptyMap(),
                columnsToRemove = mapOf("old_col" to ColumnType("varchar", true)),
                columnsToModify = emptyMap(),
            )

        assertTrue(sql.contains("""ALTER TABLE "ns"."tbl" DROP COLUMN "old_col";"""))
    }

    @Test
    fun `matchSchemas SUPER to VARCHAR uses JSON_SERIALIZE`() {
        val tableName = TableName(namespace = "ns", name = "tbl")
        val sql =
            sqlGenerator.matchSchemas(
                tableName,
                columnsToAdd = emptyMap(),
                columnsToRemove = emptyMap(),
                columnsToModify =
                    mapOf(
                        "json_col" to
                            ColumnTypeChange(
                                originalType = ColumnType("super", true),
                                newType = ColumnType("varchar(65535)", true),
                            )
                    ),
            )

        assertTrue(sql.contains("""ADD COLUMN "_airbyte_tmp_json_col" varchar(65535);"""))
        assertTrue(sql.contains("JSON_SERIALIZE(\"json_col\")"))
        assertTrue(sql.contains("""DROP COLUMN "json_col";"""))
        assertTrue(sql.contains("""RENAME COLUMN "_airbyte_tmp_json_col" TO "json_col";"""))
    }

    @Test
    fun `matchSchemas VARCHAR to SUPER uses JSON_PARSE`() {
        val tableName = TableName(namespace = "ns", name = "tbl")
        val sql =
            sqlGenerator.matchSchemas(
                tableName,
                columnsToAdd = emptyMap(),
                columnsToRemove = emptyMap(),
                columnsToModify =
                    mapOf(
                        "data_col" to
                            ColumnTypeChange(
                                originalType = ColumnType("varchar(65535)", true),
                                newType = ColumnType("super", true),
                            )
                    ),
            )

        assertTrue(sql.contains("""ADD COLUMN "_airbyte_tmp_data_col" super;"""))
        assertTrue(sql.contains("JSON_PARSE(\"data_col\")"))
        assertTrue(sql.contains("""DROP COLUMN "data_col";"""))
        assertTrue(sql.contains("""RENAME COLUMN "_airbyte_tmp_data_col" TO "data_col";"""))
    }

    @Test
    fun `matchSchemas generic type change uses CAST`() {
        val tableName = TableName(namespace = "ns", name = "tbl")
        val sql =
            sqlGenerator.matchSchemas(
                tableName,
                columnsToAdd = emptyMap(),
                columnsToRemove = emptyMap(),
                columnsToModify =
                    mapOf(
                        "num_col" to
                            ColumnTypeChange(
                                originalType = ColumnType("bigint", false),
                                newType = ColumnType("numeric(38,9)", false),
                            )
                    ),
            )

        assertTrue(sql.contains("""ADD COLUMN "_airbyte_tmp_num_col" numeric(38,9);"""))
        assertTrue(sql.contains("""CAST("num_col" AS numeric(38,9))"""))
        assertTrue(sql.contains("""DROP COLUMN "num_col";"""))
        assertTrue(sql.contains("""RENAME COLUMN "_airbyte_tmp_num_col" TO "num_col";"""))
    }

    // ================================================================
    // Staging & schema discovery
    // ================================================================

    @Test
    fun `copyFromS3 generates COPY command`() {
        val sql =
            sqlGenerator.copyFromS3(
                tableName = TableName(namespace = "ns", name = "tbl"),
                s3Path = "s3://bucket/path/file.csv.gz",
                accessKeyId = "AKIATEST",
                secretAccessKey = "secret123",
                region = "us-east-1",
            )

        assertTrue(sql.contains("""COPY "ns"."tbl""""))
        assertTrue(sql.contains("FROM 's3://bucket/path/file.csv.gz'"))
        assertTrue(
            sql.contains("CREDENTIALS 'aws_access_key_id=AKIATEST;aws_secret_access_key=secret123'")
        )
        assertTrue(sql.contains("CSV GZIP"))
        assertTrue(sql.contains("REGION 'us-east-1'"))
        assertTrue(sql.contains("TIMEFORMAT 'auto'"))
        assertTrue(sql.contains("IGNOREHEADER 1"))
    }

    @Test
    fun `getTableSchema queries information_schema`() {
        val sql = sqlGenerator.getTableSchema(TableName(namespace = "my_schema", name = "my_table"))

        assertTrue(sql.contains("SELECT column_name, data_type, is_nullable"))
        assertTrue(sql.contains("FROM information_schema.columns"))
        assertTrue(sql.contains("table_schema = 'my_schema'"))
        assertTrue(sql.contains("table_name = 'my_table'"))
        assertTrue(sql.contains("ORDER BY ordinal_position"))
    }

    // ================================================================
    // Edge cases
    // ================================================================

    @Test
    fun `blank namespace defaults to public`() {
        val sql = sqlGenerator.dropTable(TableName(namespace = "", name = "tbl"))
        assertEquals("""DROP TABLE IF EXISTS "public"."tbl";""", sql)
    }
}
