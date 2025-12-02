/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.util

import java.util.*
import java.util.function.Supplier
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito
import org.mockito.invocation.InvocationOnMock
import org.mockito.kotlin.mock

internal class LazyAutoCloseableIteratorTest {
    private var internalIterator: AutoCloseableIterator<String> = mock()
    private var iteratorSupplier: Supplier<AutoCloseableIterator<String>> = mock()

    @BeforeEach
    fun setup() {
        internalIterator = mock()
        iteratorSupplier = mock()
        Mockito.`when`(iteratorSupplier.get()).thenReturn(internalIterator)
    }

    @Test
    @Throws(Exception::class)
    fun testEmptyInput() {
        mockInternalIteratorWith(Collections.emptyIterator())
        val iterator: AutoCloseableIterator<String> =
            LazyAutoCloseableIterator(iteratorSupplier, null)

        Assertions.assertFalse(iterator.hasNext())
        iterator.close()
        Mockito.verify(internalIterator).close()
    }

    @Test
    @Throws(Exception::class)
    fun test() {
        mockInternalIteratorWith(MoreIterators.of("a", "b", "c"))

        val iterator: AutoCloseableIterator<String> =
            LazyAutoCloseableIterator(iteratorSupplier, null)
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
        val iterator: AutoCloseableIterator<String> =
            LazyAutoCloseableIterator(iteratorSupplier, null)
        iterator.close()
        Mockito.verify(iteratorSupplier, Mockito.never()).get()
    }

    private fun mockInternalIteratorWith(iterator: Iterator<String>) {
        Mockito.`when`(internalIterator!!.hasNext()).then { a: InvocationOnMock ->
            iterator.hasNext()
        }
        Mockito.`when`(internalIterator!!.next()).then { a: InvocationOnMock -> iterator.next() }
    }

    private fun assertNext(iterator: Iterator<String>, value: String) {
        Assertions.assertTrue(iterator.hasNext())
        Assertions.assertEquals(value, iterator.next())
    }
}
