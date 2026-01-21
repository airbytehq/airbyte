/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.sql

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.ColumnTypeChange
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.integrations.destination.postgres.schema.PostgresColumnManager
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
    private lateinit var columnManager: PostgresColumnManager
    private lateinit var postgresConfiguration: PostgresConfiguration

    @BeforeEach
    fun setUp() {
        postgresConfiguration =
            mockk<PostgresConfiguration> {
                every { legacyRawTablesOnly } returns false
                every { dropCascade } returns false
                every { internalTableSchema } returns "airbyte_internal"
                every { schema } returns "public"
            }
        columnManager = PostgresColumnManager(postgresConfiguration)
        postgresDirectLoadSqlGenerator =
            PostgresDirectLoadSqlGenerator(columnManager, postgresConfiguration)
    }

    @Test
    fun testCreateTable() {
        val finalSchema =
            mapOf(
                "targetId" to ColumnType("varchar", true),
                "sourceName" to ColumnType("varchar", false)
            )
        val columnSchema = ColumnSchema(emptyMap(), emptyMap(), finalSchema)
        val streamTableSchema =
            mockk<StreamTableSchema> {
                every { this@mockk.columnSchema } returns columnSchema
                every { getPrimaryKey() } returns emptyList()
                every { getCursor() } returns emptyList()
            }
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
                every { tableSchema } returns streamTableSchema
            }
        val tableName = TableName(namespace = "namespace", name = "name")

        val (createTableSql, createIndexesSql) =
            postgresDirectLoadSqlGenerator.createTable(
                stream = stream,
                tableName = tableName,
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
        val finalSchema = mapOf("targetId" to ColumnType("varchar", true))
        val columnSchema = ColumnSchema(emptyMap(), emptyMap(), finalSchema)
        val streamTableSchema =
            mockk<StreamTableSchema> {
                every { this@mockk.columnSchema } returns columnSchema
                every { getPrimaryKey() } returns emptyList()
                every { getCursor() } returns emptyList()
            }
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
                every { tableSchema } returns streamTableSchema
            }
        val tableName = TableName(namespace = "namespace", name = "name")

        val (createTableSql, createIndexesSql) =
            postgresDirectLoadSqlGenerator.createTable(
                stream = stream,
                tableName = tableName,
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
        val finalSchema =
            mapOf(
                "id" to ColumnType("bigint", true),
                "name" to ColumnType("varchar", true),
                "updatedAt" to ColumnType("timestamp with time zone", true)
            )
        val columnSchema = ColumnSchema(emptyMap(), emptyMap(), finalSchema)
        val streamTableSchema =
            mockk<StreamTableSchema> {
                every { this@mockk.columnSchema } returns columnSchema
                every { getPrimaryKey() } returns listOf(listOf("id"))
                every { getCursor() } returns listOf("updatedAt")
            }
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
                every { tableSchema } returns streamTableSchema
            }
        val tableName = TableName(namespace = "test_schema", name = "test_table")

        val (createTableSql, createIndexesSql) =
            postgresDirectLoadSqlGenerator.createTable(
                stream = stream,
                tableName = tableName,
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
                every { internalTableSchema } returns "airbyte_internal"
                every { schema } returns "public"
            }
        val rawModeColumnManager = PostgresColumnManager(rawModeConfig)
        val rawModeSqlGenerator =
            PostgresDirectLoadSqlGenerator(rawModeColumnManager, rawModeConfig)

        val finalSchema =
            mapOf(
                Meta.COLUMN_NAME_DATA to ColumnType(PostgresDataType.JSONB.typeName, false)
            )
        val columnSchema = ColumnSchema(emptyMap(), emptyMap(), finalSchema)
        val streamTableSchema =
            mockk<StreamTableSchema> {
                every { this@mockk.columnSchema } returns columnSchema
                every { getPrimaryKey() } returns listOf(listOf("id"))
                every { getCursor() } returns listOf("updatedAt")
            }

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
                every { tableSchema } returns streamTableSchema
            }
        val tableName = TableName(namespace = "test_schema", name = "test_table")

        val (createTableSql, createIndexesSql) =
            rawModeSqlGenerator.createTable(
                stream = stream,
                tableName = tableName,
                replace = true
            )

        // In raw mode, table should only have default columns (no user columns like id, name,
        // updatedAt)
        // _airbyte_data is now considered a user column
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
        val columnNames =
            listOf(
                "_airbyte_raw_id",
                "_airbyte_extracted_at",
                "_airbyte_meta",
                "_airbyte_generation_id",
                "targetId"
            )
        val sourceTableName = TableName(namespace = "namespace", name = "source")
        val destinationTableName = TableName(namespace = "namespace", name = "target")

        val sql =
            postgresDirectLoadSqlGenerator.copyTable(
                columnNames = columnNames,
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
    fun testUpsertTable() {
        every { postgresConfiguration.cdcDeletionMode } returns CdcDeletionMode.HARD_DELETE

        val finalSchema =
            mapOf(
                "id" to ColumnType("bigint", false),
                "name" to ColumnType("varchar", true),
                "updatedAt" to ColumnType("timestamp with time zone", true),
                CDC_DELETED_AT_COLUMN to ColumnType("timestamp with time zone", true)
            )
        val columnSchema = ColumnSchema(emptyMap(), emptyMap(), finalSchema)
        val streamTableSchema =
            mockk<StreamTableSchema> {
                every { this@mockk.columnSchema } returns columnSchema
                every { getPrimaryKey() } returns listOf(listOf("id"))
                every { getCursor() } returns listOf("updatedAt")
            }
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
                every { tableSchema } returns streamTableSchema
            }

        val sourceTableName = TableName(namespace = "test_schema", name = "staging_table")
        val targetTableName = TableName(namespace = "test_schema", name = "final_table")

        val sql =
            postgresDirectLoadSqlGenerator.upsertTable(
                stream = stream,
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

        val sourceTableName = TableName(namespace = "test_schema", name = "source_table")
        val targetTableName = TableName(namespace = "test_schema", name = "target_table")

        val exception =
            assertThrows<IllegalArgumentException> {
                postgresDirectLoadSqlGenerator.upsertTable(
                    stream = stream,
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
        val columnsToAdd =
            mapOf(
                "new_column1" to ColumnType("varchar", true),
                "new_column2" to ColumnType("bigint", true)
            )
        val columnsToRemove = emptyMap<String, ColumnType>()
        val columnsToModify = emptyMap<String, ColumnTypeChange>()

        val sql =
            postgresDirectLoadSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
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
        val columnsToAdd = emptyMap<String, ColumnType>()
        val columnsToRemove =
            mapOf(
                "old_column1" to ColumnType("varchar", true),
                "old_column2" to ColumnType("bigint", true)
            )
        val columnsToModify = emptyMap<String, ColumnTypeChange>()

        val sql =
            postgresDirectLoadSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
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
        val columnsToAdd = emptyMap<String, ColumnType>()
        val columnsToRemove = emptyMap<String, ColumnType>()
        val columnsToModify =
            mapOf(
                "column_a" to
                    ColumnTypeChange(
                        originalType = ColumnType("varchar", true),
                        newType = ColumnType("jsonb", true)
                    )
            )

        val sql =
            postgresDirectLoadSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
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
        val columnsToAdd = emptyMap<String, ColumnType>()
        val columnsToRemove = emptyMap<String, ColumnType>()
        val columnsToModify =
            mapOf(
                "column_b" to
                    ColumnTypeChange(
                        originalType = ColumnType("jsonb", true),
                        newType = ColumnType("varchar", true)
                    )
            )

        val sql =
            postgresDirectLoadSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
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
        val columnsToAdd = emptyMap<String, ColumnType>()
        val columnsToRemove = emptyMap<String, ColumnType>()
        val columnsToModify =
            mapOf(
                "column_c" to
                    ColumnTypeChange(
                        originalType = ColumnType("jsonb", true),
                        newType = ColumnType("character varying", true)
                    )
            )

        val sql =
            postgresDirectLoadSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
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
        val columnsToAdd = emptyMap<String, ColumnType>()
        val columnsToRemove = emptyMap<String, ColumnType>()
        val columnsToModify =
            mapOf(
                "column_d" to
                    ColumnTypeChange(
                        originalType = ColumnType("bigint", true),
                        newType = ColumnType("varchar", true)
                    )
            )

        val sql =
            postgresDirectLoadSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
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
        val columnsToAdd = mapOf("new_col" to ColumnType("bigint", true))
        val columnsToRemove = mapOf("old_col" to ColumnType("varchar", true))
        val columnsToModify =
            mapOf(
                "modified_col" to
                    ColumnTypeChange(
                        originalType = ColumnType("varchar", true),
                        newType = ColumnType("jsonb", true)
                    )
            )

        val sql =
            postgresDirectLoadSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
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
        val columnsToAdd = mapOf("new_col" to ColumnType("bigint", true))
        val columnsToRemove = emptyMap<String, ColumnType>()
        val columnsToModify = emptyMap<String, ColumnTypeChange>()
        val primaryKeyColumnNames = listOf("id", "user_id")

        val sql =
            postgresDirectLoadSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
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
        val columnsToAdd = mapOf("new_col" to ColumnType("bigint", true))
        val columnsToRemove = emptyMap<String, ColumnType>()
        val columnsToModify = emptyMap<String, ColumnTypeChange>()
        val cursorColumnName = "updated_at"

        val sql =
            postgresDirectLoadSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
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
        val columnsToAdd = emptyMap<String, ColumnType>()
        val columnsToRemove = emptyMap<String, ColumnType>()
        val columnsToModify =
            mapOf(
                "modified_col" to
                    ColumnTypeChange(
                        originalType = ColumnType("varchar", true),
                        newType = ColumnType("jsonb", true)
                    )
            )
        val primaryKeyColumnNames = listOf("id")
        val cursorColumnName = "updated_at"

        val sql =
            postgresDirectLoadSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
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
                every { internalTableSchema } returns "airbyte_internal"
                every { schema } returns "public"
            }
        val cascadeColumnManager = PostgresColumnManager(cascadeConfig)
        val cascadeSqlGenerator =
            PostgresDirectLoadSqlGenerator(cascadeColumnManager, cascadeConfig)

        val tableName = TableName(namespace = "test_schema", name = "test_table")
        val columnsToAdd = emptyMap<String, ColumnType>()
        val columnsToRemove =
            mapOf(
                "old_column1" to ColumnType("varchar", true),
                "old_column2" to ColumnType("bigint", true)
            )
        val columnsToModify = emptyMap<String, ColumnTypeChange>()

        val sql =
            cascadeSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
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
    fun testMatchSchemasModifyColumnsWithCascadeDoesNotApplyCascade() {
        // CASCADE should NOT be applied to ALTER COLUMN TYPE statements,
        // it only applies to DROP operations (DROP TABLE, DROP INDEX, DROP COLUMN)
        val cascadeConfig =
            mockk<PostgresConfiguration> {
                every { legacyRawTablesOnly } returns false
                every { dropCascade } returns true
                every { internalTableSchema } returns "airbyte_internal"
                every { schema } returns "public"
            }
        val cascadeColumnManager = PostgresColumnManager(cascadeConfig)
        val cascadeSqlGenerator =
            PostgresDirectLoadSqlGenerator(cascadeColumnManager, cascadeConfig)

        val tableName = TableName(namespace = "test_schema", name = "test_table")
        val columnsToAdd = emptyMap<String, ColumnType>()
        val columnsToRemove = emptyMap<String, ColumnType>()
        val columnsToModify =
            mapOf(
                "modified_col" to
                    ColumnTypeChange(
                        originalType = ColumnType("varchar", true),
                        newType = ColumnType("jsonb", true)
                    )
            )

        val sql =
            cascadeSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
                recreatePrimaryKeyIndex = false,
                primaryKeyColumnNames = emptyList(),
                recreateCursorIndex = false,
                cursorColumnName = null
            )

        assert(sql.contains("BEGIN TRANSACTION;"))
        assert(sql.contains("COMMIT;"))
        // CASCADE should NOT be on ALTER COLUMN TYPE
        assert(
            sql.contains(
                "ALTER COLUMN \"modified_col\" TYPE jsonb USING to_jsonb(\"modified_col\");"
            )
        )
        assert(
            !sql.contains(
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
                every { internalTableSchema } returns "airbyte_internal"
                every { schema } returns "public"
            }
        val cascadeColumnManager = PostgresColumnManager(cascadeConfig)
        val cascadeSqlGenerator =
            PostgresDirectLoadSqlGenerator(cascadeColumnManager, cascadeConfig)

        val tableName = TableName(namespace = "test_schema", name = "test_table")
        val columnsToAdd = emptyMap<String, ColumnType>()
        val columnsToRemove = emptyMap<String, ColumnType>()
        val columnsToModify = emptyMap<String, ColumnTypeChange>()
        val primaryKeyColumnNames = listOf("id")
        val cursorColumnName = "updated_at"

        val sql =
            cascadeSqlGenerator.matchSchemas(
                tableName,
                columnsToAdd,
                columnsToRemove,
                columnsToModify,
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
