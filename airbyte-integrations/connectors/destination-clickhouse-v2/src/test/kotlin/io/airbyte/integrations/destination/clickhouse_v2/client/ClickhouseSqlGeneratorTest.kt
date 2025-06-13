/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.client

import org.junit.jupiter.api.Test

class ClickhouseSqlGeneratorTest {
    val clickhouseSqlGenerator = ClickhouseSqlGenerator()

    @Test
    fun testCreateNamespace() {
        val namespace = "test_namespace"
        val expected = "CREATE DATABASE IF NOT EXISTS `$namespace`;"
        val actual = clickhouseSqlGenerator.createNamespace(namespace)
        assert(expected == actual) { "Expected: $expected, but got: $actual" }
    }
}
