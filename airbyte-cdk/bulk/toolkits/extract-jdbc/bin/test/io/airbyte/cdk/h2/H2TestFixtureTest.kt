/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.h2

import java.sql.DriverManager
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class H2TestFixtureTest {
    val h2 = H2TestFixture()

    @Test
    fun testMem() {
        h2.execute("CREATE SCHEMA hello")
        val expected: List<List<Any?>> =
            listOf(listOf("HELLO"), listOf("INFORMATION_SCHEMA"), listOf("PUBLIC"))
        Assertions.assertEquals(expected, h2.query("SHOW SCHEMAS"))
    }

    @Test
    fun testTcp() {
        val actual: String =
            DriverManager.getConnection(h2.jdbcUrl).use { it.metaData.databaseProductName }
        Assertions.assertEquals("H2", actual)
    }
}
