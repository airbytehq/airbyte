/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.util

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito
import org.mockito.invocation.InvocationOnMock
import java.util.*
import java.util.function.Supplier

internal class LazyAutoCloseableIteratorTest {
    private var internalIterator: AutoCloseableIterator<String>? = null
    private var iteratorSupplier: Supplier<AutoCloseableIterator<String>>? = null

    @BeforeEach
    fun setup() {
        internalIterator = Mockito.mock(AutoCloseableIterator::class.java) as AutoCloseableIterator<String>
        iteratorSupplier = Mockito.mock(Supplier::class.java)
        Mockito.`when`(iteratorSupplier.get()).thenReturn(internalIterator)
    }

    @Test
    fun testNullInput() {
        Assertions.assertThrows(NullPointerException::class.java) { LazyAutoCloseableIterator<Any>(null, null) }
        val iteratorWithNullSupplier: AutoCloseableIterator<String> = LazyAutoCloseableIterator({ null }, null)
        Assertions.assertThrows(NullPointerException::class.java) { iteratorWithNullSupplier.next() }
    }

    @Test
    @Throws(Exception::class)
    fun testEmptyInput() {
        mockInternalIteratorWith(Collections.emptyIterator())
        val iterator: AutoCloseableIterator<String> = LazyAutoCloseableIterator(iteratorSupplier, null)

        Assertions.assertFalse(iterator.hasNext())
        iterator.close()
        Mockito.verify(internalIterator).close()
    }

    @Test
    @Throws(Exception::class)
    fun test() {
        mockInternalIteratorWith(MoreIterators.of("a", "b", "c"))

        val iterator: AutoCloseableIterator<String> = LazyAutoCloseableIterator(iteratorSupplier, null)
        Mockito.verify(iteratorSupplier, Mockito.never()).get()
        assertNext(iterator, "a")
        Mockito.verify(iteratorSupplier).get()
        Mockito.verifyNoMoreInteractions(iteratorSupplier)
        assertNext(iterator, "b")
        assertNext(iterator, "c")
        iterator.close()
        Mockito.verify(internalIterator).close()
    }

    @Test
    @Throws(Exception::class)
    fun testCloseBeforeSupply() {
        mockInternalIteratorWith(MoreIterators.of("a", "b", "c"))
        val iterator: AutoCloseableIterator<String> = LazyAutoCloseableIterator(iteratorSupplier, null)
        iterator.close()
        Mockito.verify(iteratorSupplier, Mockito.never()).get()
    }

    private fun mockInternalIteratorWith(iterator: Iterator<String>) {
        Mockito.`when`(internalIterator!!.hasNext()).then { a: InvocationOnMock? -> iterator.hasNext() }
        Mockito.`when`(internalIterator!!.next()).then { a: InvocationOnMock? -> iterator.next() }
    }

    private fun assertNext(iterator: Iterator<String>, value: String) {
        Assertions.assertTrue(iterator.hasNext())
        Assertions.assertEquals(value, iterator.next())
    }
}
