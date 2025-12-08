/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema

import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class ColumnNameResolverTest {
    @MockK private lateinit var mapper: TableSchemaMapper

    @Test
    fun `handles no collisions`() {
        val resolver = ColumnNameResolver(mapper)
        val columns = setOf("col1", "col2", "col3")

        every { mapper.toColumnName("col1") } returns "col1"
        every { mapper.toColumnName("col2") } returns "col2"
        every { mapper.toColumnName("col3") } returns "col3"
        every { mapper.colsConflict(any(), any()) } returns false

        val result = resolver.getColumnNameMapping(columns)

        assertEquals(3, result.size)
        assertEquals("col1", result["col1"])
        assertEquals("col2", result["col2"])
        assertEquals("col3", result["col3"])
    }

    @Test
    fun `handles simple collision with numeric suffix`() {
        val resolver = ColumnNameResolver(mapper)
        val columns = setOf("name", "Name")

        every { mapper.toColumnName("name") } returns "name"
        every { mapper.toColumnName("Name") } returns "name"
        every { mapper.toColumnName("Name_1") } returns "name_1"
        every { mapper.colsConflict(any(), any()) } answers { args[0] == args[1] }

        val result = resolver.getColumnNameMapping(columns)

        assertEquals(2, result.size)
        assertEquals("name", result["name"])
        assertEquals("name_1", result["Name"])
    }

    @Test
    fun `handles multiple collisions with incremental suffixes`() {
        val resolver = ColumnNameResolver(mapper)
        val columns = setOf("col", "Col", "COL")

        every { mapper.toColumnName("col") } returns "col"
        every { mapper.toColumnName("Col") } returns "col"
        every { mapper.toColumnName("COL") } returns "col"
        every { mapper.toColumnName("Col_1") } returns "col_1"
        every { mapper.toColumnName("COL_1") } returns "col_1"
        every { mapper.toColumnName("COL_2") } returns "col_2"
        every { mapper.colsConflict(any(), any()) } answers { args[0] == args[1] }

        val result = resolver.getColumnNameMapping(columns)

        assertEquals(3, result.size)
        assertEquals("col", result["col"])
        assertEquals("col_1", result["Col"])
        assertEquals("col_2", result["COL"])
    }

    // We're testing some internals here, but I think it's important to validate this behavior as it
    // represents an API contract with the destination. Any changes here will potentially affect
    // customer destination schemas.
    @Test
    fun `handles truncation with super resolution`() {
        val resolver = ColumnNameResolver(mapper)
        val shortName = "short"
        val longName1 = "a".repeat(100)
        val longName2 = "a".repeat(50)
        val columns = setOf("short", longName1, longName2)

        every { mapper.toColumnName(shortName) } returns "short"
        every { mapper.toColumnName(longName1) } returns "truncated"
        every { mapper.toColumnName(longName2) } returns "truncated"
        every { mapper.toColumnName("${longName1}_1") } returns "truncated"
        every { mapper.toColumnName("${longName2}_1") } returns "truncated"
        every { mapper.toColumnName("aa46aa") } returns "different"
        every { mapper.colsConflict(any(), any()) } answers { args[0] == args[1] }

        val result = resolver.getColumnNameMapping(columns)

        assertEquals(3, result.size)
        assertEquals("short", result["short"])
        assertEquals("truncated", result[longName1])
        assertEquals("different", result[longName2])
    }

    @Test
    fun `throws exception when super resolution fails`() {
        val resolver = ColumnNameResolver(mapper)
        val shortName = "short"
        val longName1 = "a".repeat(100)
        val longName2 = "a".repeat(50)
        val columns = setOf("short", longName1, longName2)

        every { mapper.toColumnName(shortName) } returns "short"
        every { mapper.toColumnName(longName1) } returns "truncated"
        every { mapper.toColumnName(longName2) } returns "truncated"
        every { mapper.toColumnName("${longName1}_1") } returns "truncated"
        every { mapper.toColumnName("${longName2}_1") } returns "truncated"
        every { mapper.toColumnName("aa46aa") } returns "truncated"
        every { mapper.colsConflict(any(), any()) } answers { args[0] == args[1] }

        assertThrows(IllegalArgumentException::class.java) {
            resolver.getColumnNameMapping(columns)
        }
    }

    @Test
    fun `handles empty set`() {
        val resolver = ColumnNameResolver(mapper)
        val result = resolver.getColumnNameMapping(emptySet())

        assertEquals(0, result.size)
    }

    @Test
    fun `preserves original names when no processing needed`() {
        val resolver = ColumnNameResolver(mapper)
        val columns = setOf("valid_name_1", "valid_name_2")

        every { mapper.toColumnName("valid_name_1") } returns "valid_name_1"
        every { mapper.toColumnName("valid_name_2") } returns "valid_name_2"
        every { mapper.colsConflict(any(), any()) } returns false

        val result = resolver.getColumnNameMapping(columns)

        assertEquals(2, result.size)
        assertEquals("valid_name_1", result["valid_name_1"])
        assertEquals("valid_name_2", result["valid_name_2"])
    }
}
