/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.buffers

import io.airbyte.cdk.integrations.destination.async.GlobalMemoryManager
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteRecordMessage
import io.airbyte.cdk.integrations.destination.async.state.GlobalAsyncStateManager
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.mockk.every
import io.mockk.mockk
import java.util.Optional
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class BufferEnqueueTest {
    companion object {
        private const val RECORD_SIZE_20_BYTES = 20
        private const val DEFAULT_NAMESPACE = "foo_namespace"
    }

    @Test
    internal fun testAddRecordShouldAdd() {
        val twoMB = 2 * 1024 * 1024
        val streamToBuffer = AsyncBuffers()
        val bufferMemory: BufferMemory = mockk()
        val globalAsyncStateManager: GlobalAsyncStateManager = mockk()

        every { bufferMemory.getMemoryLimit() } returns twoMB.toLong()
        every { globalAsyncStateManager.getStateIdAndIncrementCounter(any()) } returns 1L

        val enqueue =
            BufferEnqueue(
                globalMemoryManager = GlobalMemoryManager(bufferMemory),
                asyncBuffers = streamToBuffer,
                globalAsyncStateManager = globalAsyncStateManager,
            )

        val streamName = "stream"
        val stream = StreamDescriptor().withName(streamName)
        val record =
            PartialAirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    PartialAirbyteRecordMessage().withStream(streamName),
                )

        enqueue.addRecord(record, RECORD_SIZE_20_BYTES, Optional.of(DEFAULT_NAMESPACE))
        Assertions.assertEquals(1, streamToBuffer.buffers[stream]!!.size())
        Assertions.assertEquals(20L, streamToBuffer.buffers[stream]!!.getCurrentMemoryUsage())
    }

    @Test
    internal fun testAddRecordShouldExpand() {
        val oneKb = 1024
        val streamToBuffer = AsyncBuffers()
        val bufferMemory: BufferMemory = mockk()
        val globalAsyncStateManager: GlobalAsyncStateManager = mockk()

        every { bufferMemory.getMemoryLimit() } returns oneKb.toLong()
        every { globalAsyncStateManager.getStateIdAndIncrementCounter(any()) } returns 1L

        val enqueue =
            BufferEnqueue(
                globalMemoryManager = GlobalMemoryManager(bufferMemory),
                asyncBuffers = streamToBuffer,
                globalAsyncStateManager = globalAsyncStateManager,
            )

        val streamName = "stream"
        val stream = StreamDescriptor().withName(streamName)
        val record =
            PartialAirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    PartialAirbyteRecordMessage().withStream(streamName),
                )

        enqueue.addRecord(record, RECORD_SIZE_20_BYTES, Optional.of(DEFAULT_NAMESPACE))
        enqueue.addRecord(record, RECORD_SIZE_20_BYTES, Optional.of(DEFAULT_NAMESPACE))
        Assertions.assertEquals(2, streamToBuffer.buffers[stream]!!.size())
        Assertions.assertEquals(40, streamToBuffer.buffers[stream]!!.getCurrentMemoryUsage())
    }
}
