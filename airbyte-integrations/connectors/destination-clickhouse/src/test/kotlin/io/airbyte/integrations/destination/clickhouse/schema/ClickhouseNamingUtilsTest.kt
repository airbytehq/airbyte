/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.schema

import java.util.UUID
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class ClickhouseNamingUtilsTest {
    @Test
    fun `toClickHouseCompatibleName replaces special characters with underscores`() {
        Assertions.assertEquals("hello_world", "hello world".toClickHouseCompatibleName())
        Assertions.assertEquals("user_123", "user-123".toClickHouseCompatibleName())
        Assertions.assertEquals(
            "________________________________",
            ",./<>?'\";[]\\:{}|`~!@#\$%^&*()_+-=".toClickHouseCompatibleName()
        )
        Assertions.assertEquals("a_b_c", "a.b.c".toClickHouseCompatibleName())
    }

    @Test
    fun `toClickHouseCompatibleName prepends underscore if starts with digit`() {
        Assertions.assertEquals("_123test", "123test".toClickHouseCompatibleName())
        Assertions.assertEquals("_456", "456".toClickHouseCompatibleName())
        Assertions.assertEquals("value_789", "value_789".toClickHouseCompatibleName())
    }

    @Test
    fun `toClickHouseCompatibleName returns default name for empty result`() {
        val result = "".toClickHouseCompatibleName()
        assert(result.startsWith("default_name_"))
        assert(UUID.fromString(result.substringAfter("default_name_")) != null)
    }

    @Test
    fun `toClickHouseCompatibleName handles mixed cases`() {
        Assertions.assertEquals("Mixed_Case_Name", "Mixed Case Name".toClickHouseCompatibleName())
        Assertions.assertEquals("_1st_Value", "1st Value".toClickHouseCompatibleName())
    }

    @Test
    fun `toClickHouseCompatibleName handles already compatible names`() {
        Assertions.assertEquals("valid_name", "valid_name".toClickHouseCompatibleName())
        Assertions.assertEquals(
            "another_valid_123",
            "another_valid_123".toClickHouseCompatibleName()
        )
    }
}
