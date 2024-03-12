/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.buffers

import io.airbyte.cdk.integrations.destination.async.GlobalMemoryManager
import io.airbyte.cdk.integrations.destination.async.GlobalMemoryManager.Companion.BLOCK_SIZE_BYTES
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteRecordMessage
import io.airbyte.cdk.integrations.destination.async.state.GlobalAsyncStateManager
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.mockk.every
import io.mockk.mockk
import java.time.Instant
import java.time.temporal.ChronoUnit
import java.util.Optional
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test

class BufferDequeueTest {
    companion object {
        private const val RECORD_SIZE_20_BYTES = 20
        private const val DEFAULT_NAMESPACE = "foo_namespace"
        private const val STREAM_NAME = "stream1"
        private const val MEMORY_LIMIT = BLOCK_SIZE_BYTES * 4
        private val STREAM_DESC: StreamDescriptor = StreamDescriptor().withName(STREAM_NAME)
        private val RECORD_MSG_20_BYTES: PartialAirbyteMessage =
            PartialAirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    PartialAirbyteRecordMessage().withStream(STREAM_NAME),
                )
    }

    private lateinit var asyncBuffers: AsyncBuffers

    @BeforeEach
    internal fun setup() {
        asyncBuffers = AsyncBuffers()
    }

    @Nested
    internal inner class Take {
        @Test
        internal fun testTakeShouldBestEffortRead() {
            val asyncBuffers = AsyncBuffers()
            val globalMemoryManager: GlobalMemoryManager = mockk()
            val globalAsyncStateManager: GlobalAsyncStateManager = mockk()

            every { globalMemoryManager.free(any()) } returns Unit
            every { globalMemoryManager.requestMemory() } returns BLOCK_SIZE_BYTES
            every { globalAsyncStateManager.getStateIdAndIncrementCounter(any()) } returns 1L

            val bufferDequeue =
                BufferDequeue(
                    globalMemoryManager = globalMemoryManager,
                    globalAsyncStateManager = globalAsyncStateManager,
                    asyncBuffers = asyncBuffers,
                )
            val bufferEnqueue =
                BufferEnqueue(
                    globalMemoryManager = globalMemoryManager,
                    globalAsyncStateManager = globalAsyncStateManager,
                    asyncBuffers = asyncBuffers,
                )

            bufferEnqueue.addRecord(
                RECORD_MSG_20_BYTES,
                RECORD_SIZE_20_BYTES,
                Optional.of(DEFAULT_NAMESPACE)
            )
            bufferEnqueue.addRecord(
                RECORD_MSG_20_BYTES,
                RECORD_SIZE_20_BYTES,
                Optional.of(DEFAULT_NAMESPACE)
            )
            bufferEnqueue.addRecord(
                RECORD_MSG_20_BYTES,
                RECORD_SIZE_20_BYTES,
                Optional.of(DEFAULT_NAMESPACE)
            )
            bufferEnqueue.addRecord(
                RECORD_MSG_20_BYTES,
                RECORD_SIZE_20_BYTES,
                Optional.of(DEFAULT_NAMESPACE)
            )

            // total size of records is 80, so we expect 50 to get us 2 records (prefer to
            // under-pull records
            // than over-pull).
            try {
                bufferDequeue.take(STREAM_DESC, 50).use { take ->
                    assertEquals(2, take.getData().size)
                    // verify it only took the records from the queue that it actually returned.
                    assertEquals(
                        2,
                        bufferDequeue.getQueueSizeInRecords(STREAM_DESC).orElseThrow(),
                    )
                }
            } catch (e: Exception) {
                throw RuntimeException(e)
            }
        }

        @Test
        internal fun testTakeShouldReturnAllIfPossible() {
            val globalMemoryManager: GlobalMemoryManager = mockk()
            val globalAsyncStateManager: GlobalAsyncStateManager = mockk()

            every { globalMemoryManager.free(any()) } returns Unit
            every { globalMemoryManager.requestMemory() } returns BLOCK_SIZE_BYTES
            every { globalAsyncStateManager.getStateIdAndIncrementCounter(any()) } returns 1L

            val bufferDequeue =
                BufferDequeue(
                    globalMemoryManager = globalMemoryManager,
                    globalAsyncStateManager = globalAsyncStateManager,
                    asyncBuffers = asyncBuffers,
                )
            val bufferEnqueue =
                BufferEnqueue(
                    globalMemoryManager = globalMemoryManager,
                    globalAsyncStateManager = globalAsyncStateManager,
                    asyncBuffers = asyncBuffers,
                )

            bufferEnqueue.addRecord(
                RECORD_MSG_20_BYTES,
                RECORD_SIZE_20_BYTES,
                Optional.of(DEFAULT_NAMESPACE)
            )
            bufferEnqueue.addRecord(
                RECORD_MSG_20_BYTES,
                RECORD_SIZE_20_BYTES,
                Optional.of(DEFAULT_NAMESPACE)
            )
            bufferEnqueue.addRecord(
                RECORD_MSG_20_BYTES,
                RECORD_SIZE_20_BYTES,
                Optional.of(DEFAULT_NAMESPACE)
            )

            try {
                bufferDequeue.take(STREAM_DESC, 60).use { take ->
                    assertEquals(3, take.getData().size)
                }
            } catch (e: Exception) {
                throw RuntimeException(e)
            }
        }

        @Test
        internal fun testTakeFewerRecordsThanSizeLimitShouldNotError() {
            val globalMemoryManager: GlobalMemoryManager = mockk()
            val globalAsyncStateManager: GlobalAsyncStateManager = mockk()

            every { globalMemoryManager.free(any()) } returns Unit
            every { globalMemoryManager.requestMemory() } returns BLOCK_SIZE_BYTES
            every { globalAsyncStateManager.getStateIdAndIncrementCounter(any()) } returns 1L

            val bufferDequeue =
                BufferDequeue(
                    globalMemoryManager = globalMemoryManager,
                    globalAsyncStateManager = globalAsyncStateManager,
                    asyncBuffers = asyncBuffers,
                )
            val bufferEnqueue =
                BufferEnqueue(
                    globalMemoryManager = globalMemoryManager,
                    globalAsyncStateManager = globalAsyncStateManager,
                    asyncBuffers = asyncBuffers,
                )

            bufferEnqueue.addRecord(
                RECORD_MSG_20_BYTES,
                RECORD_SIZE_20_BYTES,
                Optional.of(DEFAULT_NAMESPACE)
            )
            bufferEnqueue.addRecord(
                RECORD_MSG_20_BYTES,
                RECORD_SIZE_20_BYTES,
                Optional.of(DEFAULT_NAMESPACE)
            )

            try {
                bufferDequeue.take(STREAM_DESC, Long.MAX_VALUE).use { take ->
                    assertEquals(2, take.getData().size)
                }
            } catch (e: Exception) {
                throw RuntimeException(e)
            }
        }
    }

    @Test
    internal fun testMetadataOperationsCorrect() {
        val globalMemoryManager: GlobalMemoryManager = mockk()
        val globalAsyncStateManager: GlobalAsyncStateManager = mockk()

        every { globalMemoryManager.free(any()) } returns Unit
        every { globalMemoryManager.requestMemory() } returns BLOCK_SIZE_BYTES
        every { globalAsyncStateManager.getStateIdAndIncrementCounter(any()) } returns 1L

        val bufferDequeue =
            BufferDequeue(
                globalMemoryManager = globalMemoryManager,
                globalAsyncStateManager = globalAsyncStateManager,
                asyncBuffers = asyncBuffers,
            )
        val bufferEnqueue =
            BufferEnqueue(
                globalMemoryManager = globalMemoryManager,
                globalAsyncStateManager = globalAsyncStateManager,
                asyncBuffers = asyncBuffers,
            )

        bufferEnqueue.addRecord(
            RECORD_MSG_20_BYTES,
            RECORD_SIZE_20_BYTES,
            Optional.of(DEFAULT_NAMESPACE)
        )
        bufferEnqueue.addRecord(
            RECORD_MSG_20_BYTES,
            RECORD_SIZE_20_BYTES,
            Optional.of(DEFAULT_NAMESPACE)
        )

        val secondStream = StreamDescriptor().withName("stream_2")
        val recordFromSecondStream = Jsons.clone(RECORD_MSG_20_BYTES)
        recordFromSecondStream.record?.withStream(secondStream.name)
        bufferEnqueue.addRecord(
            recordFromSecondStream,
            RECORD_SIZE_20_BYTES,
            Optional.of(DEFAULT_NAMESPACE)
        )

        assertEquals(60, bufferDequeue.getTotalGlobalQueueSizeBytes())
        assertEquals(2, bufferDequeue.getQueueSizeInRecords(STREAM_DESC).get())
        assertEquals(1, bufferDequeue.getQueueSizeInRecords(secondStream).get())
        assertEquals(40, bufferDequeue.getQueueSizeBytes(STREAM_DESC).get())
        assertEquals(20, bufferDequeue.getQueueSizeBytes(secondStream).get())

        // Buffer of 3 sec to deal with test execution variance.
        val lastThreeSec = Instant.now().minus(3, ChronoUnit.SECONDS)
        assertTrue(lastThreeSec.isBefore(bufferDequeue.getTimeOfLastRecord(STREAM_DESC).get()))
        assertTrue(lastThreeSec.isBefore(bufferDequeue.getTimeOfLastRecord(secondStream).get()))
    }

    @Test
    internal fun testMetadataOperationsError() {
        val bufferMemory: BufferMemory = mockk()
        every { bufferMemory.getMemoryLimit() } returns MEMORY_LIMIT
        val globalMemoryManager = GlobalMemoryManager(bufferMemory)
        val globalAsyncStateManager = GlobalAsyncStateManager(globalMemoryManager)
        val bufferDequeue =
            BufferDequeue(
                globalMemoryManager = globalMemoryManager,
                globalAsyncStateManager = globalAsyncStateManager,
                asyncBuffers = asyncBuffers,
            )

        val ghostStream = StreamDescriptor().withName("ghost stream")
        assertEquals(0, bufferDequeue.getTotalGlobalQueueSizeBytes())
        assertTrue(bufferDequeue.getQueueSizeInRecords(ghostStream).isEmpty)
        assertTrue(bufferDequeue.getQueueSizeBytes(ghostStream).isEmpty)
        assertTrue(bufferDequeue.getTimeOfLastRecord(ghostStream).isEmpty)
    }

    @Test
    @Throws(Exception::class)
    internal fun cleansUpMemoryForEmptyQueues() {
        val bufferMemory: BufferMemory = mockk()
        every { bufferMemory.getMemoryLimit() } returns MEMORY_LIMIT
        val globalMemoryManager = GlobalMemoryManager(bufferMemory)
        val globalAsyncStateManager = GlobalAsyncStateManager(globalMemoryManager)
        val bufferDequeue =
            BufferDequeue(
                globalMemoryManager = globalMemoryManager,
                globalAsyncStateManager = globalAsyncStateManager,
                asyncBuffers = asyncBuffers,
            )
        val bufferEnqueue =
            BufferEnqueue(
                globalMemoryManager = globalMemoryManager,
                globalAsyncStateManager = globalAsyncStateManager,
                asyncBuffers = asyncBuffers,
            )

        // we initialize with a block for state
        assertEquals(
            GlobalMemoryManager.BLOCK_SIZE_BYTES,
            globalMemoryManager.currentMemoryBytes.get()
        )

        // allocate a block for new stream
        bufferEnqueue.addRecord(
            RECORD_MSG_20_BYTES,
            RECORD_SIZE_20_BYTES,
            Optional.of(DEFAULT_NAMESPACE)
        )
        assertEquals(2 * BLOCK_SIZE_BYTES, globalMemoryManager.currentMemoryBytes.get())

        bufferEnqueue.addRecord(
            RECORD_MSG_20_BYTES,
            RECORD_SIZE_20_BYTES,
            Optional.of(DEFAULT_NAMESPACE)
        )
        bufferEnqueue.addRecord(
            RECORD_MSG_20_BYTES,
            RECORD_SIZE_20_BYTES,
            Optional.of(DEFAULT_NAMESPACE)
        )
        bufferEnqueue.addRecord(
            RECORD_MSG_20_BYTES,
            RECORD_SIZE_20_BYTES,
            Optional.of(DEFAULT_NAMESPACE)
        )

        // no re-allocates as we haven't breached block size
        assertEquals(2 * BLOCK_SIZE_BYTES, globalMemoryManager.currentMemoryBytes.get())

        val totalBatchSize = RECORD_SIZE_20_BYTES * 4

        bufferDequeue.take(STREAM_DESC, totalBatchSize.toLong()).use { batch ->
            // slop allocation gets cleaned up
            assertEquals(
                BLOCK_SIZE_BYTES + totalBatchSize,
                globalMemoryManager.currentMemoryBytes.get(),
            )
            batch.close()
            // back to initial state after flush clears the batch
            assertEquals(
                BLOCK_SIZE_BYTES,
                globalMemoryManager.currentMemoryBytes.get(),
            )
            assertEquals(
                0,
                asyncBuffers.buffers[STREAM_DESC]!!.getMaxMemoryUsage(),
            )
        }
    }
}
