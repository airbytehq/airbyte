/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.util

import com.google.common.collect.Iterators
import io.airbyte.commons.concurrency.VoidCallable
import java.util.concurrent.atomic.AtomicBoolean
import java.util.stream.Stream
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito

internal class AutoCloseableIteratorsTest {
    @Test
    @Throws(Exception::class)
    fun testFromIterator() {
        val onClose = Mockito.mock(VoidCallable::class.java)
        val iterator =
            AutoCloseableIterators.fromIterator(MoreIterators.of("a", "b", "c"), onClose, null)

        assertNext(iterator, "a")
        assertNext(iterator, "b")
        assertNext(iterator, "c")
        iterator.close()

        Mockito.verify(onClose).call()
    }

    @Test
    @Throws(Exception::class)
    fun testFromStream() {
        val isClosed = AtomicBoolean(false)
        val stream = Stream.of("a", "b", "c")
        stream.onClose { isClosed.set(true) }

        val iterator = AutoCloseableIterators.fromStream(stream, null)

        assertNext(iterator, "a")
        assertNext(iterator, "b")
        assertNext(iterator, "c")
        iterator.close()

        Assertions.assertTrue(isClosed.get())
    }

    private fun assertNext(iterator: Iterator<String>, value: String) {
        Assertions.assertTrue(iterator.hasNext())
        Assertions.assertEquals(value, iterator.next())
    }

    @Test
    @Throws(Exception::class)
    fun testAppendOnClose() {
        val onClose1 = Mockito.mock(VoidCallable::class.java)
        val onClose2 = Mockito.mock(VoidCallable::class.java)

        val iterator =
            AutoCloseableIterators.fromIterator(MoreIterators.of(1, 2, 3), onClose1, null)
        val iteratorWithExtraClose = AutoCloseableIterators.appendOnClose(iterator, onClose2)

        iteratorWithExtraClose.close()
        Mockito.verify(onClose1).call()
        Mockito.verify(onClose2).call()
    }

    @Test
    fun testTransform() {
        val transform = Iterators.transform(MoreIterators.of(1, 2, 3)) { i: Int -> i + 1 }
        Assertions.assertEquals(listOf(2, 3, 4), MoreIterators.toList(transform))
    }

    @Test
    @Throws(Exception::class)
    fun testConcatWithEagerClose() {
        val onClose1 = Mockito.mock(VoidCallable::class.java)
        val onClose2 = Mockito.mock(VoidCallable::class.java)

        val iterator: AutoCloseableIterator<String> =
            CompositeIterator(
                java.util.List.of(
                    AutoCloseableIterators.fromIterator(MoreIterators.of("a", "b"), onClose1, null),
                    AutoCloseableIterators.fromIterator(MoreIterators.of("d"), onClose2, null)
                ),
                null
            )

        assertOnCloseInvocations(listOf(), java.util.List.of(onClose1, onClose2))
        assertNext(iterator, "a")
        assertNext(iterator, "b")
        assertNext(iterator, "d")
        assertOnCloseInvocations(java.util.List.of(onClose1), java.util.List.of(onClose2))
        Assertions.assertFalse(iterator.hasNext())
        assertOnCloseInvocations(java.util.List.of(onClose1, onClose2), listOf())

        iterator.close()

        Mockito.verify(onClose1, Mockito.times(1)).call()
        Mockito.verify(onClose2, Mockito.times(1)).call()
    }

    @Throws(Exception::class)
    private fun assertOnCloseInvocations(
        haveClosed: List<VoidCallable>,
        haveNotClosed: List<VoidCallable>
    ) {
        for (voidCallable in haveClosed) {
            Mockito.verify(voidCallable).call()
        }

        for (voidCallable in haveNotClosed) {
            Mockito.verify(voidCallable, Mockito.never()).call()
        }
    }
}
