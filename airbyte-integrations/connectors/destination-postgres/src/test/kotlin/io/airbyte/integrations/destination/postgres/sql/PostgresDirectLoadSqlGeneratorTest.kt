/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.sql

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
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
    private val postgresConfiguration: PostgresConfiguration = mockk()

    @BeforeEach
    fun setUp() {
        postgresDirectLoadSqlGenerator = PostgresDirectLoadSqlGenerator(postgresConfiguration)
    }

    @Test
    fun testCreateTable() {
        val stream = mockk<DestinationStream> {
            every { schema } returns ObjectType(
                properties = linkedMapOf(
                    "sourceId" to FieldType(StringType, nullable = false),
                    "sourceName" to FieldType(StringType, nullable = false)
                )
            )

            every { importType } returns Append
        }
        val columnNameMapping = ColumnNameMapping(
            mapOf(
                "sourceId" to "targetId"
            )
        )
        val tableName = TableName(namespace = "namespace", name = "name")

        val sql = postgresDirectLoadSqlGenerator.createTable(
            stream = stream,
            tableName = tableName,
            columnNameMapping = columnNameMapping,
            replace = true
        )

        val expected = """
            BEGIN TRANSACTION;
            DROP TABLE IF EXISTS "namespace"."name";
            CREATE TABLE "namespace"."name" (
            "_airbyte_raw_id" varchar NOT NULL,
            "_airbyte_extracted_at" timestamp with time zone NOT NULL,
            "_airbyte_meta" jsonb NOT NULL,
            "_airbyte_generation_id" bigint NOT NULL,
            "targetId" varchar,
            "sourceName" varchar
            );
            CREATE INDEX ON "namespace"."name" ("_airbyte_extracted_at");
            COMMIT;
            """.trimIndent()

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    private fun assertEqualsIgnoreWhitespace(expected: String, actual: String) {
        assertEquals(
            dropWhitespace(expected),
            dropWhitespace(actual))
    }

    private fun dropWhitespace(text: String) = text
        .lines()
        .map { it.trim()}
        .filter { it.isNotEmpty() }
        .joinToString("\n") { it.trim() }

    @Test
    fun testCreateTableNoReplace() {
        val stream = mockk<DestinationStream> {
            every { schema } returns ObjectType(
                properties = linkedMapOf(
                    "sourceId" to FieldType(StringType, nullable = false),
                )
            )

            every { importType } returns Append
        }
        val columnNameMapping = ColumnNameMapping(
            mapOf(
                "sourceId" to "targetId",
            )
        )
        val tableName = TableName(namespace = "namespace", name = "name")

        val sql = postgresDirectLoadSqlGenerator.createTable(
            stream = stream,
            tableName = tableName,
            columnNameMapping = columnNameMapping,
            replace = false
        )

        val expected = """
            BEGIN TRANSACTION;
            CREATE TABLE "namespace"."name" (
            "_airbyte_raw_id" varchar NOT NULL,
            "_airbyte_extracted_at" timestamp with time zone NOT NULL,
            "_airbyte_meta" jsonb NOT NULL,
            "_airbyte_generation_id" bigint NOT NULL,
            "targetId" varchar
            );
            CREATE INDEX ON "namespace"."name" ("_airbyte_extracted_at");
            COMMIT;
            """.trimIndent()

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testCreateTableWithPrimaryKeysAndCursor() {
        val stream = mockk<DestinationStream> {
            every { schema } returns ObjectType(
                properties = linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = false),
                    "name" to FieldType(StringType, nullable = true),
                    "updatedAt" to FieldType(TimestampTypeWithTimezone, nullable = true)
                )
            )
            every { importType } returns Dedupe(
                primaryKey = listOf(listOf("id")),
                cursor = listOf("updatedAt")
            )
        }
        val columnNameMapping = ColumnNameMapping(emptyMap())
        val tableName = TableName(namespace = "test_schema", name = "test_table")

        val sql = postgresDirectLoadSqlGenerator.createTable(
            stream = stream,
            tableName = tableName,
            columnNameMapping = columnNameMapping,
            replace = true
        )

        val expected = """
            BEGIN TRANSACTION;
            DROP TABLE IF EXISTS "test_schema"."test_table";
            CREATE TABLE "test_schema"."test_table" (
            "_airbyte_raw_id" varchar NOT NULL,
            "_airbyte_extracted_at" timestamp with time zone NOT NULL,
            "_airbyte_meta" jsonb NOT NULL,
            "_airbyte_generation_id" bigint NOT NULL,
            "id" bigint,
            "name" varchar,
            "updatedAt" timestamp with time zone
            );
            CREATE INDEX "idx_pk_test_table" ON "test_schema"."test_table" ("id");
            CREATE INDEX "idx_cursor_test_table" ON "test_schema"."test_table" ("updatedAt");
            CREATE INDEX ON "test_schema"."test_table" ("_airbyte_extracted_at");
            COMMIT;
            """.trimIndent()

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testOverwriteTable() {
        val sourceTableName = TableName(namespace = "namespace", name = "source")
        val targetTableName = TableName(namespace = "namespace", name = "target")
        val sql = postgresDirectLoadSqlGenerator.overwriteTable(sourceTableName, targetTableName)

        val expected = """
            BEGIN TRANSACTION;
            DROP TABLE IF EXISTS "namespace"."target";
            ALTER TABLE "namespace"."source" RENAME TO "target";
            COMMIT;
        """.trimIndent()

        assertEquals(expected, sql)
    }

    @Test
    fun testGenerateCopyTable() {
        val columnNameMapping = ColumnNameMapping(
            mapOf(
                "sourceId" to "targetId"
            )
        )
        val sourceTableName = TableName(namespace = "namespace", name = "source")
        val destinationTableName = TableName(namespace = "namespace", name = "target")

        val sql = postgresDirectLoadSqlGenerator.copyTable(
            columnNameMapping = columnNameMapping,
            sourceTableName = sourceTableName,
            targetTableName = destinationTableName
        )

        val expected = """
            INSERT INTO "namespace"."target" ("_airbyte_raw_id","_airbyte_extracted_at","_airbyte_meta","_airbyte_generation_id","targetId")
            SELECT "_airbyte_raw_id","_airbyte_extracted_at","_airbyte_meta","_airbyte_generation_id","targetId"
            FROM "namespace"."source";
        """.trimIndent()

        assertEquals(expected, sql)
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
        assertEquals(
            "SELECT COUNT(*) AS \"total\" FROM \"namespace\".\"name\";",
            sql
        )
    }

    @Test
    fun testCreateNamespace() {
        val namespace = "namespace"
        val sql = postgresDirectLoadSqlGenerator.createNamespace(namespace)
        assertEquals(
            "CREATE SCHEMA IF NOT EXISTS \"namespace\";",
            sql
        )
    }

    @Test
    fun testGetGenerationId() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val sql = postgresDirectLoadSqlGenerator.getGenerationId(tableName = tableName)
        assertEquals(
            "SELECT \"_airbyte_generation_id\" FROM \"namespace\".\"name\" LIMIT 1;",
            sql
        )
    }

    @Test
    fun testToDialectTypeMapping() {
        with(postgresDirectLoadSqlGenerator) {
            assertEquals("boolean", BooleanType.toDialectType())
            assertEquals("date", DateType.toDialectType())
            assertEquals("bigint", IntegerType.toDialectType())
            assertEquals("decimal", NumberType.toDialectType())
            assertEquals("varchar", StringType.toDialectType())
            assertEquals("time with time zone", TimeTypeWithTimezone.toDialectType())
            assertEquals("time", TimeTypeWithoutTimezone.toDialectType())
            assertEquals("timestamp with time zone", TimestampTypeWithTimezone.toDialectType())
            assertEquals("timestamp", TimestampTypeWithoutTimezone.toDialectType())

            assertEquals("jsonb", ArrayType(items = FieldType(StringType, false)).toDialectType())
            assertEquals("jsonb", ArrayTypeWithoutSchema.toDialectType())
            assertEquals("jsonb", ObjectType(linkedMapOf()).toDialectType())
            assertEquals("jsonb", ObjectTypeWithEmptySchema.toDialectType())
            assertEquals("jsonb", ObjectTypeWithoutSchema.toDialectType())
            assertEquals("jsonb", UnknownType(mockk<JsonNode>()).toDialectType())
        }
    }

    @Test
    fun testToDialectTypeMappingUnions() {
        with(postgresDirectLoadSqlGenerator) {
            val unionWithStruct = UnionType(
                options = setOf(
                    StringType,
                    ObjectType(linkedMapOf("field" to FieldType(StringType, nullable = false)))
                ),
                isLegacyUnion = true
            )
            assertEquals("jsonb", unionWithStruct.toDialectType())

            val unionWithBasicTypes = UnionType(
                options = setOf(StringType, IntegerType),
                isLegacyUnion = true
            )
            assertEquals("jsonb", unionWithBasicTypes.toDialectType())
        }
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
    fun testUpsertTableWithNoCdcDelete() {
        every { postgresConfiguration.cdcDeletionMode } returns CdcDeletionMode.SOFT_DELETE

        val stream = mockk<DestinationStream> {
            every { schema } returns ObjectType(
                properties = linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = false),
                    "name" to FieldType(StringType, nullable = true),
                    "updatedAt" to FieldType(TimestampTypeWithTimezone, nullable = true)
                )
            )
            every { importType } returns Dedupe(
                primaryKey = listOf(listOf("id")),
                cursor = listOf("updatedAt")
            )
        }

        val columnNameMapping = ColumnNameMapping(emptyMap())
        val sourceTableName = TableName(namespace = "test_schema", name = "staging_table")
        val targetTableName = TableName(namespace = "test_schema", name = "final_table")

        val sql = postgresDirectLoadSqlGenerator.upsertTable(
            stream = stream,
            columnNameMapping = columnNameMapping,
            sourceTableName = sourceTableName,
            targetTableName = targetTableName
        )

        val expected = """
            WITH deduped_source AS (
            SELECT "_airbyte_raw_id", "_airbyte_extracted_at", "_airbyte_meta", "_airbyte_generation_id", "id", "name", "updatedAt"
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

            updates AS (
            UPDATE "test_schema"."final_table"
            SET
            "_airbyte_raw_id" = deduped_source."_airbyte_raw_id",
            "_airbyte_extracted_at" = deduped_source."_airbyte_extracted_at",
            "_airbyte_meta" = deduped_source."_airbyte_meta",
            "_airbyte_generation_id" = deduped_source."_airbyte_generation_id",
            "id" = deduped_source."id",
            "name" = deduped_source."name",
            "updatedAt" = deduped_source."updatedAt"
            FROM deduped_source
            WHERE "test_schema"."final_table"."id" = deduped_source."id"
            AND ("test_schema"."final_table"."updatedAt" < deduped_source."updatedAt"
            OR ("test_schema"."final_table"."updatedAt" = deduped_source."updatedAt" AND "test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at")
            OR ("test_schema"."final_table"."updatedAt" IS NULL AND deduped_source."updatedAt" IS NOT NULL)
            OR ("test_schema"."final_table"."updatedAt" IS NULL AND deduped_source."updatedAt" IS NULL AND "test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at"))
            )

            INSERT INTO "test_schema"."final_table" (
            "_airbyte_raw_id",
            "_airbyte_extracted_at",
            "_airbyte_meta",
            "_airbyte_generation_id",
            "id",
            "name",
            "updatedAt"
            )
            SELECT
            "_airbyte_raw_id",
            "_airbyte_extracted_at",
            "_airbyte_meta",
            "_airbyte_generation_id",
            "id",
            "name",
            "updatedAt"
            FROM deduped_source
            WHERE
            NOT EXISTS (
            SELECT 1
            FROM "test_schema"."final_table"
            WHERE "test_schema"."final_table"."id" = deduped_source."id"
            )
            """.trimIndent()

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testUpsertTableWithCdcDelete() {
        every { postgresConfiguration.cdcDeletionMode } returns CdcDeletionMode.HARD_DELETE

        val stream = mockk<DestinationStream> {
            every { schema } returns ObjectType(
                properties = linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = false),
                    "name" to FieldType(StringType, nullable = true),
                    "updatedAt" to FieldType(TimestampTypeWithTimezone, nullable = true),
                    CDC_DELETED_AT_COLUMN to FieldType(TimestampTypeWithTimezone, nullable = true)
                )
            )
            every { importType } returns Dedupe(
                primaryKey = listOf(listOf("id")),
                cursor = listOf("updatedAt")
            )
        }

        val columnNameMapping = ColumnNameMapping(emptyMap())
        val sourceTableName = TableName(namespace = "test_schema", name = "staging_table")
        val targetTableName = TableName(namespace = "test_schema", name = "final_table")

        val sql = postgresDirectLoadSqlGenerator.upsertTable(
            stream = stream,
            columnNameMapping = columnNameMapping,
            sourceTableName = sourceTableName,
            targetTableName = targetTableName
        )

        val expected = """
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
            AND ("test_schema"."final_table"."updatedAt" < deduped_source."updatedAt"
            OR ("test_schema"."final_table"."updatedAt" = deduped_source."updatedAt" AND "test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at")
            OR ("test_schema"."final_table"."updatedAt" IS NULL AND deduped_source."updatedAt" IS NOT NULL)
            OR ("test_schema"."final_table"."updatedAt" IS NULL AND deduped_source."updatedAt" IS NULL AND "test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at"))
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
            AND ("test_schema"."final_table"."updatedAt" < deduped_source."updatedAt"
            OR ("test_schema"."final_table"."updatedAt" = deduped_source."updatedAt" AND "test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at")
            OR ("test_schema"."final_table"."updatedAt" IS NULL AND deduped_source."updatedAt" IS NOT NULL)
            OR ("test_schema"."final_table"."updatedAt" IS NULL AND deduped_source."updatedAt" IS NULL AND "test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at"))
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
            """.trimIndent()

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testUpsertTableWithoutPrimaryKeyThrowsException() {
        val stream = mockk<DestinationStream> {
            every { importType } returns Dedupe(
                primaryKey = emptyList(),
                cursor = emptyList()
            )
        }

        val columnNameMapping = ColumnNameMapping(emptyMap())
        val sourceTableName = TableName(namespace = "test_schema", name = "source_table")
        val targetTableName = TableName(namespace = "test_schema", name = "target_table")

        val exception = assertThrows<IllegalArgumentException> {
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

        val sql = postgresDirectLoadSqlGenerator.selectDeduped(
            primaryKeyColumns,
            cursorColumn,
            allColumns,
            sourceTable
        )

        val expected = """
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
            """.trimIndent()

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testSelectDedupedWithoutCursor() {
        val primaryKeyColumns = listOf("id")
        val allColumns = listOf("id", "name", "updatedAt", "_airbyte_extracted_at")
        val sourceTable = TableName(namespace = "test_schema", name = "staging_table")

        val sql = postgresDirectLoadSqlGenerator.selectDeduped(
            primaryKeyColumns,
            null,
            allColumns,
            sourceTable
        )

        val expected = """
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
            """.trimIndent()

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testCdcDeleteWithCursor() {
        val dedupTableAlias = "deduped_source"
        val cursorColumn = "updatedAt"
        val targetTable = TableName(namespace = "test_schema", name = "final_table")
        val primaryKeyColumns = listOf("id")

        val sql = postgresDirectLoadSqlGenerator.cdcDelete(
            dedupTableAlias,
            cursorColumn,
            targetTable,
            primaryKeyColumns
        )

        val expected = """
            DELETE FROM "test_schema"."final_table"
            USING deduped_source
            WHERE "test_schema"."final_table".id = deduped_source.id
            AND deduped_source."_ab_cdc_deleted_at" IS NOT NULL
            AND ("test_schema"."final_table".updatedAt < deduped_source.updatedAt
            OR ("test_schema"."final_table".updatedAt = deduped_source.updatedAt AND "test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at")
            OR ("test_schema"."final_table".updatedAt IS NULL AND deduped_source.updatedAt IS NOT NULL)
            OR ("test_schema"."final_table".updatedAt IS NULL AND deduped_source.updatedAt IS NULL AND "test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at"))
            """.trimIndent()

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testCdcDeleteWithoutCursor() {
        val dedupTableAlias = "deduped_source"
        val targetTable = TableName(namespace = "test_schema", name = "final_table")
        val primaryKeyColumns = listOf("id")

        val sql = postgresDirectLoadSqlGenerator.cdcDelete(
            dedupTableAlias,
            null,
            targetTable,
            primaryKeyColumns
        )

        val expected = """
            DELETE FROM "test_schema"."final_table"
            USING deduped_source
            WHERE "test_schema"."final_table".id = deduped_source.id
            AND deduped_source."_ab_cdc_deleted_at" IS NOT NULL
            AND ("test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at")
            """.trimIndent()

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testUpdateExistingRows() {
        val dedupTableAlias = "deduped_source"
        val targetTable = TableName(namespace = "test_schema", name = "final_table")
        val allColumns = listOf("id", "name")
        val primaryKeyColumns = listOf("id")

        val sql = postgresDirectLoadSqlGenerator.updateExistingRows(
            dedupTableAlias,
            targetTable,
            allColumns,
            primaryKeyColumns,
            null,
            false
        )

        val expected = """
            UPDATE "test_schema"."final_table"
            SET
            id = deduped_source.id,
            name = deduped_source.name
            FROM deduped_source
            WHERE "test_schema"."final_table".id = deduped_source.id
            AND ("test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at")
            """.trimIndent()

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testUpdateExistingRowsWithCursor() {
        val dedupTableAlias = "deduped_source"
        val targetTable = TableName(namespace = "test_schema", name = "final_table")
        val allColumns = listOf("id", "name", "updatedAt")
        val primaryKeyColumns = listOf("id")
        val cursorColumn = "updatedAt"

        val sql = postgresDirectLoadSqlGenerator.updateExistingRows(
            dedupTableAlias,
            targetTable,
            allColumns,
            primaryKeyColumns,
            cursorColumn,
            false
        )

        val expected = """
            UPDATE "test_schema"."final_table"
            SET
            id = deduped_source.id,
            name = deduped_source.name,
            updatedAt = deduped_source.updatedAt
            FROM deduped_source
            WHERE "test_schema"."final_table".id = deduped_source.id
            AND ("test_schema"."final_table".updatedAt < deduped_source.updatedAt
            OR ("test_schema"."final_table".updatedAt = deduped_source.updatedAt AND "test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at")
            OR ("test_schema"."final_table".updatedAt IS NULL AND deduped_source.updatedAt IS NOT NULL)
            OR ("test_schema"."final_table".updatedAt IS NULL AND deduped_source.updatedAt IS NULL AND "test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at"))
            """.trimIndent()

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testUpdateExistingRowsWithCdcDelete() {
        val dedupTableAlias = "deduped_source"
        val targetTable = TableName(namespace = "test_schema", name = "final_table")
        val allColumns = listOf("id", "name")
        val primaryKeyColumns = listOf("id")

        val sql = postgresDirectLoadSqlGenerator.updateExistingRows(
            dedupTableAlias,
            targetTable,
            allColumns,
            primaryKeyColumns,
            null,
            true
        )

        val expected = """
            UPDATE "test_schema"."final_table"
            SET
            id = deduped_source.id,
            name = deduped_source.name
            FROM deduped_source
            WHERE "test_schema"."final_table".id = deduped_source.id
            AND deduped_source."_ab_cdc_deleted_at" IS NULL
            AND ("test_schema"."final_table"."_airbyte_extracted_at" < deduped_source."_airbyte_extracted_at")
            """.trimIndent()

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testInsertNewRows() {
        val dedupTableAlias = "deduped_source"
        val targetTable = TableName(namespace = "test_schema", name = "final_table")
        val allColumns = listOf("id", "name")
        val primaryKeyColumns = listOf("id")

        val sql = postgresDirectLoadSqlGenerator.insertNewRows(
            dedupTableAlias,
            targetTable,
            allColumns,
            primaryKeyColumns,
            false
        )

        val expected = """
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
            """.trimIndent()

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testInsertNewRowsWithCdcDelete() {
        val dedupTableAlias = "deduped_source"
        val targetTable = TableName(namespace = "test_schema", name = "final_table")
        val allColumns = listOf("id", "name")
        val primaryKeyColumns = listOf("id")

        val sql = postgresDirectLoadSqlGenerator.insertNewRows(
            dedupTableAlias,
            targetTable,
            allColumns,
            primaryKeyColumns,
            true
        )

        val expected = """
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
            """.trimIndent()

        assertEqualsIgnoreWhitespace(expected, sql)
    }
}
