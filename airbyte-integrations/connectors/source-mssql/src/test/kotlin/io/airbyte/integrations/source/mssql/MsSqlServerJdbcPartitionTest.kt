/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.IntFieldType
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Test

/**
 * Tests for MSSQL partition logic, specifically focusing on numeric type handling and null safety
 * fixes.
 */
class MsSqlServerJdbcPartitionTest {

    @Test
    fun `test stateValueToJsonNode converts NUMBER to BigDecimal`() {
        // This prevents precision loss and type mismatch issues
        val field = Field("numericId", BigDecimalFieldType)

        // Convert state value "13" using NUMBER type
        val result = stateValueToJsonNode(field, "13")

        assertNotNull(result)
        assertEquals(13, result.decimalValue().toInt())
        // Verify it's BigDecimal by checking the node type
        assert(result.isBigDecimal) { "Expected BigDecimal node but got ${result.nodeType}" }
    }

    @Test
    fun `test stateValueToJsonNode handles large NUMERIC values without precision loss`() {
        // Test that large NUMERIC values don't lose precision when converted
        val field = Field("largeNumericId", BigDecimalFieldType)
        val largeValue = "12345678901234567890"

        val result = stateValueToJsonNode(field, largeValue)

        assertNotNull(result)
        assertEquals(largeValue, result.decimalValue().toPlainString())
    }

    @Test
    fun `test stateValueToJsonNode handles decimal NUMERIC values`() {
        // Test that decimal NUMERIC values are preserved correctly
        val field = Field("decimalValue", BigDecimalFieldType)
        val decimalValue = "123.456"

        val result = stateValueToJsonNode(field, decimalValue)

        assertNotNull(result)
        assertEquals(decimalValue, result.decimalValue().toPlainString())
    }

    @Test
    fun `test stateValueToJsonNode handles INTEGER values`() {
        // Test that INTEGER types work correctly
        val field = Field("integerId", IntFieldType)

        val result = stateValueToJsonNode(field, "42")

        assertNotNull(result)
        assertEquals(42, result.bigIntegerValue().toInt())
    }

    @Test
    fun `test stateValueToJsonNode handles empty string for NUMBER`() {
        // Test that empty string returns null node
        val field = Field("numericId", BigDecimalFieldType)

        val result = stateValueToJsonNode(field, "")

        assertNotNull(result)
        assert(result.isNull) { "Expected null node for empty string" }
    }

    @Test
    fun `test stateValueToJsonNode handles null for NUMBER`() {
        // Test that null string returns null node
        val field = Field("numericId", BigDecimalFieldType)

        val result = stateValueToJsonNode(field, null)

        assertNotNull(result)
        assert(result.isNull) { "Expected null node for null string" }
    }

    @Test
    fun `test stateValueToJsonNode handles string null for NUMBER`() {
        // Test that the string "null" (not null value) returns null node
        // This can happen when JSON serialization converts null to string "null"
        val field = Field("numericId", BigDecimalFieldType)

        val result = stateValueToJsonNode(field, "null")

        assertNotNull(result)
        assert(result.isNull) { "Expected null node for string 'null'" }
    }

    @Test
    fun `test stateValueToJsonNode handles string null for INTEGER`() {
        // Test that the string "null" (not null value) returns null node for INTEGER
        val field = Field("integerId", IntFieldType)

        val result = stateValueToJsonNode(field, "null")

        assertNotNull(result)
        assert(result.isNull) { "Expected null node for string 'null'" }
    }
}
