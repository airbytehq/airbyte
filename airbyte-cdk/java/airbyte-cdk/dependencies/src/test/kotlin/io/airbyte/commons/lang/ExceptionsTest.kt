/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.lang

import java.io.IOException
import java.util.concurrent.Callable
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class ExceptionsTest {
    @Test
    fun testToRuntime() {
        Assertions.assertEquals("hello", Exceptions.toRuntime<String> { callable("hello", false) })
        Assertions.assertThrows(RuntimeException::class.java) {
            Exceptions.toRuntime(Callable { callable("goodbye", true) })
        }
    }

    @Test
    fun testToRuntimeVoid() {
        val list: MutableList<String> = ArrayList()
        Assertions.assertThrows(RuntimeException::class.java) {
            Exceptions.toRuntime { voidCallable(list, "hello", true) }
        }
        Assertions.assertEquals(0, list.size)

        Exceptions.toRuntime { voidCallable(list, "goodbye", false) }
        Assertions.assertEquals(1, list.size)
        Assertions.assertEquals("goodbye", list[0])
    }

    @Test
    fun testSwallow() {
        Exceptions.swallow { throw RuntimeException() }
        Exceptions.swallow { throw Exception() }
    }

    @Throws(IOException::class)
    private fun callable(input: String, shouldThrow: Boolean): String {
        if (shouldThrow) {
            throw IOException()
        } else {
            return input
        }
    }

    @Throws(IOException::class)
    private fun voidCallable(list: MutableList<String>, input: String, shouldThrow: Boolean) {
        if (shouldThrow) {
            throw IOException()
        } else {
            list.add(input)
        }
    }
}
