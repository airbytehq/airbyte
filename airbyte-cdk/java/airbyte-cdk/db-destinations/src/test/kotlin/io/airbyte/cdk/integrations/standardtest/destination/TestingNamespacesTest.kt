/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.destination

import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class TestingNamespacesTest {
    @Test
    fun testGenerate() {
        val namespace =
            TestingNamespaces.generate()
                .split("_".toRegex())
                .dropLastWhile { it.isEmpty() }
                .toTypedArray()
        Assertions.assertEquals("test", namespace[0])
        Assertions.assertEquals(
            FORMATTER.format(Instant.now().atZone(ZoneId.of("UTC")).toLocalDate()),
            namespace[1]
        )
        Assertions.assertFalse(namespace[2].isBlank())
    }

    @Test
    fun testGenerateWithPrefix() {
        val namespace =
            TestingNamespaces.generate("myprefix")
                .split("_".toRegex())
                .dropLastWhile { it.isEmpty() }
                .toTypedArray()
        Assertions.assertEquals("myprefix", namespace[0])
        Assertions.assertEquals("test", namespace[1])
        Assertions.assertEquals(
            FORMATTER.format(Instant.now().atZone(ZoneId.of("UTC")).toLocalDate()),
            namespace[2]
        )
        Assertions.assertFalse(namespace[3].isBlank())
    }

    @Test
    fun testIsOlderThan2Days() {
        Assertions.assertFalse(
            TestingNamespaces.isOlderThan2Days("myprefix_test_" + getDate(0) + "_12345")
        )
        Assertions.assertTrue(
            TestingNamespaces.isOlderThan2Days("myprefix_test_" + getDate(2) + "_12345")
        )
    }

    @Test
    fun doesNotFailOnNonConventionalNames() {
        Assertions.assertFalse(TestingNamespaces.isOlderThan2Days("12345"))
        Assertions.assertFalse(TestingNamespaces.isOlderThan2Days("test_12345"))
        Assertions.assertFalse(TestingNamespaces.isOlderThan2Days("hello_test_12345"))
        Assertions.assertFalse(
            TestingNamespaces.isOlderThan2Days("myprefix_test1_" + getDate(2) + "_12345")
        )
    }

    companion object {
        private val FORMATTER: DateTimeFormatter = DateTimeFormatter.ofPattern("yyyyMMdd")

        private fun getDate(daysAgo: Int): String {
            return FORMATTER.format(
                Instant.now()
                    .minus(daysAgo.toLong(), ChronoUnit.DAYS)
                    .atZone(ZoneId.of("UTC"))
                    .toLocalDate()
            )
        }
    }
}
