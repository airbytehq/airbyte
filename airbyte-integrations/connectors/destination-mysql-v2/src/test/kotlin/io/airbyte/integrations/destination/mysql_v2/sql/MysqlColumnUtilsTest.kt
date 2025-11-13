/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql_v2.sql

import com.fasterxml.jackson.databind.JsonNode
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
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.CsvSource
import org.junit.jupiter.params.provider.MethodSource

class MysqlColumnUtilsTest {

    private lateinit var columnUtils: MysqlColumnUtils

    @BeforeEach
    fun setup() {
        columnUtils = MysqlColumnUtils()
    }

    // ========== Type Mapping Tests ==========

    @Test
    fun testToDialectTypeBooleanType() {
        assertEquals("BOOLEAN", columnUtils.toDialectType(BooleanType))
    }

    @Test
    fun testToDialectTypeIntegerType() {
        assertEquals("BIGINT", columnUtils.toDialectType(IntegerType))
    }

    @Test
    fun testToDialectTypeNumberType() {
        assertEquals("DECIMAL(38, 9)", columnUtils.toDialectType(NumberType))
    }

    @Test
    fun testToDialectTypeStringType() {
        assertEquals("TEXT", columnUtils.toDialectType(StringType))
    }

    @Test
    fun testToDialectTypeDateType() {
        assertEquals("DATE", columnUtils.toDialectType(DateType))
    }

    @Test
    fun testToDialectTypeTimeTypeWithTimezone() {
        assertEquals("TIME", columnUtils.toDialectType(TimeTypeWithTimezone))
    }

    @Test
    fun testToDialectTypeTimeTypeWithoutTimezone() {
        assertEquals("TIME", columnUtils.toDialectType(TimeTypeWithoutTimezone))
    }

    @Test
    fun testToDialectTypeTimestampTypeWithTimezone() {
        assertEquals("TIMESTAMP", columnUtils.toDialectType(TimestampTypeWithTimezone))
    }

    @Test
    fun testToDialectTypeTimestampTypeWithoutTimezone() {
        assertEquals("DATETIME", columnUtils.toDialectType(TimestampTypeWithoutTimezone))
    }

    @Test
    fun testToDialectTypeArrayType() {
        val arrayType = ArrayType(items = FieldType(StringType, false))
        assertEquals("JSON", columnUtils.toDialectType(arrayType))
    }

    @Test
    fun testToDialectTypeArrayTypeWithoutSchema() {
        assertEquals("JSON", columnUtils.toDialectType(ArrayTypeWithoutSchema))
    }

    @Test
    fun testToDialectTypeObjectType() {
        val objectType = ObjectType(
            properties = LinkedHashMap(),
            additionalProperties = false
        )
        assertEquals("JSON", columnUtils.toDialectType(objectType))
    }

    @Test
    fun testToDialectTypeObjectTypeWithEmptySchema() {
        assertEquals("JSON", columnUtils.toDialectType(ObjectTypeWithEmptySchema))
    }

    @Test
    fun testToDialectTypeObjectTypeWithoutSchema() {
        assertEquals("JSON", columnUtils.toDialectType(ObjectTypeWithoutSchema))
    }

    @Test
    fun testToDialectTypeUnionType() {
        val unionType = UnionType(
            options = setOf(StringType, IntegerType),
            isLegacyUnion = false
        )
        assertEquals("JSON", columnUtils.toDialectType(unionType))
    }

    @Test
    fun testToDialectTypeUnknownType() {
        val unknownType = UnknownType(schema = mockk<JsonNode>())
        assertEquals("JSON", columnUtils.toDialectType(unknownType))
    }

    // ========== Format Column Tests ==========

    @Test
    fun testFormatColumnNullable() {
        val result = columnUtils.formatColumn("user_name", StringType, true)
        assertEquals("`user_name` TEXT", result)
    }

    @Test
    fun testFormatColumnNotNullable() {
        val result = columnUtils.formatColumn("user_id", IntegerType, false)
        assertEquals("`user_id` BIGINT NOT NULL", result)
    }

    @Test
    fun testFormatColumnWithSpecialCharacters() {
        val result = columnUtils.formatColumn("user-name", StringType, true)
        assertEquals("`user-name` TEXT", result)
    }

    @Test
    fun testFormatColumnWithUnderscores() {
        val result = columnUtils.formatColumn("user_email_address", StringType, false)
        assertEquals("`user_email_address` TEXT NOT NULL", result)
    }

    @ParameterizedTest
    @MethodSource("formatColumnTestCases")
    fun testFormatColumnParameterized(
        name: String,
        type: io.airbyte.cdk.load.data.AirbyteType,
        nullable: Boolean,
        expected: String
    ) {
        val result = columnUtils.formatColumn(name, type, nullable)
        assertEquals(expected, result)
    }

    // ========== Quote Tests ==========

    @Test
    fun testQuoteSimpleString() {
        assertEquals("`tableName`", "tableName".let { columnUtils.run { it.quote() } })
    }

    @Test
    fun testQuoteWithSpecialCharacters() {
        assertEquals("`table-name`", "table-name".let { columnUtils.run { it.quote() } })
    }

    @Test
    fun testQuoteWithUnderscores() {
        assertEquals("`table_name`", "table_name".let { columnUtils.run { it.quote() } })
    }

    @Test
    fun testQuoteWithNumbers() {
        assertEquals("`table123`", "table123".let { columnUtils.run { it.quote() } })
    }

    @Test
    fun testQuoteWithSpaces() {
        assertEquals("`table name`", "table name".let { columnUtils.run { it.quote() } })
    }

    // ========== Fully Qualified Name Tests ==========

    @Test
    fun testFullyQualifiedName() {
        val result = columnUtils.fullyQualifiedName("test_database", "users")
        assertEquals("`test_database`.`users`", result)
    }

    @Test
    fun testFullyQualifiedNameWithSpecialCharacters() {
        val result = columnUtils.fullyQualifiedName("test-database", "user-table")
        assertEquals("`test-database`.`user-table`", result)
    }

    @Test
    fun testFullyQualifiedNameWithUnderscores() {
        val result = columnUtils.fullyQualifiedName("test_database", "user_table")
        assertEquals("`test_database`.`user_table`", result)
    }

    @Test
    fun testFullyQualifiedNameWithNumbers() {
        val result = columnUtils.fullyQualifiedName("db123", "table456")
        assertEquals("`db123`.`table456`", result)
    }

    @Test
    fun testFullyQualifiedNameWithMixedCase() {
        val result = columnUtils.fullyQualifiedName("TestDatabase", "UserTable")
        assertEquals("`TestDatabase`.`UserTable`", result)
    }

    // ========== Edge Cases ==========

    @Test
    fun testFormatColumnWithEmptyName() {
        val result = columnUtils.formatColumn("", StringType, true)
        assertEquals("`` TEXT", result)
    }

    @Test
    fun testQuoteEmptyString() {
        assertEquals("``", "".let { columnUtils.run { it.quote() } })
    }

    @Test
    fun testFullyQualifiedNameWithEmptyDatabase() {
        val result = columnUtils.fullyQualifiedName("", "table")
        assertEquals("``.`table`", result)
    }

    @Test
    fun testFullyQualifiedNameWithEmptyTable() {
        val result = columnUtils.fullyQualifiedName("database", "")
        assertEquals("`database`.``", result)
    }

    // ========== Type Consistency Tests ==========

    @Test
    fun testAllTimeTypesMapToTime() {
        assertEquals(
            columnUtils.toDialectType(TimeTypeWithTimezone),
            columnUtils.toDialectType(TimeTypeWithoutTimezone)
        )
    }

    @Test
    fun testTimestampTypesMapDifferently() {
        val withTz = columnUtils.toDialectType(TimestampTypeWithTimezone)
        val withoutTz = columnUtils.toDialectType(TimestampTypeWithoutTimezone)

        assertEquals("TIMESTAMP", withTz)
        assertEquals("DATETIME", withoutTz)
        assert(withTz != withoutTz) { "TIMESTAMP and DATETIME should be different" }
    }

    @Test
    fun testAllJsonTypesMapToJson() {
        val arrayType = columnUtils.toDialectType(ArrayTypeWithoutSchema)
        val objectType = columnUtils.toDialectType(ObjectTypeWithoutSchema)
        val unionType = columnUtils.toDialectType(
            UnionType(options = emptySet(), isLegacyUnion = false)
        )

        assertEquals("JSON", arrayType)
        assertEquals("JSON", objectType)
        assertEquals("JSON", unionType)
    }

    companion object {
        @JvmStatic
        fun formatColumnTestCases(): List<Arguments> = listOf(
            Arguments.of("id", IntegerType, false, "`id` BIGINT NOT NULL"),
            Arguments.of("name", StringType, true, "`name` TEXT"),
            Arguments.of("age", IntegerType, true, "`age` BIGINT"),
            Arguments.of("active", BooleanType, false, "`active` BOOLEAN NOT NULL"),
            Arguments.of("created_at", TimestampTypeWithTimezone, true, "`created_at` TIMESTAMP"),
            Arguments.of("updated_at", TimestampTypeWithoutTimezone, false, "`updated_at` DATETIME NOT NULL"),
            Arguments.of("birth_date", DateType, true, "`birth_date` DATE"),
            Arguments.of("price", NumberType, false, "`price` DECIMAL(38, 9) NOT NULL"),
            Arguments.of("metadata", ObjectTypeWithoutSchema, true, "`metadata` JSON"),
            Arguments.of("tags", ArrayTypeWithoutSchema, true, "`tags` JSON")
        )
    }
}
