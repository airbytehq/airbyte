/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.record_buffer

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito
import org.mockito.kotlin.any

class SerializedBufferingStrategyTest {
    private val catalog: ConfiguredAirbyteCatalog =
        Mockito.mock(ConfiguredAirbyteCatalog::class.java)
    private val perStreamFlushHook: FlushBufferFunction =
        Mockito.mock(FlushBufferFunction::class.java)

    private val recordWriter1: SerializableBuffer = Mockito.mock(SerializableBuffer::class.java)
    private val recordWriter2: SerializableBuffer = Mockito.mock(SerializableBuffer::class.java)
    private val recordWriter3: SerializableBuffer = Mockito.mock(SerializableBuffer::class.java)
    private val recordWriter4: SerializableBuffer = Mockito.mock(SerializableBuffer::class.java)

    @BeforeEach
    @Throws(Exception::class)
    fun setup() {
        setupMock(recordWriter1)
        setupMock(recordWriter2)
        setupMock(recordWriter3)
        setupMock(recordWriter4)
    }

    @Throws(Exception::class)
    private fun setupMock(mockObject: SerializableBuffer) {
        Mockito.`when`(mockObject.accept(any())).thenReturn(10L)
        Mockito.`when`(mockObject.byteCount).thenReturn(10L)
        Mockito.`when`(mockObject.maxTotalBufferSizeInBytes).thenReturn(MAX_TOTAL_BUFFER_SIZE_BYTES)
        Mockito.`when`(mockObject.maxPerStreamBufferSizeInBytes)
            .thenReturn(MAX_PER_STREAM_BUFFER_SIZE_BYTES)
        Mockito.`when`(mockObject.maxConcurrentStreamsInBuffer).thenReturn(4)
    }

    @Test
    @Throws(Exception::class)
    fun testPerStreamThresholdFlush() {
        val buffering =
            SerializedBufferingStrategy(onCreateBufferFunction(), catalog, perStreamFlushHook)
        val stream1 = AirbyteStreamNameNamespacePair(STREAM_1, "namespace")
        val stream2 = AirbyteStreamNameNamespacePair(STREAM_2, null)
        // To test per stream threshold, we are sending multiple test messages on a single stream
        val message1 = generateMessage(stream1)
        val message2 = generateMessage(stream2)
        val message3 = generateMessage(stream2)
        val message4 = generateMessage(stream2)
        val message5 = generateMessage(stream2)

        Mockito.`when`(recordWriter1.byteCount).thenReturn(10L) // one record in recordWriter1
        Assertions.assertFalse(buffering.addRecord(stream1, message1).isPresent)
        Mockito.`when`(recordWriter2.byteCount).thenReturn(10L) // one record in recordWriter2
        Assertions.assertFalse(buffering.addRecord(stream2, message2).isPresent)

        // Total and per stream Buffers still have room
        Mockito.verify(perStreamFlushHook, Mockito.times(0)).accept(stream1, recordWriter1)
        Mockito.verify(perStreamFlushHook, Mockito.times(0)).accept(stream2, recordWriter2)

        Mockito.`when`(recordWriter2.byteCount).thenReturn(20L) // second record in recordWriter2
        Assertions.assertFalse(buffering.addRecord(stream2, message3).isPresent)
        Mockito.`when`(recordWriter2.byteCount).thenReturn(30L) // third record in recordWriter2

        // Buffer reaches limit so a buffer flush occurs returning a buffer flush type of single
        // stream
        val flushType = buffering.addRecord(stream2, message4)
        Assertions.assertTrue(flushType.isPresent)
        Assertions.assertEquals(flushType.get(), BufferFlushType.FLUSH_SINGLE_STREAM)

        // The buffer limit is now reached for stream2, flushing that single stream only
        Mockito.verify(perStreamFlushHook, Mockito.times(0)).accept(stream1, recordWriter1)
        Mockito.verify(perStreamFlushHook, Mockito.times(1)).accept(stream2, recordWriter2)

        Mockito.`when`(recordWriter2.byteCount)
            .thenReturn(10L) // back to one record in recordWriter2
        Assertions.assertFalse(buffering.addRecord(stream2, message5).isPresent)

        // force flush to terminate test
        buffering.flushAllBuffers()
        Mockito.verify(perStreamFlushHook, Mockito.times(1)).accept(stream1, recordWriter1)
        Mockito.verify(perStreamFlushHook, Mockito.times(2)).accept(stream2, recordWriter2)
    }

    @Test
    @Throws(Exception::class)
    fun testTotalStreamThresholdFlush() {
        val buffering =
            SerializedBufferingStrategy(onCreateBufferFunction(), catalog, perStreamFlushHook)
        val stream1 = AirbyteStreamNameNamespacePair(STREAM_1, "namespace")
        val stream2 = AirbyteStreamNameNamespacePair(STREAM_2, "namespace")
        val stream3 = AirbyteStreamNameNamespacePair(STREAM_3, "namespace")
        // To test total stream threshold, we are sending test messages to multiple streams without
        // reaching
        // per stream limits
        val message1 = generateMessage(stream1)
        val message2 = generateMessage(stream2)
        val message3 = generateMessage(stream3)
        val message4 = generateMessage(stream1)
        val message5 = generateMessage(stream2)
        val message6 = generateMessage(stream3)

        Assertions.assertFalse(buffering.addRecord(stream1, message1).isPresent)
        Assertions.assertFalse(buffering.addRecord(stream2, message2).isPresent)
        // Total and per stream Buffers still have room
        Mockito.verify(perStreamFlushHook, Mockito.times(0)).accept(stream1, recordWriter1)
        Mockito.verify(perStreamFlushHook, Mockito.times(0)).accept(stream2, recordWriter2)
        Mockito.verify(perStreamFlushHook, Mockito.times(0)).accept(stream3, recordWriter3)

        Assertions.assertFalse(buffering.addRecord(stream3, message3).isPresent)
        Mockito.`when`(recordWriter1.byteCount).thenReturn(20L) // second record in recordWriter1
        Assertions.assertFalse(buffering.addRecord(stream1, message4).isPresent)
        Mockito.`when`(recordWriter2.byteCount).thenReturn(20L) // second record in recordWriter2

        // In response to checkpointing, will need to know what type of buffer flush occurred to
        // mark
        // AirbyteStateMessage as committed depending on DestDefaultStateLifecycleManager
        val flushType = buffering.addRecord(stream2, message5)
        Assertions.assertTrue(flushType.isPresent)
        Assertions.assertEquals(flushType.get(), BufferFlushType.FLUSH_ALL)

        // Buffer limit reached for total streams, flushing all streams
        Mockito.verify(perStreamFlushHook, Mockito.times(1)).accept(stream1, recordWriter1)
        Mockito.verify(perStreamFlushHook, Mockito.times(1)).accept(stream2, recordWriter2)
        Mockito.verify(perStreamFlushHook, Mockito.times(1)).accept(stream3, recordWriter3)

        Assertions.assertFalse(buffering.addRecord(stream3, message6).isPresent)
        // force flush to terminate test
        buffering.flushAllBuffers()
        Mockito.verify(perStreamFlushHook, Mockito.times(1)).accept(stream1, recordWriter1)
        Mockito.verify(perStreamFlushHook, Mockito.times(1)).accept(stream2, recordWriter2)
        Mockito.verify(perStreamFlushHook, Mockito.times(2)).accept(stream3, recordWriter3)
    }

    @Test
    @Throws(Exception::class)
    fun testConcurrentStreamThresholdFlush() {
        val buffering =
            SerializedBufferingStrategy(onCreateBufferFunction(), catalog, perStreamFlushHook)
        val stream1 = AirbyteStreamNameNamespacePair(STREAM_1, "namespace1")
        val stream2 = AirbyteStreamNameNamespacePair(STREAM_2, "namespace2")
        val stream3 = AirbyteStreamNameNamespacePair(STREAM_3, null)
        val stream4 = AirbyteStreamNameNamespacePair(STREAM_4, null)
        // To test concurrent stream threshold, we are sending test messages to multiple streams
        val message1 = generateMessage(stream1)
        val message2 = generateMessage(stream2)
        val message3 = generateMessage(stream3)
        val message4 = generateMessage(stream4)
        val message5 = generateMessage(stream1)

        Assertions.assertFalse(buffering.addRecord(stream1, message1).isPresent)
        Assertions.assertFalse(buffering.addRecord(stream2, message2).isPresent)
        Assertions.assertFalse(buffering.addRecord(stream3, message3).isPresent)
        // Total and per stream Buffers still have room
        Mockito.verify(perStreamFlushHook, Mockito.times(0)).accept(stream1, recordWriter1)
        Mockito.verify(perStreamFlushHook, Mockito.times(0)).accept(stream2, recordWriter2)
        Mockito.verify(perStreamFlushHook, Mockito.times(0)).accept(stream3, recordWriter3)

        // Since the concurrent stream threshold has been exceeded, all buffer streams are flush
        val flushType = buffering.addRecord(stream4, message4)
        Assertions.assertTrue(flushType.isPresent)
        Assertions.assertEquals(flushType.get(), BufferFlushType.FLUSH_ALL)

        // Buffer limit reached for concurrent streams, flushing all streams
        Mockito.verify(perStreamFlushHook, Mockito.times(1)).accept(stream1, recordWriter1)
        Mockito.verify(perStreamFlushHook, Mockito.times(1)).accept(stream2, recordWriter2)
        Mockito.verify(perStreamFlushHook, Mockito.times(1)).accept(stream3, recordWriter3)
        Mockito.verify(perStreamFlushHook, Mockito.times(1)).accept(stream4, recordWriter4)

        Assertions.assertFalse(buffering.addRecord(stream1, message5).isPresent)
        // force flush to terminate test
        buffering.flushAllBuffers()
        Mockito.verify(perStreamFlushHook, Mockito.times(2)).accept(stream1, recordWriter1)
        Mockito.verify(perStreamFlushHook, Mockito.times(1)).accept(stream2, recordWriter2)
        Mockito.verify(perStreamFlushHook, Mockito.times(1)).accept(stream3, recordWriter3)
        Mockito.verify(perStreamFlushHook, Mockito.times(1)).accept(stream4, recordWriter4)
    }

    @Test
    fun testCreateBufferFailure() {
        val buffering =
            SerializedBufferingStrategy(onCreateBufferFunction(), catalog, perStreamFlushHook)
        val stream = AirbyteStreamNameNamespacePair("unknown_stream", "namespace1")
        Assertions.assertThrows(RuntimeException::class.java) {
            buffering.addRecord(stream, generateMessage(stream))
        }
    }

    private fun onCreateBufferFunction(): BufferCreateFunction {
        return BufferCreateFunction {
            stream: AirbyteStreamNameNamespacePair,
            catalog: ConfiguredAirbyteCatalog ->
            when (stream.name) {
                STREAM_1 -> recordWriter1
                STREAM_2 -> recordWriter2
                STREAM_3 -> recordWriter3
                STREAM_4 -> recordWriter4
                else -> null
            }
        }
    }

    companion object {
        private val MESSAGE_DATA: JsonNode = Jsons.deserialize("{ \"field1\": 10000 }")
        private const val STREAM_1 = "stream1"
        private const val STREAM_2 = "stream2"
        private const val STREAM_3 = "stream3"
        private const val STREAM_4 = "stream4"

        // we set the limit to hold at most 4 messages of 10b total
        private const val MAX_TOTAL_BUFFER_SIZE_BYTES = 42L

        // we set the limit to hold at most 2 messages of 10b per stream
        private const val MAX_PER_STREAM_BUFFER_SIZE_BYTES = 21L

        private fun generateMessage(stream: AirbyteStreamNameNamespacePair): AirbyteMessage {
            return AirbyteMessage()
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(stream.name)
                        .withNamespace(stream.namespace)
                        .withData(MESSAGE_DATA)
                )
        }
    }
}
