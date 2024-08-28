/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.util

import com.google.common.collect.ImmutableList
import io.airbyte.commons.concurrency.VoidCallable
import io.airbyte.commons.stream.AirbyteStreamStatusHolder
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair
import java.util.function.Consumer
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito
import org.mockito.kotlin.any
import org.mockito.kotlin.mock

internal class CompositeIteratorTest {
    private lateinit var onClose1: VoidCallable
    private lateinit var onClose2: VoidCallable
    private lateinit var onClose3: VoidCallable
    private lateinit var airbyteStreamStatusConsumer: Consumer<AirbyteStreamStatusHolder>
    private var airbyteStream1: AirbyteStreamNameNamespacePair? = null
    private var airbyteStream2: AirbyteStreamNameNamespacePair? = null
    private var airbyteStream3: AirbyteStreamNameNamespacePair? = null

    @BeforeEach
    fun setup() {
        onClose1 = Mockito.mock(VoidCallable::class.java)
        onClose2 = Mockito.mock(VoidCallable::class.java)
        onClose3 = Mockito.mock(VoidCallable::class.java)
        airbyteStreamStatusConsumer = mock()
        airbyteStream1 = AirbyteStreamNameNamespacePair("stream1", "namespace")
        airbyteStream2 = AirbyteStreamNameNamespacePair("stream2", "namespace")
        airbyteStream3 = AirbyteStreamNameNamespacePair("stream3", "namespace")
    }

    @Test
    fun testNullInput() {
        Mockito.verify(airbyteStreamStatusConsumer, Mockito.times(0)).accept(any())
    }

    @Test
    fun testEmptyInput() {
        val iterator: AutoCloseableIterator<String> =
            CompositeIterator(
                emptyList<AutoCloseableIterator<String>>(),
                airbyteStreamStatusConsumer
            )
        Assertions.assertFalse(iterator.hasNext())
        Mockito.verify(airbyteStreamStatusConsumer, Mockito.times(0)).accept(any())
    }

    @Test
    @Throws(Exception::class)
    fun testMultipleIterators() {
        val iterator: AutoCloseableIterator<String> =
            CompositeIterator<String>(
                ImmutableList.of(
                    AutoCloseableIterators.fromIterator(
                        MoreIterators.of("a", "b", "c"),
                        onClose1,
                        airbyteStream1
                    ),
                    AutoCloseableIterators.fromIterator(
                        MoreIterators.of("d", "e", "f"),
                        onClose2,
                        airbyteStream2
                    ),
                    AutoCloseableIterators.fromIterator(
                        MoreIterators.of("g", "h", "i"),
                        onClose3,
                        airbyteStream3
                    )
                ),
                airbyteStreamStatusConsumer,
                true
            )

        assertOnCloseInvocations(ImmutableList.of(), ImmutableList.of(onClose1, onClose2, onClose3))
        assertNext(iterator, "a")
        assertNext(iterator, "b")
        assertNext(iterator, "c")
        assertNext(iterator, "d")
        assertOnCloseInvocations(ImmutableList.of(onClose1), ImmutableList.of(onClose2, onClose3))
        assertNext(iterator, "e")
        assertNext(iterator, "f")
        assertNext(iterator, "g")
        assertOnCloseInvocations(ImmutableList.of(onClose1, onClose2), ImmutableList.of(onClose3))
        assertNext(iterator, "h")
        assertNext(iterator, "i")
        assertOnCloseInvocations(ImmutableList.of(onClose1, onClose2), ImmutableList.of(onClose3))
        Assertions.assertFalse(iterator.hasNext())
        assertOnCloseInvocations(ImmutableList.of(onClose1, onClose2, onClose3), ImmutableList.of())

        iterator.close()

        Mockito.verify(onClose1, Mockito.times(1)).call()
        Mockito.verify(onClose2, Mockito.times(1)).call()
        Mockito.verify(onClose3, Mockito.times(1)).call()
        Mockito.verify(airbyteStreamStatusConsumer, Mockito.times(9)).accept(any())
    }

    @Test
    @Throws(Exception::class)
    fun testWithEmptyIterators() {
        val iterator: AutoCloseableIterator<String> =
            CompositeIterator<String>(
                ImmutableList.of(
                    AutoCloseableIterators.fromIterator(
                        MoreIterators.of("a", "b", "c"),
                        onClose1,
                        airbyteStream1
                    ),
                    AutoCloseableIterators.fromIterator(
                        MoreIterators.of(),
                        onClose2,
                        airbyteStream2
                    ),
                    AutoCloseableIterators.fromIterator(
                        MoreIterators.of("g", "h", "i"),
                        onClose3,
                        airbyteStream3
                    )
                ),
                airbyteStreamStatusConsumer,
                true
            )

        assertOnCloseInvocations(ImmutableList.of(), ImmutableList.of(onClose1, onClose2, onClose3))
        assertNext(iterator, "a")
        assertNext(iterator, "b")
        assertNext(iterator, "c")
        assertNext(iterator, "g")
        assertOnCloseInvocations(ImmutableList.of(onClose1, onClose2), ImmutableList.of(onClose3))
        assertNext(iterator, "h")
        assertNext(iterator, "i")
        Assertions.assertFalse(iterator.hasNext())
        assertOnCloseInvocations(ImmutableList.of(onClose1, onClose2, onClose3), ImmutableList.of())
        Mockito.verify(airbyteStreamStatusConsumer, Mockito.times(8)).accept(any())
    }

    @Test
    @Throws(Exception::class)
    fun testCloseBeforeUsingItUp() {
        val iterator: AutoCloseableIterator<String> =
            CompositeIterator<String>(
                ImmutableList.of(
                    AutoCloseableIterators.fromIterator(
                        MoreIterators.of("a", "b", "c"),
                        onClose1,
                        airbyteStream1
                    )
                ),
                airbyteStreamStatusConsumer,
                true
            )

        assertOnCloseInvocations(ImmutableList.of(), ImmutableList.of(onClose1))
        assertNext(iterator, "a")
        assertNext(iterator, "b")
        assertOnCloseInvocations(ImmutableList.of(), ImmutableList.of(onClose1))
        iterator.close()
        assertOnCloseInvocations(ImmutableList.of(onClose1), ImmutableList.of())
        Mockito.verify(airbyteStreamStatusConsumer, Mockito.times(2)).accept(any())
    }

    @Test
    @Throws(Exception::class)
    fun testCannotOperateAfterClosing() {
        val iterator: AutoCloseableIterator<String> =
            CompositeIterator<String>(
                ImmutableList.of(
                    AutoCloseableIterators.fromIterator(
                        MoreIterators.of("a", "b", "c"),
                        onClose1,
                        airbyteStream1
                    )
                ),
                airbyteStreamStatusConsumer,
                true
            )

        assertOnCloseInvocations(ImmutableList.of(), ImmutableList.of(onClose1))
        assertNext(iterator, "a")
        assertNext(iterator, "b")
        iterator.close()
        Assertions.assertThrows(IllegalStateException::class.java) { iterator.hasNext() }
        Assertions.assertThrows(IllegalStateException::class.java) { iterator.next() }
        iterator.close() // still allowed to close again.
        Mockito.verify(airbyteStreamStatusConsumer, Mockito.times(2)).accept(any())
    }

    private fun assertNext(iterator: Iterator<String>, value: String) {
        Assertions.assertTrue(iterator.hasNext())
        Assertions.assertEquals(value, iterator.next())
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
