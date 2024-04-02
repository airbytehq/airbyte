/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destnation.async.buffers

import io.airbyte.cdk.integrations.destination.async.GlobalMemoryManager
import io.airbyte.cdk.integrations.destination.async.buffers.BufferEnqueue
import io.airbyte.cdk.integrations.destination.async.buffers.StreamAwareQueue
import io.airbyte.cdk.integrations.destination.async.partial_messages.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.partial_messages.PartialAirbyteRecordMessage
import io.airbyte.cdk.integrations.destination.async.state.GlobalAsyncStateManager
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito
import java.util.concurrent.ConcurrentHashMap

class BufferEnqueueTest {
    private val RECORD_SIZE_20_BYTES = 20
    private val DEFAULT_NAMESPACE = "foo_namespace"

    @Test
    internal fun testAddRecordShouldAdd() {
        val twoMB = 2 * 1024 * 1024
        val streamToBuffer = ConcurrentHashMap<StreamDescriptor, StreamAwareQueue>()
        val enqueue =
            BufferEnqueue(
                GlobalMemoryManager(twoMB.toLong()),
                streamToBuffer,
                Mockito.mock(
                    GlobalAsyncStateManager::class.java,
                ),
            )

        val streamName = "stream"
        val stream = StreamDescriptor().withName(streamName)
        val record =
            PartialAirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    PartialAirbyteRecordMessage()
                        .withStream(streamName),
                )

        enqueue.addRecord(record, RECORD_SIZE_20_BYTES, DEFAULT_NAMESPACE)
        Assertions.assertEquals(1, streamToBuffer[stream]!!.size())
        Assertions.assertEquals(20L, streamToBuffer[stream]!!.currentMemoryUsage)
    }

    @Test
    internal fun testAddRecordShouldExpand() {
        val oneKb = 1024
        val streamToBuffer = ConcurrentHashMap<StreamDescriptor, StreamAwareQueue>()
        val enqueue =
            BufferEnqueue(
                GlobalMemoryManager(oneKb.toLong()),
                streamToBuffer,
                Mockito.mock(
                    GlobalAsyncStateManager::class.java,
                ),
            )

        val streamName = "stream"
        val stream = StreamDescriptor().withName(streamName)
        val record =
            PartialAirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    PartialAirbyteRecordMessage()
                        .withStream(streamName),
                )

        enqueue.addRecord(record, RECORD_SIZE_20_BYTES, DEFAULT_NAMESPACE)
        enqueue.addRecord(record, RECORD_SIZE_20_BYTES, DEFAULT_NAMESPACE)
        Assertions.assertEquals(2, streamToBuffer[stream]!!.size())
        Assertions.assertEquals(40, streamToBuffer[stream]!!.currentMemoryUsage)
    }
}
