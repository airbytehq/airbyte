/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.sql

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.postgres.spec.CdcDeletionMode
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

internal class PostgresDirectLoadSqlGeneratorTest {

    private lateinit var postgresDirectLoadSqlGenerator: PostgresDirectLoadSqlGenerator
    private lateinit var columnUtils: PostgresColumnUtils
    private lateinit var postgresConfiguration: PostgresConfiguration

    @BeforeEach
    fun setUp() {
        postgresConfiguration =
            mockk<PostgresConfiguration> {
                every { legacyRawTablesOnly } returns false
                every { dropCascade } returns false
            }
        columnUtils = PostgresColumnUtils(postgresConfiguration)
        postgresDirectLoadSqlGenerator =
            PostgresDirectLoadSqlGenerator(columnUtils, postgresConfiguration)
    }

    @Test
    fun testCreateTable() {
        val stream =
            mockk<DestinationStream> {
                every { schema } returns
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "sourceId" to FieldType(StringType, nullable = true),
                                "sourceName" to FieldType(StringType, nullable = false)
                            )
                    )

                every { importType } returns Append
            }
        val columnNameMapping = ColumnNameMapping(mapOf("sourceId" to "targetId"))
        val tableName = TableName(namespace = "namespace", name = "name")

        val (createTableSql, createIndexesSql) =
            postgresDirectLoadSqlGenerator.createTable(
                stream = stream,
                tableName = tableName,
                columnNameMapping = columnNameMapping,
                replace = true
            )

        val expectedTableSql =
            """
            BEGIN TRANSACTION;
            DROP TABLE IF EXISTS "namespace"."name";
            CREATE TABLE IF NOT EXISTS "namespace"."name" (
            "_airbyte_raw_id" varchar NOT NULL,
            "_airbyte_extracted_at" timestamp with time zone NOT NULL,
            "_airbyte_meta" jsonb NOT NULL,
            "_airbyte_generation_id" bigint NOT NULL,
            "targetId" varchar,
            "sourceName" varchar NOT NULL
            );
            COMMIT;
            """

        val expectedIndexesSql =
            """
            CREATE INDEX IF NOT EXISTS "idx_extracted_at_name" ON "namespace"."name" ("_airbyte_extracted_at");
            """

        assertEqualsIgnoreWhitespace(expectedTableSql, createTableSql)
        assertEqualsIgnoreWhitespace(expectedIndexesSql, createIndexesSql)
    }

    private fun assertEqualsIgnoreWhitespace(expected: String, actual: String) {
        assertEquals(dropWhitespace(expected), dropWhitespace(actual))
    }

    private fun dropWhitespace(text: String) =
        text.lines().map { it.trim() }.filter { it.isNotEmpty() }.joinToString("\n") { it.trim() }

    @Test
    fun testCreateTableNoReplace() {
        val stream =
            mockk<DestinationStream> {
                every { schema } returns
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "sourceId" to FieldType(StringType, nullable = true),
                            )
                    )

                every { importType } returns Append
            }
        val columnNameMapping =
            ColumnNameMapping(
                mapOf(
                    "sourceId" to "targetId",
                )
            )
        val tableName = TableName(namespace = "namespace", name = "name")

        val (createTableSql, createIndexesSql) =
            postgresDirectLoadSqlGenerator.createTable(
                stream = stream,
                tableName = tableName,
                columnNameMapping = columnNameMapping,
                replace = false
            )

        val expectedTableSql =
            """
            BEGIN TRANSACTION;
            CREATE TABLE IF NOT EXISTS "namespace"."name" (
            "_airbyte_raw_id" varchar NOT NULL,
            "_airbyte_extracted_at" timestamp with time zone NOT NULL,
            "_airbyte_meta" jsonb NOT NULL,
            "_airbyte_generation_id" bigint NOT NULL,
            "targetId" varchar
            );
            COMMIT;
            """

        val expectedIndexesSql =
            """
            CREATE INDEX IF NOT EXISTS "idx_extracted_at_name" ON "namespace"."name" ("_airbyte_extracted_at");
            """

        assertEqualsIgnoreWhitespace(expectedTableSql, createTableSql)
        assertEqualsIgnoreWhitespace(expectedIndexesSql, createIndexesSql)
    }

    @Test
    fun testCreateTableWithPrimaryKeysAndCursor() {
        val stream =
            mockk<DestinationStream> {
                every { schema } returns
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "id" to FieldType(IntegerType, nullable = true),
                                "name" to FieldType(StringType, nullable = true),
                                "updatedAt" to FieldType(TimestampTypeWithTimezone, nullable = true)
                            )
                    )
                every { importType } returns
                    Dedupe(primaryKey = listOf(listOf("id")), cursor = listOf("updatedAt"))
            }
        val columnNameMapping = ColumnNameMapping(emptyMap())
        val tableName = TableName(namespace = "test_schema", name = "test_table")

        val (createTableSql, createIndexesSql) =
            postgresDirectLoadSqlGenerator.createTable(
                stream = stream,
                tableName = tableName,
                columnNameMapping = columnNameMapping,
                replace = true
            )

        val expectedTableSql =
            """
            BEGIN TRANSACTION;
            DROP TABLE IF EXISTS "test_schema"."test_table";
            CREATE TABLE IF NOT EXISTS "test_schema"."test_table" (
            "_airbyte_raw_id" varchar NOT NULL,
            "_airbyte_extracted_at" timestamp with time zone NOT NULL,
            "_airbyte_meta" jsonb NOT NULL,
            "_airbyte_generation_id" bigint NOT NULL,
            "id" bigint,
            "name" varchar,
            "updatedAt" timestamp with time zone
            );
            COMMIT;
            """

        val expectedIndexesSql =
            """
            CREATE INDEX IF NOT EXISTS "idx_pk_test_table" ON "test_schema"."test_table" ("id");
            CREATE INDEX IF NOT EXISTS "idx_cursor_test_table" ON "test_schema"."test_table" ("updatedAt");
            CREATE INDEX IF NOT EXISTS "idx_extracted_at_test_table" ON "test_schema"."test_table" ("_airbyte_extracted_at");
            """

        assertEqualsIgnoreWhitespace(expectedTableSql, createTableSql)
        assertEqualsIgnoreWhitespace(expectedIndexesSql, createIndexesSql)
    }

    @Test
    fun testCreateTableWithPrimaryKeysAndCursorInRawMode() {
        // Setup config with legacyRawTablesOnly = true
        val rawModeConfig =
            mockk<PostgresConfiguration> {
                every { legacyRawTablesOnly } returns true
                every { dropCascade } returns false
            }
        val rawModeColumnUtils = PostgresColumnUtils(rawModeConfig)
        val rawModeSqlGenerator = PostgresDirectLoadSqlGenerator(rawModeColumnUtils, rawModeConfig)

        val stream =
            mockk<DestinationStream> {
                every { schema } returns
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "id" to FieldType(IntegerType, nullable = true),
                                "name" to FieldType(StringType, nullable = true),
                                "updatedAt" to FieldType(TimestampTypeWithTimezone, nullable = true)
                            )
                    )
                every { importType } returns
                    Dedupe(primaryKey = listOf(listOf("id")), cursor = listOf("updatedAt"))
            }
        val columnNameMapping = ColumnNameMapping(emptyMap())
        val tableName = TableName(namespace = "test_schema", name = "test_table")

        val (createTableSql, createIndexesSql) =
            rawModeSqlGenerator.createTable(
                stream = stream,
                tableName = tableName,
                columnNameMapping = columnNameMapping,
                replace = true
            )

        // In raw mode, table should only have default columns (no user columns like id, name,
        // updatedAt)
        val expectedTableSql =
            """
            BEGIN TRANSACTION;
            DROP TABLE IF EXISTS "test_schema"."test_table";
            CREATE TABLE IF NOT EXISTS "test_schema"."test_table" (
            "_airbyte_raw_id" varchar NOT NULL,
            "_airbyte_extracted_at" timestamp with time zone NOT NULL,
            "_airbyte_meta" jsonb NOT NULL,
            "_airbyte_generation_id" bigint NOT NULL,
            "_airbyte_loaded_at" timestamp with time zone,
            "_airbyte_data" jsonb NOT NULL
            );
            COMMIT;
            """

        // In raw mode, only extracted_at index should be created (no pk or cursor indexes)
        val expectedIndexesSql =
            """
            CREATE INDEX IF NOT EXISTS "idx_extracted_at_test_table" ON "test_schema"."test_table" ("_airbyte_extracted_at");
            """

        assertEqualsIgnoreWhitespace(expectedTableSql, createTableSql)
        assertEqualsIgnoreWhitespace(expectedIndexesSql, createIndexesSql)
    }

    @Test
    fun testOverwriteTable() {
        val sourceTableName = TableName(namespace = "namespace", name = "source")
        val targetTableName = TableName(namespace = "namespace", name = "target")
        val sql = postgresDirectLoadSqlGenerator.overwriteTable(sourceTableName, targetTableName)

        val expected =
            """
            BEGIN TRANSACTION;
            DROP TABLE IF EXISTS "namespace"."target";
            ALTER TABLE "namespace"."source" RENAME TO "target";
            COMMIT;
        """

        assertEqualsWithTrimIndent(expected, sql)
    }

    private fun assertEqualsWithTrimIndent(expected: String, actual: String) {
        assertEquals(expected.trimIndent(), actual.trimIndent())
    }

    @Test
    fun testGenerateCopyTable() {
        val columnNameMapping = ColumnNameMapping(mapOf("sourceId" to "targetId"))
        val sourceTableName = TableName(namespace = "namespace", name = "source")
        val destinationTableName = TableName(namespace = "namespace", name = "target")

        val sql =
            postgresDirectLoadSqlGenerator.copyTable(
                columnNameMapping = columnNameMapping,
                sourceTableName = sourceTableName,
                targetTableName = destinationTableName
            )

        val expected =
            """
            INSERT INTO "namespace"."target" ("_airbyte_raw_id","_airbyte_extracted_at","_airbyte_meta","_airbyte_generation_id","targetId")
            SELECT "_airbyte_raw_id","_airbyte_extracted_at","_airbyte_meta","_airbyte_generation_id","targetId"
            FROM "namespace"."source";
        """

        assertEqualsWithTrimIndent(expected, sql)
    }

    @Test
    fun testDropTable() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val sql = postgresDirectLoadSqlGenerator.dropTable(tableName)
        assertEquals("DROP TABLE IF EXISTS \"namespace\".\"name\";", sql)
    }

    @Test
    fun testCountTable() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val sql = postgresDirectLoadSqlGenerator.countTable(tableName)
        assertEquals("SELECT COUNT(*) AS \"total\" FROM \"namespace\".\"name\";", sql)
    }

    @Test
    fun testCreateNamespace() {
        val namespace = "namespace"
        val sql = postgresDirectLoadSqlGenerator.createNamespace(namespace)
        assertEquals("CREATE SCHEMA IF NOT EXISTS \"namespace\";", sql)
    }

    @Test
    fun testGetGenerationId() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val sql = postgresDirectLoadSqlGenerator.getGenerationId(tableName = tableName)
        assertEquals("SELECT \"_airbyte_generation_id\" FROM \"namespace\".\"name\" LIMIT 1;", sql)
    }

    @Test
    fun testColumnAndTypeToString() {
        with(postgresDirectLoadSqlGenerator) {
            val column = Column("column", "varchar", nullable = false)
            assertEquals("\"column\" varchar NOT NULL", column.toSQLString())
        }
    }

    @Test
    fun testNullableColumnAndTypeToString() {
        with(postgresDirectLoadSqlGenerator) {
            val nullableColumn = Column("column", "varchar", nullable = true)
            assertEquals("\"column\" varchar", nullableColumn.toSQLString())
        }
    }

    @Test
    fun testUpsertTable() {
        every { postgresConfiguration.cdcDeletionMode } returns CdcDeletionMode.HARD_DELETE

        val stream =
            mockk<DestinationStream> {
                every { schema } returns
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "id" to FieldType(IntegerType, nullable = false),
                                "name" to FieldType(StringType, nullable = true),
                                "updatedAt" to
                                    FieldType(TimestampTypeWithTimezone, nullable = true),
                                CDC_DELETED_AT_COLUMN to
                                    FieldType(TimestampTypeWithTimezone, nullable = true)
                            )
                    )
                every { importType } returns
                    Dedupe(primaryKey = listOf(listOf("id")), cursor = listOf("updatedAt"))
            }

        val columnNameMapping = ColumnNameMapping(emptyMap())
        val sourceTableName = TableName(namespace = "test_schema", name = "staging_table")
        val targetTableName = TableName(namespace = "test_schema", name = "final_table")

        val sql =
            postgresDirectLoadSqlGenerator.upsertTable(
                stream = stream,
                columnNameMapping = columnNameMapping,
                sourceTableName = sourceTableName,
                targetTableName = targetTableName
            )

        val expected =
            """
            WITH deduped_source AS (
            SELECT "_airbyte_raw_id", "_airbyte_extracted_at", "_airbyte_meta", "_airbyte_generation_id", "id", "name", "updatedAt", "_ab_cdc_deleted_at"
            FROM (
            SELECT *,
            ROW_NUMBER() OVER (
            PARTITION BY "id"
            ORDER BY
            "updatedAt" DESC NULLS LAST, "_airbyte_extracted_at" DESC
            ) AS row_number
            FROM "test_schema"."staging_table"
            ) AS deduplicated
            WHERE row_number = 1
            ),

            deleted AS (
            DELETE FROM "test_schema"."final_table"
            USING deduped_source
            WHERE "test_schema"."final_table"."id" = deduped_source."id"
            AND deduped_source."_ab_cdc_deleted_at" IS NOT NULL
            AND (
            "test_schema"."final_table"."updatedAt" < deduped_source."updatedAt"
            OR ("test_schema"."final_table"."updatedAt" = deduped_source."updatedAt" AND "test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at")
            OR ("test_schema"."final_table"."updatedAt" IS NULL AND deduped_source."updatedAt" IS NOT NULL)
            OR ("test_schema"."final_table"."updatedAt" IS NULL AND deduped_source."updatedAt" IS NULL AND "test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at")
            )
            ),

            updates AS (
            UPDATE "test_schema"."final_table"
            SET
            "_airbyte_raw_id" = deduped_source."_airbyte_raw_id",
            "_airbyte_extracted_at" = deduped_source."_airbyte_extracted_at",
            "_airbyte_meta" = deduped_source."_airbyte_meta",
            "_airbyte_generation_id" = deduped_source."_airbyte_generation_id",
            "id" = deduped_source."id",
            "name" = deduped_source."name",
            "updatedAt" = deduped_source."updatedAt",
            "_ab_cdc_deleted_at" = deduped_source."_ab_cdc_deleted_at"
            FROM deduped_source
            WHERE "test_schema"."final_table"."id" = deduped_source."id"
            AND deduped_source."_ab_cdc_deleted_at" IS NULL
            AND (
            "test_schema"."final_table"."updatedAt" < deduped_source."updatedAt"
            OR ("test_schema"."final_table"."updatedAt" = deduped_source."updatedAt" AND "test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at")
            OR ("test_schema"."final_table"."updatedAt" IS NULL AND deduped_source."updatedAt" IS NOT NULL)
            OR ("test_schema"."final_table"."updatedAt" IS NULL AND deduped_source."updatedAt" IS NULL AND "test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at")
            )
            )

            INSERT INTO "test_schema"."final_table" (
            "_airbyte_raw_id",
            "_airbyte_extracted_at",
            "_airbyte_meta",
            "_airbyte_generation_id",
            "id",
            "name",
            "updatedAt",
            "_ab_cdc_deleted_at"
            )
            SELECT
            "_airbyte_raw_id",
            "_airbyte_extracted_at",
            "_airbyte_meta",
            "_airbyte_generation_id",
            "id",
            "name",
            "updatedAt",
            "_ab_cdc_deleted_at"
            FROM deduped_source
            WHERE
            NOT EXISTS (
            SELECT 1
            FROM "test_schema"."final_table"
            WHERE "test_schema"."final_table"."id" = deduped_source."id"
            )
            AND deduped_source."_ab_cdc_deleted_at" IS NULL
            """

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testUpsertTableWithoutPrimaryKeyThrowsException() {
        val stream =
            mockk<DestinationStream> {
                every { importType } returns Dedupe(primaryKey = emptyList(), cursor = emptyList())
            }

        val columnNameMapping = ColumnNameMapping(emptyMap())
        val sourceTableName = TableName(namespace = "test_schema", name = "source_table")
        val targetTableName = TableName(namespace = "test_schema", name = "target_table")

        val exception =
            assertThrows<IllegalArgumentException> {
                postgresDirectLoadSqlGenerator.upsertTable(
                    stream = stream,
                    columnNameMapping = columnNameMapping,
                    sourceTableName = sourceTableName,
                    targetTableName = targetTableName
                )
            }

        assertEquals("Cannot perform upsert without primary key", exception.message)
    }

    @Test
    fun testSelectDedupedWithCursor() {
        val primaryKeyColumns = listOf("id")
        val cursorColumn = "updatedAt"
        val allColumns = listOf("id", "name", "updatedAt", "_airbyte_extracted_at")
        val sourceTable = TableName(namespace = "test_schema", name = "staging_table")

        val sql =
            postgresDirectLoadSqlGenerator.selectDeduped(
                primaryKeyColumns,
                cursorColumn,
                allColumns,
                sourceTable
            )

        val expected =
            """
            SELECT id, name, updatedAt, _airbyte_extracted_at
            FROM (
            SELECT *,
            ROW_NUMBER() OVER (
            PARTITION BY id
            ORDER BY
            updatedAt DESC NULLS LAST, "_airbyte_extracted_at" DESC
            ) AS row_number
            FROM "test_schema"."staging_table"
            ) AS deduplicated
            WHERE row_number = 1
            """

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testSelectDedupedWithoutCursor() {
        val primaryKeyColumns = listOf("id")
        val allColumns = listOf("id", "name", "updatedAt", "_airbyte_extracted_at")
        val sourceTable = TableName(namespace = "test_schema", name = "staging_table")

        val sql =
            postgresDirectLoadSqlGenerator.selectDeduped(
                primaryKeyColumns,
                null,
                allColumns,
                sourceTable
            )

        val expected =
            """
            SELECT id, name, updatedAt, _airbyte_extracted_at
            FROM (
            SELECT *,
            ROW_NUMBER() OVER (
            PARTITION BY id
            ORDER BY
            "_airbyte_extracted_at" DESC
            ) AS row_number
            FROM "test_schema"."staging_table"
            ) AS deduplicated
            WHERE row_number = 1
            """

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testCdcDeleteWithCursor() {
        val dedupTableAlias = "deduped_source"
        val cursorColumn = "updatedAt"
        val targetTable = TableName(namespace = "test_schema", name = "final_table")
        val primaryKeyColumns = listOf("id")

        val sql =
            postgresDirectLoadSqlGenerator.cdcDelete(
                dedupTableAlias,
                cursorColumn,
                targetTable,
                primaryKeyColumns,
                true
            )

        val expected =
            """
            deleted AS (
            DELETE FROM "test_schema"."final_table"
            USING deduped_source
            WHERE "test_schema"."final_table".id = deduped_source.id
            AND deduped_source."_ab_cdc_deleted_at" IS NOT NULL
            AND (
            "test_schema"."final_table".updatedAt < deduped_source.updatedAt
            OR ("test_schema"."final_table".updatedAt = deduped_source.updatedAt AND "test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at")
            OR ("test_schema"."final_table".updatedAt IS NULL AND deduped_source.updatedAt IS NOT NULL)
            OR ("test_schema"."final_table".updatedAt IS NULL AND deduped_source.updatedAt IS NULL AND "test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at")
            )
            ),
            """

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testCdcDeleteWithoutCursor() {
        val dedupTableAlias = "deduped_source"
        val targetTable = TableName(namespace = "test_schema", name = "final_table")
        val primaryKeyColumns = listOf("id")

        val sql =
            postgresDirectLoadSqlGenerator.cdcDelete(
                dedupTableAlias,
                null,
                targetTable,
                primaryKeyColumns,
                true
            )

        val expected =
            """
            deleted AS (
            DELETE FROM "test_schema"."final_table"
            USING deduped_source
            WHERE "test_schema"."final_table".id = deduped_source.id
            AND deduped_source."_ab_cdc_deleted_at" IS NOT NULL
            AND ("test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at")
            ),
            """

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testCdcDeleteDisabled() {
        val dedupTableAlias = "deduped_source"
        val targetTable = TableName(namespace = "test_schema", name = "final_table")
        val primaryKeyColumns = listOf("id")

        val sql =
            postgresDirectLoadSqlGenerator.cdcDelete(
                dedupTableAlias,
                "updatedAt",
                targetTable,
                primaryKeyColumns,
                false
            )

        assertEquals("", sql)
    }

    @Test
    fun testUpdateExistingRows() {
        val dedupTableAlias = "deduped_source"
        val targetTable = TableName(namespace = "test_schema", name = "final_table")
        val allColumns = listOf("id", "name")
        val primaryKeyColumns = listOf("id")

        val sql =
            postgresDirectLoadSqlGenerator.updateExistingRows(
                dedupTableAlias,
                targetTable,
                allColumns,
                primaryKeyColumns,
                null,
                false
            )

        val expected =
            """
            UPDATE "test_schema"."final_table"
            SET
            id = deduped_source.id,
            name = deduped_source.name
            FROM deduped_source
            WHERE "test_schema"."final_table".id = deduped_source.id
            AND ("test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at")
            """

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testUpdateExistingRowsWithCursor() {
        val dedupTableAlias = "deduped_source"
        val targetTable = TableName(namespace = "test_schema", name = "final_table")
        val allColumns = listOf("id", "name", "updatedAt")
        val primaryKeyColumns = listOf("id")
        val cursorColumn = "updatedAt"

        val sql =
            postgresDirectLoadSqlGenerator.updateExistingRows(
                dedupTableAlias,
                targetTable,
                allColumns,
                primaryKeyColumns,
                cursorColumn,
                false
            )

        val expected =
            """
            UPDATE "test_schema"."final_table"
            SET
            id = deduped_source.id,
            name = deduped_source.name,
            updatedAt = deduped_source.updatedAt
            FROM deduped_source
            WHERE "test_schema"."final_table".id = deduped_source.id
            AND (
            "test_schema"."final_table".updatedAt < deduped_source.updatedAt
            OR ("test_schema"."final_table".updatedAt = deduped_source.updatedAt AND "test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at")
            OR ("test_schema"."final_table".updatedAt IS NULL AND deduped_source.updatedAt IS NOT NULL)
            OR ("test_schema"."final_table".updatedAt IS NULL AND deduped_source.updatedAt IS NULL AND "test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at")
            )
            """

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testUpdateExistingRowsWithCdcDelete() {
        val dedupTableAlias = "deduped_source"
        val targetTable = TableName(namespace = "test_schema", name = "final_table")
        val allColumns = listOf("id", "name")
        val primaryKeyColumns = listOf("id")

        val sql =
            postgresDirectLoadSqlGenerator.updateExistingRows(
                dedupTableAlias,
                targetTable,
                allColumns,
                primaryKeyColumns,
                null,
                true
            )

        val expected =
            """
            UPDATE "test_schema"."final_table"
            SET
            id = deduped_source.id,
            name = deduped_source.name
            FROM deduped_source
            WHERE "test_schema"."final_table".id = deduped_source.id
            AND deduped_source."_ab_cdc_deleted_at" IS NULL
            AND ("test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at")
            """

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testInsertNewRows() {
        val dedupTableAlias = "deduped_source"
        val targetTable = TableName(namespace = "test_schema", name = "final_table")
        val allColumns = listOf("id", "name")
        val primaryKeyColumns = listOf("id")

        val sql =
            postgresDirectLoadSqlGenerator.insertNewRows(
                dedupTableAlias,
                targetTable,
                allColumns,
                primaryKeyColumns,
                false
            )

        val expected =
            """
            INSERT INTO "test_schema"."final_table" (
            id,
            name
            )
            SELECT
            id,
            name
            FROM deduped_source
            WHERE
            NOT EXISTS (
            SELECT 1
            FROM "test_schema"."final_table"
            WHERE "test_schema"."final_table".id = deduped_source.id
            )
            """

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testInsertNewRowsWithCdcDelete() {
        val dedupTableAlias = "deduped_source"
        val targetTable = TableName(namespace = "test_schema", name = "final_table")
        val allColumns = listOf("id", "name")
        val primaryKeyColumns = listOf("id")

        val sql =
            postgresDirectLoadSqlGenerator.insertNewRows(
                dedupTableAlias,
                targetTable,
                allColumns,
                primaryKeyColumns,
                true
            )

        val expected =
            """
            INSERT INTO "test_schema"."final_table" (
            id,
            name
            )
            SELECT
            id,
            name
            FROM deduped_source
            WHERE
            NOT EXISTS (
            SELECT 1
            FROM "test_schema"."final_table"
            WHERE "test_schema"."final_table".id = deduped_source.id
            )
            AND deduped_source."_ab_cdc_deleted_at" IS NULL
            """

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testMatchSchemasAddColumns() {
        val tableName = TableName(namespace = "test_schema", name = "test_table")
        val columnsToAdd = setOf(Column("new_column1", "varchar"), Column("new_column2", "bigint"))
        val columnsToRemove = emptySet<Column>()
        val columnsToModify = emptySet<Column>()
        val columnsInDb = emptySet<Column>()

        val sql =
            postgresDirectLoadSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
                columnsInDb,
                recreatePrimaryKeyIndex = false,
                primaryKeyColumnNames = emptyList(),
                recreateCursorIndex = false,
                cursorColumnName = null
            )

        assert(sql.contains("BEGIN TRANSACTION;"))
        assert(sql.contains("COMMIT;"))
        assert(sql.contains("ADD COLUMN \"new_column1\" varchar"))
        assert(sql.contains("ADD COLUMN \"new_column2\" bigint"))
    }

    @Test
    fun testMatchSchemasRemoveColumns() {
        val tableName = TableName(namespace = "test_schema", name = "test_table")
        val columnsToAdd = emptySet<Column>()
        val columnsToRemove =
            setOf(Column("old_column1", "varchar"), Column("old_column2", "bigint"))
        val columnsToModify = emptySet<Column>()
        val columnsInDb = setOf(Column("old_column1", "varchar"), Column("old_column2", "bigint"))

        val sql =
            postgresDirectLoadSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
                columnsInDb,
                recreatePrimaryKeyIndex = false,
                primaryKeyColumnNames = emptyList(),
                recreateCursorIndex = false,
                cursorColumnName = null
            )

        assert(sql.contains("BEGIN TRANSACTION;"))
        assert(sql.contains("COMMIT;"))
        assert(sql.contains("DROP COLUMN \"old_column1\""))
        assert(sql.contains("DROP COLUMN \"old_column2\""))
    }

    @Test
    fun testMatchSchemasModifyColumnToJsonb() {
        val tableName = TableName(namespace = "test_schema", name = "test_table")
        val columnsToAdd = emptySet<Column>()
        val columnsToRemove = emptySet<Column>()
        val columnsToModify = setOf(Column("column_a", "jsonb"))
        val columnsInDb = setOf(Column("column_a", "varchar"))

        val sql =
            postgresDirectLoadSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
                columnsInDb,
                recreatePrimaryKeyIndex = false,
                primaryKeyColumnNames = emptyList(),
                recreateCursorIndex = false,
                cursorColumnName = null
            )

        assert(sql.contains("ALTER COLUMN \"column_a\" TYPE jsonb"))
        assert(sql.contains("USING to_jsonb(\"column_a\")"))
    }

    @Test
    fun testMatchSchemasModifyColumnFromJsonbToVarchar() {
        val tableName = TableName(namespace = "test_schema", name = "test_table")
        val columnsToAdd = emptySet<Column>()
        val columnsToRemove = emptySet<Column>()
        val columnsToModify = setOf(Column("column_b", "varchar"))
        val columnsInDb = setOf(Column("column_b", "jsonb"))

        val sql =
            postgresDirectLoadSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
                columnsInDb,
                recreatePrimaryKeyIndex = false,
                primaryKeyColumnNames = emptyList(),
                recreateCursorIndex = false,
                cursorColumnName = null
            )

        assert(sql.contains("ALTER COLUMN \"column_b\" TYPE varchar"))
        assert(sql.contains("USING \"column_b\" #>> '{}'"))
    }

    @Test
    fun testMatchSchemasModifyColumnFromJsonbToCharacterVarying() {
        val tableName = TableName(namespace = "test_schema", name = "test_table")
        val columnsToAdd = emptySet<Column>()
        val columnsToRemove = emptySet<Column>()
        val columnsToModify = setOf(Column("column_c", "character varying"))
        val columnsInDb = setOf(Column("column_c", "jsonb"))

        val sql =
            postgresDirectLoadSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
                columnsInDb,
                recreatePrimaryKeyIndex = false,
                primaryKeyColumnNames = emptyList(),
                recreateCursorIndex = false,
                cursorColumnName = null
            )

        assert(sql.contains("ALTER COLUMN \"column_c\" TYPE character varying"))
        assert(sql.contains("USING \"column_c\" #>> '{}'"))
    }

    @Test
    fun testMatchSchemasModifyColumnStandardCast() {
        val tableName = TableName(namespace = "test_schema", name = "test_table")
        val columnsToAdd = emptySet<Column>()
        val columnsToRemove = emptySet<Column>()
        val columnsToModify = setOf(Column("column_d", "varchar"))
        val columnsInDb = setOf(Column("column_d", "bigint"))

        val sql =
            postgresDirectLoadSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
                columnsInDb,
                recreatePrimaryKeyIndex = false,
                primaryKeyColumnNames = emptyList(),
                recreateCursorIndex = false,
                cursorColumnName = null
            )

        assert(sql.contains("ALTER COLUMN \"column_d\" TYPE varchar"))
        assert(sql.contains("USING \"column_d\"::varchar"))
    }

    @Test
    fun testMatchSchemasCombinedOperations() {
        val tableName = TableName(namespace = "test_schema", name = "test_table")
        val columnsToAdd = setOf(Column("new_col", "bigint"))
        val columnsToRemove = setOf(Column("old_col", "varchar"))
        val columnsToModify = setOf(Column("modified_col", "jsonb"))
        val columnsInDb = setOf(Column("old_col", "varchar"), Column("modified_col", "varchar"))

        val sql =
            postgresDirectLoadSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
                columnsInDb,
                recreatePrimaryKeyIndex = false,
                primaryKeyColumnNames = emptyList(),
                recreateCursorIndex = false,
                cursorColumnName = null
            )

        assert(sql.contains("BEGIN TRANSACTION;"))
        assert(sql.contains("COMMIT;"))
        assert(sql.contains("ADD COLUMN \"new_col\" bigint"))
        assert(sql.contains("DROP COLUMN \"old_col\""))
        assert(sql.contains("ALTER COLUMN \"modified_col\" TYPE jsonb"))
    }

    @Test
    fun testMatchSchemasWithPrimaryKeyIndexRecreation() {
        val tableName = TableName(namespace = "test_schema", name = "test_table")
        val columnsToAdd = setOf(Column("new_col", "bigint"))
        val columnsToRemove = emptySet<Column>()
        val columnsToModify = emptySet<Column>()
        val columnsInDb = emptySet<Column>()
        val primaryKeyColumnNames = listOf("id", "user_id")

        val sql =
            postgresDirectLoadSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
                columnsInDb,
                recreatePrimaryKeyIndex = true,
                primaryKeyColumnNames = primaryKeyColumnNames,
                recreateCursorIndex = false,
                cursorColumnName = null
            )

        assert(sql.contains("BEGIN TRANSACTION;"))
        assert(sql.contains("COMMIT;"))
        assert(sql.contains("ADD COLUMN \"new_col\" bigint"))
        assert(sql.contains("DROP INDEX IF EXISTS \"test_schema\".\"idx_pk_test_table\""))
        assert(
            sql.contains(
                "CREATE INDEX IF NOT EXISTS \"idx_pk_test_table\" ON \"test_schema\".\"test_table\" (\"id\", \"user_id\")"
            )
        )
    }

    @Test
    fun testMatchSchemasWithCursorIndexRecreation() {
        val tableName = TableName(namespace = "test_schema", name = "test_table")
        val columnsToAdd = setOf(Column("new_col", "bigint"))
        val columnsToRemove = emptySet<Column>()
        val columnsToModify = emptySet<Column>()
        val columnsInDb = emptySet<Column>()
        val cursorColumnName = "updated_at"

        val sql =
            postgresDirectLoadSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
                columnsInDb,
                recreatePrimaryKeyIndex = false,
                primaryKeyColumnNames = emptyList(),
                recreateCursorIndex = true,
                cursorColumnName = cursorColumnName
            )

        assert(sql.contains("BEGIN TRANSACTION;"))
        assert(sql.contains("COMMIT;"))
        assert(sql.contains("ADD COLUMN \"new_col\" bigint"))
        assert(sql.contains("DROP INDEX IF EXISTS \"test_schema\".\"idx_cursor_test_table\""))
        assert(
            sql.contains(
                "CREATE INDEX IF NOT EXISTS \"idx_cursor_test_table\" ON \"test_schema\".\"test_table\" (\"updated_at\")"
            )
        )
    }

    @Test
    fun testMatchSchemasWithBothIndexRecreations() {
        val tableName = TableName(namespace = "test_schema", name = "test_table")
        val columnsToAdd = emptySet<Column>()
        val columnsToRemove = emptySet<Column>()
        val columnsToModify = setOf(Column("modified_col", "jsonb"))
        val columnsInDb = setOf(Column("modified_col", "varchar"))
        val primaryKeyColumnNames = listOf("id")
        val cursorColumnName = "updated_at"

        val sql =
            postgresDirectLoadSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
                columnsInDb,
                recreatePrimaryKeyIndex = true,
                primaryKeyColumnNames = primaryKeyColumnNames,
                recreateCursorIndex = true,
                cursorColumnName = cursorColumnName
            )

        assert(sql.contains("BEGIN TRANSACTION;"))
        assert(sql.contains("COMMIT;"))
        assert(sql.contains("ALTER COLUMN \"modified_col\" TYPE jsonb"))
        assert(sql.contains("DROP INDEX IF EXISTS \"test_schema\".\"idx_pk_test_table\""))
        assert(
            sql.contains(
                "CREATE INDEX IF NOT EXISTS \"idx_pk_test_table\" ON \"test_schema\".\"test_table\" (\"id\")"
            )
        )
        assert(sql.contains("DROP INDEX IF EXISTS \"test_schema\".\"idx_cursor_test_table\""))
        assert(
            sql.contains(
                "CREATE INDEX IF NOT EXISTS \"idx_cursor_test_table\" ON \"test_schema\".\"test_table\" (\"updated_at\")"
            )
        )
    }

    @Test
    fun testMatchSchemasRemoveColumnsWithCascade() {
        val cascadeConfig =
            mockk<PostgresConfiguration> {
                every { legacyRawTablesOnly } returns false
                every { dropCascade } returns true
            }
        val cascadeColumnUtils = PostgresColumnUtils(cascadeConfig)
        val cascadeSqlGenerator = PostgresDirectLoadSqlGenerator(cascadeColumnUtils, cascadeConfig)

        val tableName = TableName(namespace = "test_schema", name = "test_table")
        val columnsToAdd = emptySet<Column>()
        val columnsToRemove =
            setOf(Column("old_column1", "varchar"), Column("old_column2", "bigint"))
        val columnsToModify = emptySet<Column>()
        val columnsInDb = setOf(Column("old_column1", "varchar"), Column("old_column2", "bigint"))

        val sql =
            cascadeSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
                columnsInDb,
                recreatePrimaryKeyIndex = false,
                primaryKeyColumnNames = emptyList(),
                recreateCursorIndex = false,
                cursorColumnName = null
            )

        assert(sql.contains("BEGIN TRANSACTION;"))
        assert(sql.contains("COMMIT;"))
        assert(sql.contains("DROP COLUMN \"old_column1\" CASCADE"))
        assert(sql.contains("DROP COLUMN \"old_column2\" CASCADE"))
    }

    @Test
    fun testMatchSchemasModifyColumnsWithCascade() {
        val cascadeConfig =
            mockk<PostgresConfiguration> {
                every { legacyRawTablesOnly } returns false
                every { dropCascade } returns true
            }
        val cascadeColumnUtils = PostgresColumnUtils(cascadeConfig)
        val cascadeSqlGenerator = PostgresDirectLoadSqlGenerator(cascadeColumnUtils, cascadeConfig)

        val tableName = TableName(namespace = "test_schema", name = "test_table")
        val columnsToAdd = emptySet<Column>()
        val columnsToRemove = emptySet<Column>()
        val columnsToModify = setOf(Column("modified_col", "jsonb"))
        val columnsInDb = setOf(Column("modified_col", "varchar"))

        val sql =
            cascadeSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
                columnsInDb,
                recreatePrimaryKeyIndex = false,
                primaryKeyColumnNames = emptyList(),
                recreateCursorIndex = false,
                cursorColumnName = null
            )

        assert(sql.contains("BEGIN TRANSACTION;"))
        assert(sql.contains("COMMIT;"))
        assert(
            sql.contains(
                "ALTER COLUMN \"modified_col\" TYPE jsonb USING to_jsonb(\"modified_col\") CASCADE"
            )
        )
    }

    @Test
    fun testMatchSchemasDropIndexWithCascade() {
        val cascadeConfig =
            mockk<PostgresConfiguration> {
                every { legacyRawTablesOnly } returns false
                every { dropCascade } returns true
            }
        val cascadeColumnUtils = PostgresColumnUtils(cascadeConfig)
        val cascadeSqlGenerator = PostgresDirectLoadSqlGenerator(cascadeColumnUtils, cascadeConfig)

        val tableName = TableName(namespace = "test_schema", name = "test_table")
        val columnsToAdd = emptySet<Column>()
        val columnsToRemove = emptySet<Column>()
        val columnsToModify = emptySet<Column>()
        val columnsInDb = emptySet<Column>()
        val primaryKeyColumnNames = listOf("id")
        val cursorColumnName = "updated_at"

        val sql =
            cascadeSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
                columnsInDb,
                recreatePrimaryKeyIndex = true,
                primaryKeyColumnNames = primaryKeyColumnNames,
                recreateCursorIndex = true,
                cursorColumnName = cursorColumnName
            )

        // Verify DROP INDEX statements include CASCADE
        assert(sql.contains("DROP INDEX IF EXISTS \"test_schema\".\"idx_pk_test_table\" CASCADE"))
        assert(
            sql.contains("DROP INDEX IF EXISTS \"test_schema\".\"idx_cursor_test_table\" CASCADE")
        )
        // Verify CREATE INDEX statements are still present
        assert(
            sql.contains(
                "CREATE INDEX IF NOT EXISTS \"idx_pk_test_table\" ON \"test_schema\".\"test_table\" (\"id\")"
            )
        )
        assert(
            sql.contains(
                "CREATE INDEX IF NOT EXISTS \"idx_cursor_test_table\" ON \"test_schema\".\"test_table\" (\"updated_at\")"
            )
        )
    }
}
