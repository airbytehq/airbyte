/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.record_buffer

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.RecordWriter
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import java.util.List
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito
import org.mockito.kotlin.mock

class InMemoryRecordBufferingStrategyTest {
    private val recordWriter: RecordWriter<AirbyteRecordMessage> = mock()

    @Test
    @Throws(Exception::class)
    fun testBuffering() {
        val buffering =
            InMemoryRecordBufferingStrategy(recordWriter, MAX_QUEUE_SIZE_IN_BYTES.toLong())
        val stream1 = AirbyteStreamNameNamespacePair("stream1", "namespace")
        val stream2 = AirbyteStreamNameNamespacePair("stream2", null)
        val message1 = generateMessage(stream1)
        val message2 = generateMessage(stream2)
        val message3 = generateMessage(stream2)
        val message4 = generateMessage(stream2)

        Assertions.assertFalse(buffering.addRecord(stream1, message1).isPresent)
        Assertions.assertFalse(buffering.addRecord(stream2, message2).isPresent)
        // Buffer still has room
        val flushType = buffering.addRecord(stream2, message3)
        // Keeps track of this #addRecord since we're expecting a buffer flush & that the flushType
        // value will indicate that all buffers were flushed
        Assertions.assertTrue(flushType.isPresent)
        Assertions.assertEquals(flushType.get(), BufferFlushType.FLUSH_ALL)
        // Buffer limit reach, flushing all messages so far before adding the new incoming one
        Mockito.verify(recordWriter, Mockito.times(1)).accept(stream1, List.of(message1.record))
        Mockito.verify(recordWriter, Mockito.times(1)).accept(stream2, List.of(message2.record))

        buffering.addRecord(stream2, message4)

        // force flush to terminate test
        buffering.flushAllBuffers()
        Mockito.verify(recordWriter, Mockito.times(1))
            .accept(stream2, List.of(message3.record, message4.record))
    }

    companion object {
        private val MESSAGE_DATA: JsonNode = Jsons.deserialize("{ \"field1\": 10000 }")

        // MESSAGE_DATA should be 64 bytes long, size the buffer such as it can contain at least 2
        // message
        // instances
        private const val MAX_QUEUE_SIZE_IN_BYTES = 130

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
