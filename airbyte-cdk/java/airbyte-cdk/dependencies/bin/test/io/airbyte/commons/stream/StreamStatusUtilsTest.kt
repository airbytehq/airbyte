/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.stream

import io.airbyte.commons.util.AirbyteStreamAware
import io.airbyte.commons.util.AutoCloseableIterator
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import java.util.*
import java.util.function.Consumer
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith
import org.mockito.ArgumentCaptor
import org.mockito.ArgumentMatchers
import org.mockito.Captor
import org.mockito.Mockito
import org.mockito.junit.jupiter.MockitoExtension
import org.mockito.kotlin.mock

/** Test suite for the [StreamStatusUtils] class. */
@ExtendWith(MockitoExtension::class)
internal class StreamStatusUtilsTest {
    @Captor
    private val airbyteStreamStatusHolderArgumentCaptor:
        ArgumentCaptor<AirbyteStreamStatusHolder>? =
        null

    @Test
    fun testCreateStreamStatusConsumerWrapper() {
        val stream: AutoCloseableIterator<AirbyteMessage> = mock()
        val streamStatusEmitter = Optional.empty<Consumer<AirbyteStreamStatusHolder>>()
        val messageConsumer: Consumer<AirbyteMessage> = mock()

        val wrappedMessageConsumer =
            StreamStatusUtils.statusTrackingRecordCollector(
                stream,
                messageConsumer,
                streamStatusEmitter
            )

        Assertions.assertNotEquals(messageConsumer, wrappedMessageConsumer)
    }

    @Test
    fun testStreamStatusConsumerWrapperProduceStreamStatus() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val stream: AutoCloseableIterator<AirbyteMessage> = mock()
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)
        val messageConsumer: Consumer<AirbyteMessage> = mock()
        val airbyteMessage = Mockito.mock(AirbyteMessage::class.java)

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.of(airbyteStream))

        val wrappedMessageConsumer =
            StreamStatusUtils.statusTrackingRecordCollector(
                stream,
                messageConsumer,
                streamStatusEmitter
            )

        Assertions.assertNotEquals(messageConsumer, wrappedMessageConsumer)

        wrappedMessageConsumer.accept(airbyteMessage)
        wrappedMessageConsumer.accept(airbyteMessage)
        wrappedMessageConsumer.accept(airbyteMessage)

        Mockito.verify(messageConsumer, Mockito.times(3)).accept(ArgumentMatchers.any())
        Mockito.verify(statusEmitter, Mockito.times(1))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
        Assertions.assertEquals(
            AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.RUNNING,
            airbyteStreamStatusHolderArgumentCaptor.value.toTraceMessage().streamStatus.status
        )
    }

    @Test
    fun testEmitRunningStreamStatusIterator() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val stream: AutoCloseableIterator<AirbyteMessage> = mock()
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.of(airbyteStream))

        StreamStatusUtils.emitRunningStreamStatus(stream, streamStatusEmitter)

        Mockito.verify(statusEmitter, Mockito.times(1))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
        Assertions.assertEquals(
            AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.RUNNING,
            airbyteStreamStatusHolderArgumentCaptor.value.toTraceMessage().streamStatus.status
        )
    }

    @Test
    fun testEmitRunningStreamStatusIteratorEmptyAirbyteStream() {
        val stream: AutoCloseableIterator<AirbyteMessage> = mock()
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.empty())

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitRunningStreamStatus(stream, streamStatusEmitter)
        }
        Mockito.verify(statusEmitter, Mockito.times(0))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
    }

    @Test
    fun testEmitRunningStreamStatusIteratorEmptyStatusEmitter() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val stream: AutoCloseableIterator<AirbyteMessage> = mock()
        val streamStatusEmitter = Optional.empty<Consumer<AirbyteStreamStatusHolder>>()

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.of(airbyteStream))

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitRunningStreamStatus(stream, streamStatusEmitter)
        }
    }

    @Test
    fun testEmitRunningStreamStatusAirbyteStreamAware() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val stream = Mockito.mock(AirbyteStreamAware::class.java)
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.of(airbyteStream))

        StreamStatusUtils.emitRunningStreamStatus(stream, streamStatusEmitter)

        Mockito.verify(statusEmitter, Mockito.times(1))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
        Assertions.assertEquals(
            AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.RUNNING,
            airbyteStreamStatusHolderArgumentCaptor.value.toTraceMessage().streamStatus.status
        )
    }

    @Test
    fun testEmitRunningStreamStatusAirbyteStreamAwareEmptyStream() {
        val stream = Mockito.mock(AirbyteStreamAware::class.java)
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.empty())

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitRunningStreamStatus(stream, streamStatusEmitter)
        }
        Mockito.verify(statusEmitter, Mockito.times(0))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
    }

    @Test
    fun testEmitRunningStreamStatusAirbyteStreamAwareEmptyStatusEmitter() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val stream = Mockito.mock(AirbyteStreamAware::class.java)
        val streamStatusEmitter = Optional.empty<Consumer<AirbyteStreamStatusHolder>>()

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.of(airbyteStream))

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitRunningStreamStatus(stream, streamStatusEmitter)
        }
    }

    @Test
    fun testEmitRunningStreamStatusAirbyteStream() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        StreamStatusUtils.emitRunningStreamStatus(Optional.of(airbyteStream), streamStatusEmitter)

        Mockito.verify(statusEmitter, Mockito.times(1))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
        Assertions.assertEquals(
            AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.RUNNING,
            airbyteStreamStatusHolderArgumentCaptor.value.toTraceMessage().streamStatus.status
        )
    }

    @Test
    fun testEmitRunningStreamStatusEmptyAirbyteStream() {
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitRunningStreamStatus(Optional.empty(), streamStatusEmitter)
        }
        Mockito.verify(statusEmitter, Mockito.times(0))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
    }

    @Test
    fun testEmitRunningStreamStatusAirbyteStreamEmptyStatusEmitter() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val streamStatusEmitter = Optional.empty<Consumer<AirbyteStreamStatusHolder>>()

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitRunningStreamStatus(
                Optional.of(airbyteStream),
                streamStatusEmitter
            )
        }
    }

    @Test
    fun testEmitStartedStreamStatusIterator() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val stream: AutoCloseableIterator<AirbyteMessage> = mock()
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.of(airbyteStream))

        StreamStatusUtils.emitStartStreamStatus(stream, streamStatusEmitter)

        Mockito.verify(statusEmitter, Mockito.times(1))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
        Assertions.assertEquals(
            AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.STARTED,
            airbyteStreamStatusHolderArgumentCaptor.value.toTraceMessage().streamStatus.status
        )
    }

    @Test
    fun testEmitStartedStreamStatusIteratorEmptyAirbyteStream() {
        val stream: AutoCloseableIterator<AirbyteMessage> = mock()
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.empty())

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitStartStreamStatus(stream, streamStatusEmitter)
        }
        Mockito.verify(statusEmitter, Mockito.times(0))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
    }

    @Test
    fun testEmitStartedStreamStatusIteratorEmptyStatusEmitter() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val stream: AutoCloseableIterator<AirbyteMessage> = mock()
        val streamStatusEmitter = Optional.empty<Consumer<AirbyteStreamStatusHolder>>()

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.of(airbyteStream))

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitStartStreamStatus(stream, streamStatusEmitter)
        }
    }

    @Test
    fun testEmitStartedStreamStatusAirbyteStreamAware() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val stream = Mockito.mock(AirbyteStreamAware::class.java)
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.of(airbyteStream))

        StreamStatusUtils.emitStartStreamStatus(stream, streamStatusEmitter)

        Mockito.verify(statusEmitter, Mockito.times(1))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
        Assertions.assertEquals(
            AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.STARTED,
            airbyteStreamStatusHolderArgumentCaptor.value.toTraceMessage().streamStatus.status
        )
    }

    @Test
    fun testEmitStartedStreamStatusAirbyteStreamAwareEmptyStream() {
        val stream = Mockito.mock(AirbyteStreamAware::class.java)
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.empty())

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitStartStreamStatus(stream, streamStatusEmitter)
        }
        Mockito.verify(statusEmitter, Mockito.times(0))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
    }

    @Test
    fun testEmitStartedStreamStatusAirbyteStreamAwareEmptyStatusEmitter() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val stream = Mockito.mock(AirbyteStreamAware::class.java)
        val streamStatusEmitter = Optional.empty<Consumer<AirbyteStreamStatusHolder>>()

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.of(airbyteStream))

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitStartStreamStatus(stream, streamStatusEmitter)
        }
    }

    @Test
    fun testEmitStartedStreamStatusAirbyteStream() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        StreamStatusUtils.emitStartStreamStatus(Optional.of(airbyteStream), streamStatusEmitter)

        Mockito.verify(statusEmitter, Mockito.times(1))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
        Assertions.assertEquals(
            AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.STARTED,
            airbyteStreamStatusHolderArgumentCaptor.value.toTraceMessage().streamStatus.status
        )
    }

    @Test
    fun testEmitStartedStreamStatusEmptyAirbyteStream() {
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitStartStreamStatus(Optional.empty(), streamStatusEmitter)
        }
        Mockito.verify(statusEmitter, Mockito.times(0))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
    }

    @Test
    fun testEmitStartedStreamStatusAirbyteStreamEmptyStatusEmitter() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val streamStatusEmitter = Optional.empty<Consumer<AirbyteStreamStatusHolder>>()

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitStartStreamStatus(Optional.of(airbyteStream), streamStatusEmitter)
        }
    }

    @Test
    fun testEmitCompleteStreamStatusIterator() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val stream: AutoCloseableIterator<AirbyteMessage> = mock()
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.of(airbyteStream))

        StreamStatusUtils.emitCompleteStreamStatus(stream, streamStatusEmitter)

        Mockito.verify(statusEmitter, Mockito.times(1))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
        Assertions.assertEquals(
            AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE,
            airbyteStreamStatusHolderArgumentCaptor.value.toTraceMessage().streamStatus.status
        )
    }

    @Test
    fun testEmitCompleteStreamStatusIteratorEmptyAirbyteStream() {
        val stream: AutoCloseableIterator<AirbyteMessage> = mock()
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.empty())

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitCompleteStreamStatus(stream, streamStatusEmitter)
        }
        Mockito.verify(statusEmitter, Mockito.times(0))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
    }

    @Test
    fun testEmitCompleteStreamStatusIteratorEmptyStatusEmitter() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val stream: AutoCloseableIterator<AirbyteMessage> = mock()
        val streamStatusEmitter = Optional.empty<Consumer<AirbyteStreamStatusHolder>>()

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.of(airbyteStream))

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitCompleteStreamStatus(stream, streamStatusEmitter)
        }
    }

    @Test
    fun testEmitCompleteStreamStatusAirbyteStreamAware() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val stream = Mockito.mock(AirbyteStreamAware::class.java)
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.of(airbyteStream))

        StreamStatusUtils.emitCompleteStreamStatus(stream, streamStatusEmitter)

        Mockito.verify(statusEmitter, Mockito.times(1))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
        Assertions.assertEquals(
            AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE,
            airbyteStreamStatusHolderArgumentCaptor.value.toTraceMessage().streamStatus.status
        )
    }

    @Test
    fun testEmitCompleteStreamStatusAirbyteStreamAwareEmptyStream() {
        val stream = Mockito.mock(AirbyteStreamAware::class.java)
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.empty())

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitCompleteStreamStatus(stream, streamStatusEmitter)
        }
        Mockito.verify(statusEmitter, Mockito.times(0))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
    }

    @Test
    fun testEmitCompleteStreamStatusAirbyteStreamAwareEmptyStatusEmitter() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val stream = Mockito.mock(AirbyteStreamAware::class.java)
        val streamStatusEmitter = Optional.empty<Consumer<AirbyteStreamStatusHolder>>()

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.of(airbyteStream))

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitCompleteStreamStatus(stream, streamStatusEmitter)
        }
    }

    @Test
    fun testEmitCompleteStreamStatusAirbyteStream() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        StreamStatusUtils.emitCompleteStreamStatus(Optional.of(airbyteStream), streamStatusEmitter)

        Mockito.verify(statusEmitter, Mockito.times(1))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
        Assertions.assertEquals(
            AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE,
            airbyteStreamStatusHolderArgumentCaptor.value.toTraceMessage().streamStatus.status
        )
    }

    @Test
    fun testEmitCompleteStreamStatusEmptyAirbyteStream() {
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitCompleteStreamStatus(Optional.empty(), streamStatusEmitter)
        }
        Mockito.verify(statusEmitter, Mockito.times(0))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
    }

    @Test
    fun testEmitCompleteStreamStatusAirbyteStreamEmptyStatusEmitter() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val streamStatusEmitter = Optional.empty<Consumer<AirbyteStreamStatusHolder>>()

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitCompleteStreamStatus(
                Optional.of(airbyteStream),
                streamStatusEmitter
            )
        }
    }

    @Test
    fun testEmitIncompleteStreamStatusIterator() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val stream: AutoCloseableIterator<AirbyteMessage> = mock()
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.of(airbyteStream))

        StreamStatusUtils.emitIncompleteStreamStatus(stream, streamStatusEmitter)

        Mockito.verify(statusEmitter, Mockito.times(1))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
        Assertions.assertEquals(
            AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.INCOMPLETE,
            airbyteStreamStatusHolderArgumentCaptor.value.toTraceMessage().streamStatus.status
        )
    }

    @Test
    fun testEmitIncompleteStreamStatusIteratorEmptyAirbyteStream() {
        val stream: AutoCloseableIterator<AirbyteMessage> = mock()
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.empty())

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitIncompleteStreamStatus(stream, streamStatusEmitter)
        }
        Mockito.verify(statusEmitter, Mockito.times(0))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
    }

    @Test
    fun testEmitIncompleteStreamStatusIteratorEmptyStatusEmitter() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val stream: AutoCloseableIterator<AirbyteMessage> = mock()
        val streamStatusEmitter = Optional.empty<Consumer<AirbyteStreamStatusHolder>>()

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.of(airbyteStream))

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitIncompleteStreamStatus(stream, streamStatusEmitter)
        }
    }

    @Test
    fun testEmitIncompleteStreamStatusAirbyteStreamAware() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val stream = Mockito.mock(AirbyteStreamAware::class.java)
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.of(airbyteStream))

        StreamStatusUtils.emitIncompleteStreamStatus(stream, streamStatusEmitter)

        Mockito.verify(statusEmitter, Mockito.times(1))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
        Assertions.assertEquals(
            AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.INCOMPLETE,
            airbyteStreamStatusHolderArgumentCaptor.value.toTraceMessage().streamStatus.status
        )
    }

    @Test
    fun testEmitIncompleteStreamStatusAirbyteStreamAwareEmptyStream() {
        val stream = Mockito.mock(AirbyteStreamAware::class.java)
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.empty())

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitIncompleteStreamStatus(stream, streamStatusEmitter)
        }
        Mockito.verify(statusEmitter, Mockito.times(0))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
    }

    @Test
    fun testEmitIncompleteStreamStatusAirbyteStreamAwareEmptyStatusEmitter() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val stream = Mockito.mock(AirbyteStreamAware::class.java)
        val streamStatusEmitter = Optional.empty<Consumer<AirbyteStreamStatusHolder>>()

        Mockito.`when`(stream.airbyteStream).thenReturn(Optional.of(airbyteStream))

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitIncompleteStreamStatus(stream, streamStatusEmitter)
        }
    }

    @Test
    fun testEmitIncompleteStreamStatusAirbyteStream() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        StreamStatusUtils.emitIncompleteStreamStatus(
            Optional.of(airbyteStream),
            streamStatusEmitter
        )

        Mockito.verify(statusEmitter, Mockito.times(1))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
        Assertions.assertEquals(
            AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.INCOMPLETE,
            airbyteStreamStatusHolderArgumentCaptor.value.toTraceMessage().streamStatus.status
        )
    }

    @Test
    fun testEmitIncompleteStreamStatusEmptyAirbyteStream() {
        val statusEmitter: Consumer<AirbyteStreamStatusHolder> = mock()
        val streamStatusEmitter = Optional.of(statusEmitter)

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitIncompleteStreamStatus(Optional.empty(), streamStatusEmitter)
        }
        Mockito.verify(statusEmitter, Mockito.times(0))
            .accept(airbyteStreamStatusHolderArgumentCaptor!!.capture())
    }

    @Test
    fun testEmitIncompleteStreamStatusAirbyteStreamEmptyStatusEmitter() {
        val airbyteStream = AirbyteStreamNameNamespacePair(NAME, NAMESPACE)
        val streamStatusEmitter = Optional.empty<Consumer<AirbyteStreamStatusHolder>>()

        Assertions.assertDoesNotThrow {
            StreamStatusUtils.emitIncompleteStreamStatus(
                Optional.of(airbyteStream),
                streamStatusEmitter
            )
        }
    }

    companion object {
        private const val NAME = "name"
        private const val NAMESPACE = "namespace"
    }
}
