/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.sql

import com.fasterxml.jackson.databind.JsonNode
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
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class PostgresDirectLoadSqlGeneratorTest {

    private lateinit var postgresDirectLoadSqlGenerator: PostgresDirectLoadSqlGenerator
    private lateinit var columnUtils: PostgresColumnUtils

    @BeforeEach
    fun setUp() {
        val mockConfig = mockk<PostgresConfiguration> {
            every { legacyRawTablesOnly } returns false
        }
        columnUtils = PostgresColumnUtils(mockConfig)
        postgresDirectLoadSqlGenerator = PostgresDirectLoadSqlGenerator(columnUtils)
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
            COMMIT;
            """.trimIndent()

        assertEqualsIgnoreWhitespace(expected, sql)
    }

    @Test
    fun testOverwriteTable() {
        val sourceTableName = TableName(namespace = "sourceNamespace", name = "source")
        val targetTableName = TableName(namespace = "targetNamespace", name = "target")
        val sql = postgresDirectLoadSqlGenerator.overwriteTable(sourceTableName, targetTableName)

        val expected = """
            BEGIN TRANSACTION;
            DROP TABLE IF EXISTS "targetNamespace"."target";
            ALTER TABLE "sourceNamespace"."source" RENAME TO "targetNamespace"."target";
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
            assertEquals("varchar", unionWithBasicTypes.toDialectType())
        }
    }

    @Test
    fun testColumnAndTypeToString() {
        val notNullColumn = Column("column", "varchar", nullable = false)
        assertEquals("\"column\" varchar NOT NULL", notNullColumn.toString())
    }

    @Test
    fun testNullableColumnAndTypeToString() {
        val nullableColumn = Column("column", "varchar", nullable = true)
        assertEquals("\"column\" varchar", nullableColumn.toString())
    }
}
