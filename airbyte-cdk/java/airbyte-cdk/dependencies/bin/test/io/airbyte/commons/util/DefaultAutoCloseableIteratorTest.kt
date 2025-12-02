/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.util

import io.airbyte.commons.concurrency.VoidCallable
import java.util.*
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito

internal class DefaultAutoCloseableIteratorTest {

    @Test
    @Throws(Exception::class)
    fun testEmptyInput() {
        val onClose = Mockito.mock(VoidCallable::class.java)
        val iterator: AutoCloseableIterator<String> =
            DefaultAutoCloseableIterator(Collections.emptyIterator(), onClose, null)
        Assertions.assertFalse(iterator.hasNext())
        iterator.close()
        Mockito.verify(onClose).call()
    }

    @Test
    @Throws(Exception::class)
    fun test() {
        val onClose = Mockito.mock(VoidCallable::class.java)
        val iterator: AutoCloseableIterator<String> =
            DefaultAutoCloseableIterator(MoreIterators.of("a", "b", "c"), onClose, null)

        assertNext(iterator, "a")
        assertNext(iterator, "b")
        assertNext(iterator, "c")
        iterator.close()

        Mockito.verify(onClose).call()
    }

    @Test
    @Throws(Exception::class)
    fun testCannotOperateAfterClosing() {
        val onClose = Mockito.mock(VoidCallable::class.java)
        val iterator: AutoCloseableIterator<String> =
            DefaultAutoCloseableIterator(MoreIterators.of("a", "b", "c"), onClose, null)

        assertNext(iterator, "a")
        assertNext(iterator, "b")
        iterator.close()
        Assertions.assertThrows(IllegalStateException::class.java) { iterator.hasNext() }
        Assertions.assertThrows(IllegalStateException::class.java) { iterator.next() }
        iterator.close() // still allowed to close again.
    }

    private fun assertNext(iterator: Iterator<String>, value: String) {
        Assertions.assertTrue(iterator.hasNext())
        Assertions.assertEquals(value, iterator.next())
    }
}
