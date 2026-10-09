/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.postgres.operations

import io.airbyte.cdk.discover.SystemType
import java.sql.JDBCType
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class PgSystemTypeTest {

    private fun pgType(typeName: String, jdbcType: JDBCType) =
        PostgresSourceFieldTypeMapper.PgSystemType(
            SystemType(typeName = typeName, typeCode = jdbcType.vendorTypeNumber)
        )

    @Test
    fun `array type name with underscore prefix is an array of its element type`() {
        val type = pgType("_int4", JDBCType.ARRAY)
        assertTrue(type.isArray)
        assertEquals("int4", type.scalarTypeName)
        assertEquals(JDBCType.INTEGER, type.scalarJdbcType)
    }

    @Test
    fun `non-array type name with underscore prefix is not an array`() {
        val type = pgType("_status", JDBCType.VARCHAR)
        assertFalse(type.isArray)
        assertEquals("_status", type.scalarTypeName)
        assertEquals(JDBCType.VARCHAR, type.scalarJdbcType)
    }

    @Test
    fun `schema-qualified array type name is an array of a generic element type`() {
        val type = pgType("\"s2\".\"_kind\"", JDBCType.ARRAY)
        assertTrue(type.isArray)
        assertEquals("\"s2\".\"_kind\"", type.scalarTypeName)
        assertEquals(JDBCType.OTHER, type.scalarJdbcType)
    }

    @Test
    fun `schema-qualified array of an extension type is not mapped by element name`() {
        val type = pgType("\"extensions\".\"_hstore\"", JDBCType.ARRAY)
        assertTrue(type.isArray)
        assertEquals(JDBCType.OTHER, type.scalarJdbcType)
    }

    @Test
    fun `schema-qualified array of a type named like a built-in is not mapped as the built-in`() {
        val type = pgType("\"s2\".\"_int4\"", JDBCType.ARRAY)
        assertTrue(type.isArray)
        assertEquals(JDBCType.OTHER, type.scalarJdbcType)
    }

    @Test
    fun `schema-qualified array with quotes or dots in the names is an array`() {
        // The driver doesn't escape quotes inside quoted names: schema s"2 comes back as "s"2".
        for (name in listOf("\"s\"2\".\"_kind\"", "\"Mixed.Case\".\"_Kind\"")) {
            val type = pgType(name, JDBCType.ARRAY)
            assertTrue(type.isArray, name)
            assertEquals(JDBCType.OTHER, type.scalarJdbcType, name)
        }
    }

    @Test
    fun `array type name that is neither underscore-prefixed nor schema-qualified throws`() {
        assertThrows<IllegalStateException> { pgType("kind", JDBCType.ARRAY) }
        assertThrows<IllegalStateException> { pgType("\"s2\".\"kind\"", JDBCType.ARRAY) }
    }
}
