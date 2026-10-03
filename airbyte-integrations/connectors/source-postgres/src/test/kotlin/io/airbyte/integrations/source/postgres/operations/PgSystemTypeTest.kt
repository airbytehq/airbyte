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
    fun `array type name without underscore prefix throws`() {
        assertThrows<IllegalStateException> { pgType("\"s2\".\"_kind\"", JDBCType.ARRAY) }
    }
}
