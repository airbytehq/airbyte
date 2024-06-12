/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.text

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class NamesTest {
    @Test
    fun testToAlphanumericAndUnderscore() {
        Assertions.assertEquals("users", Names.toAlphanumericAndUnderscore("users"))
        Assertions.assertEquals("users123", Names.toAlphanumericAndUnderscore("users123"))
        Assertions.assertEquals("UsErS", Names.toAlphanumericAndUnderscore("UsErS"))
        Assertions.assertEquals(
            "users_USE_special_____",
            Names.toAlphanumericAndUnderscore("users USE special !@#$")
        )
    }

    @Test
    fun testDoubleQuote() {
        Assertions.assertEquals("\"abc\"", Names.doubleQuote("abc"))
        Assertions.assertEquals("\"abc\"", Names.doubleQuote("\"abc\""))
        Assertions.assertThrows(IllegalStateException::class.java) { Names.doubleQuote("\"abc") }
        Assertions.assertThrows(IllegalStateException::class.java) { Names.doubleQuote("abc\"") }
    }

    @Test
    fun testSimpleQuote() {
        Assertions.assertEquals("'abc'", Names.singleQuote("abc"))
        Assertions.assertEquals("'abc'", Names.singleQuote("'abc'"))
        Assertions.assertThrows(IllegalStateException::class.java) { Names.singleQuote("'abc") }
        Assertions.assertThrows(IllegalStateException::class.java) { Names.singleQuote("abc'") }
    }
}
