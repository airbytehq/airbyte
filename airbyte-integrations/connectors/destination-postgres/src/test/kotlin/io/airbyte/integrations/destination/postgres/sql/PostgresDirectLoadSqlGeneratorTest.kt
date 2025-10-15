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
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class PostgresDirectLoadSqlGeneratorTest {

    private lateinit var postgresDirectLoadSqlGenerator: PostgresDirectLoadSqlGenerator

    @BeforeEach
    fun setUp() {
        postgresDirectLoadSqlGenerator = PostgresDirectLoadSqlGenerator()
    }

    @Test
    fun testGenerateCreateTableStatement() {
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
                "sourceId" to "targetId",
                "sourceName" to "targetName"
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
            _airbyte_raw_id varchar NOT NULL,
            _airbyte_extracted_at timestamp with time zone NOT NULL,
            _airbyte_meta jsonb NOT NULL,
            _airbyte_generation_id bigint NOT NULL,
            targetId varchar,
            targetName varchar
            );
            COMMIT;
            """

        assertEqualsIgnoreIndentation(expected, sql)
    }

    private fun assertEqualsIgnoreIndentation(expected: String, actual: String) {
        assertEquals(
            normalizeIndentation(expected),
            normalizeIndentation(actual))
    }

    private fun normalizeIndentation(text: String) = text
        .lines().joinToString("\n") { it.trim() }

    @Test
    fun testGenerateCreateTableStatementNoReplace() {
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
            _airbyte_raw_id varchar NOT NULL,
            _airbyte_extracted_at timestamp with time zone NOT NULL,
            _airbyte_meta jsonb NOT NULL,
            _airbyte_generation_id bigint NOT NULL,
            targetId varchar,
            );
            COMMIT;
            """

        assertEqualsIgnoreIndentation(expected, sql)
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
    fun testGenerateDropTable() {
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
    fun testToDialectTypeMappingSimple() {
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

            assertEquals("varchar", UnknownType(mockk<JsonNode>()).toDialectType())
        }
    }

    @Test
    fun testToDialectTypeMappingComplex() {
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
        val notNullColumn = ColumnAndType("column", "varchar", nullable = false)
        assertEquals("column varchar NOT NULL", notNullColumn.toString())
    }

    @Test
    fun testNullableColumnAndTypeToString() {
        val nullableColumn = ColumnAndType("column", "varchar", nullable = true)
        assertEquals("column varchar", nullableColumn.toString())
    }
}
