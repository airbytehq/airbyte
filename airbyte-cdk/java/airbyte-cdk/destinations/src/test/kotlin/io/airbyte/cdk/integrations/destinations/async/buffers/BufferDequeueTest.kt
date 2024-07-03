/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.buffers

import io.airbyte.cdk.integrations.destination.async.GlobalMemoryManager
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteRecordMessage
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.time.Instant
import java.time.temporal.ChronoUnit
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test

class BufferDequeueTest {
    private val RECORD_SIZE_20_BYTES = 20
    private val DEFAULT_NAMESPACE = "foo_namespace"
    private val STREAM_NAME = "stream1"
    private val STREAM_DESC: StreamDescriptor = StreamDescriptor().withName(STREAM_NAME)
    private val RECORD_MSG_20_BYTES: PartialAirbyteMessage =
        PartialAirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(
                PartialAirbyteRecordMessage().withStream(STREAM_NAME),
            )

    @Nested
    internal inner class Take {
        @Test
        internal fun testTakeShouldBestEffortRead() {
            val bufferManager = BufferManager(DEFAULT_NAMESPACE)
            val enqueue = bufferManager.bufferEnqueue
            val dequeue = bufferManager.bufferDequeue

            enqueue.addRecord(
                RECORD_MSG_20_BYTES,
                RECORD_SIZE_20_BYTES,
            )
            enqueue.addRecord(
                RECORD_MSG_20_BYTES,
                RECORD_SIZE_20_BYTES,
            )
            enqueue.addRecord(
                RECORD_MSG_20_BYTES,
                RECORD_SIZE_20_BYTES,
            )
            enqueue.addRecord(
                RECORD_MSG_20_BYTES,
                RECORD_SIZE_20_BYTES,
            )

            // total size of records is 80, so we expect 50 to get us 2 records (prefer to
            // under-pull records
            // than over-pull).
            try {
                dequeue.take(STREAM_DESC, 50).use { take ->
                    Assertions.assertEquals(2, take.data.size)
                    // verify it only took the records from the queue that it actually returned.
                    Assertions.assertEquals(
                        2,
                        dequeue.getQueueSizeInRecords(STREAM_DESC).orElseThrow(),
                    )
                }
            } catch (e: Exception) {
                throw RuntimeException(e)
            }
        }

        @Test
        internal fun testTakeShouldReturnAllIfPossible() {
            val bufferManager = BufferManager(DEFAULT_NAMESPACE)
            val enqueue = bufferManager.bufferEnqueue
            val dequeue = bufferManager.bufferDequeue

            enqueue.addRecord(
                RECORD_MSG_20_BYTES,
                RECORD_SIZE_20_BYTES,
            )
            enqueue.addRecord(
                RECORD_MSG_20_BYTES,
                RECORD_SIZE_20_BYTES,
            )
            enqueue.addRecord(
                RECORD_MSG_20_BYTES,
                RECORD_SIZE_20_BYTES,
            )

            try {
                dequeue.take(STREAM_DESC, 60).use { take ->
                    Assertions.assertEquals(3, take.data.size)
                }
            } catch (e: Exception) {
                throw RuntimeException(e)
            }
        }

        @Test
        internal fun testTakeFewerRecordsThanSizeLimitShouldNotError() {
            val bufferManager = BufferManager(DEFAULT_NAMESPACE)
            val enqueue = bufferManager.bufferEnqueue
            val dequeue = bufferManager.bufferDequeue

            enqueue.addRecord(
                RECORD_MSG_20_BYTES,
                RECORD_SIZE_20_BYTES,
            )
            enqueue.addRecord(
                RECORD_MSG_20_BYTES,
                RECORD_SIZE_20_BYTES,
            )

            try {
                dequeue.take(STREAM_DESC, Long.MAX_VALUE).use { take ->
                    Assertions.assertEquals(2, take.data.size)
                }
            } catch (e: Exception) {
                throw RuntimeException(e)
            }
        }
    }

    @Test
    internal fun testMetadataOperationsCorrect() {
        val bufferManager = BufferManager(DEFAULT_NAMESPACE)
        val enqueue = bufferManager.bufferEnqueue
        val dequeue = bufferManager.bufferDequeue

        enqueue.addRecord(RECORD_MSG_20_BYTES, RECORD_SIZE_20_BYTES)
        enqueue.addRecord(RECORD_MSG_20_BYTES, RECORD_SIZE_20_BYTES)

        val secondStream = StreamDescriptor().withName("stream_2")
        val recordFromSecondStream = Jsons.clone(RECORD_MSG_20_BYTES)
        recordFromSecondStream.record?.withStream(secondStream.name)
        enqueue.addRecord(
            recordFromSecondStream,
            RECORD_SIZE_20_BYTES,
        )

        Assertions.assertEquals(60, dequeue.totalGlobalQueueSizeBytes)

        Assertions.assertEquals(2, dequeue.getQueueSizeInRecords(STREAM_DESC).get())
        Assertions.assertEquals(1, dequeue.getQueueSizeInRecords(secondStream).get())

        Assertions.assertEquals(40, dequeue.getQueueSizeBytes(STREAM_DESC).get())
        Assertions.assertEquals(20, dequeue.getQueueSizeBytes(secondStream).get())

        // Buffer of 3 sec to deal with test execution variance.
        val lastThreeSec = Instant.now().minus(3, ChronoUnit.SECONDS)
        Assertions.assertTrue(lastThreeSec.isBefore(dequeue.getTimeOfLastRecord(STREAM_DESC).get()))
        Assertions.assertTrue(
            lastThreeSec.isBefore(dequeue.getTimeOfLastRecord(secondStream).get()),
        )
    }

    @Test
    internal fun testMetadataOperationsError() {
        val bufferManager = BufferManager(DEFAULT_NAMESPACE)
        val dequeue = bufferManager.bufferDequeue

        val ghostStream = StreamDescriptor().withName("ghost stream")

        Assertions.assertEquals(0, dequeue.totalGlobalQueueSizeBytes)

        Assertions.assertTrue(dequeue.getQueueSizeInRecords(ghostStream).isEmpty)

        Assertions.assertTrue(dequeue.getQueueSizeBytes(ghostStream).isEmpty)

        Assertions.assertTrue(dequeue.getTimeOfLastRecord(ghostStream).isEmpty)
    }

    @Test
    @Throws(Exception::class)
    internal fun cleansUpMemoryForEmptyQueues() {
        val bufferManager = BufferManager(DEFAULT_NAMESPACE)
        val enqueue = bufferManager.bufferEnqueue
        val dequeue = bufferManager.bufferDequeue
        val memoryManager = bufferManager.memoryManager

        // we initialize with a block for state
        Assertions.assertEquals(
            GlobalMemoryManager.BLOCK_SIZE_BYTES,
            memoryManager.getCurrentMemoryBytes(),
        )

        // allocate a block for new stream
        enqueue.addRecord(RECORD_MSG_20_BYTES, RECORD_SIZE_20_BYTES)
        Assertions.assertEquals(
            2 * GlobalMemoryManager.BLOCK_SIZE_BYTES,
            memoryManager.getCurrentMemoryBytes(),
        )

        enqueue.addRecord(RECORD_MSG_20_BYTES, RECORD_SIZE_20_BYTES)
        enqueue.addRecord(RECORD_MSG_20_BYTES, RECORD_SIZE_20_BYTES)
        enqueue.addRecord(RECORD_MSG_20_BYTES, RECORD_SIZE_20_BYTES)

        // no re-allocates as we haven't breached block size
        Assertions.assertEquals(
            2 * GlobalMemoryManager.BLOCK_SIZE_BYTES,
            memoryManager.getCurrentMemoryBytes(),
        )

        val totalBatchSize = RECORD_SIZE_20_BYTES * 4

        dequeue.take(STREAM_DESC, totalBatchSize.toLong()).use { batch ->
            // slop allocation gets cleaned up
            Assertions.assertEquals(
                GlobalMemoryManager.BLOCK_SIZE_BYTES + totalBatchSize,
                memoryManager.getCurrentMemoryBytes(),
            )
            batch.close()
            // back to initial state after flush clears the batch
            Assertions.assertEquals(
                GlobalMemoryManager.BLOCK_SIZE_BYTES,
                memoryManager.getCurrentMemoryBytes(),
            )
            Assertions.assertEquals(
                0,
                bufferManager.buffers[STREAM_DESC]!!.maxMemoryUsage,
            )
        }
    }
}
