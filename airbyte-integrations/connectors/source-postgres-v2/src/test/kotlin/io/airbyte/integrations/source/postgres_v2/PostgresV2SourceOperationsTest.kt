/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres_v2

import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.BigIntegerFieldType
import io.airbyte.cdk.jdbc.BinaryStreamFieldType
import io.airbyte.cdk.jdbc.BooleanFieldType
import io.airbyte.cdk.jdbc.DoubleFieldType
import io.airbyte.cdk.jdbc.FloatFieldType
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.LocalDateFieldType
import io.airbyte.cdk.jdbc.LocalDateTimeFieldType
import io.airbyte.cdk.jdbc.LocalTimeFieldType
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.OffsetTimeFieldType
import io.airbyte.cdk.jdbc.PokemonFieldType
import io.airbyte.cdk.jdbc.ShortFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.read.From
import io.airbyte.cdk.read.Greater
import io.airbyte.cdk.read.Limit
import io.airbyte.cdk.read.NoOrderBy
import io.airbyte.cdk.read.NoWhere
import io.airbyte.cdk.read.OrderBy
import io.airbyte.cdk.read.SelectColumnMaxValue
import io.airbyte.cdk.read.SelectColumns
import io.airbyte.cdk.read.SelectQuerySpec
import io.airbyte.cdk.read.Where
import io.airbyte.cdk.util.Jsons
import java.sql.Types
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

class PostgresV2SourceOperationsTest {

    private val ops = PostgresV2SourceOperations()

    @ParameterizedTest
    @CsvSource(
        "BOOL, BooleanFieldType",
        "BOOLEAN, BooleanFieldType",
        "INT2, ShortFieldType",
        "SMALLINT, ShortFieldType",
        "SMALLSERIAL, ShortFieldType",
        "INT, IntFieldType",
        "INT4, IntFieldType",
        "INTEGER, IntFieldType",
        "SERIAL, IntFieldType",
        "INT8, LongFieldType",
        "BIGINT, LongFieldType",
        "BIGSERIAL, LongFieldType",
        "FLOAT4, FloatFieldType",
        "REAL, FloatFieldType",
        "FLOAT8, DoubleFieldType",
        "DOUBLE PRECISION, DoubleFieldType",
        "CHAR, StringFieldType",
        "VARCHAR, StringFieldType",
        "TEXT, StringFieldType",
        "UUID, StringFieldType",
        "DATE, LocalDateFieldType",
        "TIME, LocalTimeFieldType",
        "TIMETZ, OffsetTimeFieldType",
        "TIMESTAMP, LocalDateTimeFieldType",
        "TIMESTAMPTZ, OffsetDateTimeFieldType",
        "BYTEA, BinaryStreamFieldType",
        "JSON, StringFieldType",
        "JSONB, StringFieldType",
        "XML, StringFieldType",
    )
    fun testTypeMapping(typeName: String, expectedTypeName: String) {
        val systemType = SystemType(typeName = typeName, typeCode = Types.OTHER)
        val metadata =
            JdbcMetadataQuerier.ColumnMetadata(
                name = "test_col",
                label = "test_col",
                type = systemType,
                nullable = true,
            )
        val result = ops.toFieldType(metadata)

        val expectedType =
            when (expectedTypeName) {
                "BooleanFieldType" -> BooleanFieldType
                "ShortFieldType" -> ShortFieldType
                "IntFieldType" -> IntFieldType
                "LongFieldType" -> LongFieldType
                "FloatFieldType" -> FloatFieldType
                "DoubleFieldType" -> DoubleFieldType
                "BigDecimalFieldType" -> BigDecimalFieldType
                "BigIntegerFieldType" -> BigIntegerFieldType
                "StringFieldType" -> StringFieldType
                "LocalDateFieldType" -> LocalDateFieldType
                "LocalTimeFieldType" -> LocalTimeFieldType
                "OffsetTimeFieldType" -> OffsetTimeFieldType
                "LocalDateTimeFieldType" -> LocalDateTimeFieldType
                "OffsetDateTimeFieldType" -> OffsetDateTimeFieldType
                "BinaryStreamFieldType" -> BinaryStreamFieldType
                "PokemonFieldType" -> PokemonFieldType
                else -> throw IllegalArgumentException("Unknown type: $expectedTypeName")
            }

        assertEquals(
            expectedType::class,
            result::class,
            "Type $typeName should map to $expectedTypeName"
        )
    }

    @Test
    fun testNumericWithScaleZero() {
        val systemType = SystemType(typeName = "NUMERIC", typeCode = Types.NUMERIC, scale = 0)
        val metadata =
            JdbcMetadataQuerier.ColumnMetadata(
                name = "test_col",
                label = "test_col",
                type = systemType,
                nullable = true,
            )
        val result = ops.toFieldType(metadata)
        assertEquals(BigIntegerFieldType::class, result::class)
    }

    @Test
    fun testNumericWithScale() {
        val systemType =
            SystemType(typeName = "NUMERIC", typeCode = Types.NUMERIC, precision = 10, scale = 2)
        val metadata =
            JdbcMetadataQuerier.ColumnMetadata(
                name = "test_col",
                label = "test_col",
                type = systemType,
                nullable = true,
            )
        val result = ops.toFieldType(metadata)
        assertEquals(BigDecimalFieldType::class, result::class)
    }

    @Test
    fun testUnknownType() {
        val systemType = SystemType(typeName = "UNKNOWN_TYPE", typeCode = Types.OTHER)
        val metadata =
            JdbcMetadataQuerier.ColumnMetadata(
                name = "test_col",
                label = "test_col",
                type = systemType,
                nullable = true,
            )
        val result = ops.toFieldType(metadata)
        assertEquals(PokemonFieldType::class, result::class)
    }

    @Test
    fun testSimpleSelect() {
        val field1 = Field("id", LongFieldType)
        val field2 = Field("name", StringFieldType)

        val spec =
            SelectQuerySpec(
                SelectColumns(listOf(field1, field2)),
                From("users", "public"),
            )

        val query = ops.generate(spec)

        assertEquals("SELECT \"id\", \"name\" FROM \"public\".\"users\"", query.sql)
    }

    @Test
    fun testSelectWithoutNamespace() {
        val field1 = Field("id", LongFieldType)

        val spec =
            SelectQuerySpec(
                SelectColumns(listOf(field1)),
                From("users", null),
            )

        val query = ops.generate(spec)

        assertEquals("SELECT \"id\" FROM \"users\"", query.sql)
    }

    @Test
    fun testSelectWithWhere() {
        val field1 = Field("id", LongFieldType)

        val spec =
            SelectQuerySpec(
                SelectColumns(listOf(field1)),
                From("users", "public"),
                Where(Greater(field1, Jsons.numberNode(100))),
            )

        val query = ops.generate(spec)

        assertEquals("SELECT \"id\" FROM \"public\".\"users\" WHERE \"id\" > ?", query.sql)
    }

    @Test
    fun testSelectWithOrderBy() {
        val field1 = Field("id", LongFieldType)
        val field2 = Field("created_at", OffsetDateTimeFieldType)

        val spec =
            SelectQuerySpec(
                SelectColumns(listOf(field1, field2)),
                From("users", "public"),
                NoWhere,
                OrderBy(listOf(field2)),
            )

        val query = ops.generate(spec)

        assertEquals(
            "SELECT \"id\", \"created_at\" FROM \"public\".\"users\" ORDER BY \"created_at\"",
            query.sql
        )
    }

    @Test
    fun testSelectWithLimit() {
        val field1 = Field("id", LongFieldType)

        val spec =
            SelectQuerySpec(
                SelectColumns(listOf(field1)),
                From("users", "public"),
                NoWhere,
                NoOrderBy,
                Limit(100),
            )

        val query = ops.generate(spec)

        assertEquals("SELECT \"id\" FROM \"public\".\"users\" LIMIT ?", query.sql)
    }

    @Test
    fun testSelectMax() {
        val field = Field("id", LongFieldType)

        val spec =
            SelectQuerySpec(
                SelectColumnMaxValue(field),
                From("users", "public"),
            )

        val query = ops.generate(spec)

        assertEquals("SELECT MAX(\"id\") FROM \"public\".\"users\"", query.sql)
    }

    @Test
    fun testFullQuery() {
        val idField = Field("id", LongFieldType)
        val nameField = Field("name", StringFieldType)

        val spec =
            SelectQuerySpec(
                SelectColumns(listOf(idField, nameField)),
                From("users", "public"),
                Where(Greater(idField, Jsons.numberNode(0))),
                OrderBy(listOf(idField)),
                Limit(1000),
            )

        val query = ops.generate(spec)

        assertTrue(query.sql.contains("SELECT \"id\", \"name\""))
        assertTrue(query.sql.contains("FROM \"public\".\"users\""))
        assertTrue(query.sql.contains("WHERE \"id\" > ?"))
        assertTrue(query.sql.contains("ORDER BY \"id\""))
        assertTrue(query.sql.contains("LIMIT ?"))
    }
}
