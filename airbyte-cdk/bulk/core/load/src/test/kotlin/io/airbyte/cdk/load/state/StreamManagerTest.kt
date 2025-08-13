/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import io.airbyte.cdk.load.command.MockDestinationCatalogFactory.Companion.stream1
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory.Companion.stream2
import io.airbyte.cdk.load.message.BatchState
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow
import org.junit.jupiter.api.assertThrows

class StreamManagerTest {

    private fun checkpoint(id: String) = CheckpointId(id)

    @Test
    fun `markProcessingSucceeded requires end-of-stream`() = runTest {
        val manager = StreamManager(stream1)
        val channel = Channel<Boolean>(Channel.UNLIMITED)
        val ck = checkpoint("c1")

        // Start waiting
        launch { channel.send(manager.awaitStreamResult() is StreamProcessingSucceeded) }

        repeat(5) { manager.incrementReadCount(ck) }

        // Cannot mark success before end-of-stream
        assertThrows<IllegalStateException> { manager.markProcessingSucceeded() }

        // Mark end-of-stream and then success
        manager.markEndOfStream(true)
        manager.markProcessingSucceeded()

        Assertions.assertTrue(channel.receive())
        Assertions.assertEquals(StreamProcessingSucceeded, manager.awaitStreamResult())
    }

    @Test
    fun `markProcessingFailed can happen before end-of-stream`() = runTest {
        val manager = StreamManager(stream1)
        val channel = Channel<Boolean>(Channel.UNLIMITED)

        launch { channel.send(manager.awaitStreamResult() is StreamProcessingSucceeded) }

        manager.markProcessingFailed(Exception("test"))
        Assertions.assertFalse(channel.receive())
        Assertions.assertTrue(manager.awaitStreamResult() is StreamProcessingFailed)
    }

    @Test
    fun `cannot increment after end-of-stream`() {
        val manager = StreamManager(stream1)
        val ck = checkpoint("c1")

        manager.incrementReadCount(ck)
        manager.markEndOfStream(true)

        assertThrows<IllegalStateException> { manager.incrementReadCount(ck) }
        assertThrows<IllegalStateException> { manager.markEndOfStream(true) }

        // Now success is allowed
        assertDoesNotThrow { manager.markProcessingSucceeded() }
    }

    @Test
    fun `persisted counts without rejected records`() {
        val manager = StreamManager(stream1)
        val ck = checkpoint("c1")

        repeat(10) { manager.incrementReadCount(ck) }

        Assertions.assertFalse(manager.areRecordsPersistedForCheckpoint(ck))
        manager.incrementCheckpointCounts(
            BatchState.PERSISTED,
            mapOf(ck to CheckpointValue(records = 5, serializedBytes = 5)),
        )
        Assertions.assertFalse(manager.areRecordsPersistedForCheckpoint(ck))
        manager.incrementCheckpointCounts(
            BatchState.PERSISTED,
            mapOf(ck to CheckpointValue(records = 5, serializedBytes = 5)),
        )
        Assertions.assertTrue(manager.areRecordsPersistedForCheckpoint(ck))
    }

    @Test
    fun `persisted counts with rejected records`() {
        val manager = StreamManager(stream1)
        val ck = checkpoint("c1")

        repeat(10) { manager.incrementReadCount(ck) }

        Assertions.assertFalse(manager.areRecordsPersistedForCheckpoint(ck))
        manager.incrementCheckpointCounts(
            BatchState.PERSISTED,
            mapOf(
                ck to
                    CheckpointValue(
                        records = 3,
                        serializedBytes = 5,
                        rejectedRecords = 2,
                    )
            ),
        )
        Assertions.assertFalse(manager.areRecordsPersistedForCheckpoint(ck))
        manager.incrementCheckpointCounts(
            BatchState.PERSISTED,
            mapOf(
                ck to
                    CheckpointValue(
                        records = 4,
                        serializedBytes = 5,
                        rejectedRecords = 1,
                    )
            ),
        )
        Assertions.assertTrue(manager.areRecordsPersistedForCheckpoint(ck))
    }

    @Test
    fun `persisted counts for multiple checkpoints`() {
        val manager = StreamManager(stream1)
        val ck1 = checkpoint("c1")
        val ck2 = checkpoint("c2")

        repeat(10) { manager.incrementReadCount(ck1) }
        repeat(15) { manager.incrementReadCount(ck2) }

        Assertions.assertFalse(manager.areRecordsPersistedForCheckpoint(ck1))
        Assertions.assertFalse(manager.areRecordsPersistedForCheckpoint(ck2))

        manager.incrementCheckpointCounts(
            BatchState.PERSISTED,
            mapOf(ck1 to CheckpointValue(10, 10)),
        )
        Assertions.assertTrue(manager.areRecordsPersistedForCheckpoint(ck1))
        Assertions.assertFalse(manager.areRecordsPersistedForCheckpoint(ck2))

        manager.incrementCheckpointCounts(
            BatchState.PERSISTED,
            mapOf(ck2 to CheckpointValue(15, 15)),
        )
        Assertions.assertTrue(manager.areRecordsPersistedForCheckpoint(ck1))
        Assertions.assertTrue(manager.areRecordsPersistedForCheckpoint(ck2))
    }

    @Test
    fun `persisted counts for multiple checkpoints out of order`() {
        val manager = StreamManager(stream1)
        val ck1 = checkpoint("c1")
        val ck2 = checkpoint("c2")

        repeat(10) { manager.incrementReadCount(ck1) }
        repeat(15) { manager.incrementReadCount(ck2) }

        Assertions.assertFalse(manager.areRecordsPersistedForCheckpoint(ck1))
        Assertions.assertFalse(manager.areRecordsPersistedForCheckpoint(ck2))

        manager.incrementCheckpointCounts(
            BatchState.PERSISTED,
            mapOf(ck2 to CheckpointValue(15, 15)),
        )
        Assertions.assertFalse(manager.areRecordsPersistedForCheckpoint(ck1))
        Assertions.assertTrue(manager.areRecordsPersistedForCheckpoint(ck2))

        manager.incrementCheckpointCounts(
            BatchState.PERSISTED,
            mapOf(ck1 to CheckpointValue(10, 10)),
        )
        Assertions.assertTrue(manager.areRecordsPersistedForCheckpoint(ck1))
        Assertions.assertTrue(manager.areRecordsPersistedForCheckpoint(ck2))
    }

    @Test
    fun `completion implies persistence`() {
        val manager = StreamManager(stream1)
        val ck = checkpoint("c1")

        repeat(10) { manager.incrementReadCount(ck) }

        Assertions.assertFalse(manager.areRecordsPersistedForCheckpoint(ck))
        manager.incrementCheckpointCounts(
            BatchState.COMPLETE,
            mapOf(ck to CheckpointValue(4, 4)),
        )
        Assertions.assertFalse(manager.areRecordsPersistedForCheckpoint(ck))
        manager.incrementCheckpointCounts(
            BatchState.COMPLETE,
            mapOf(ck to CheckpointValue(6, 6)),
        )
        Assertions.assertTrue(manager.areRecordsPersistedForCheckpoint(ck))

        // Additional persisted counts do not break anything
        manager.incrementCheckpointCounts(
            BatchState.PERSISTED,
            mapOf(ck to CheckpointValue(10, 10)),
        )
        Assertions.assertTrue(manager.areRecordsPersistedForCheckpoint(ck))
    }

    @Test
    fun `batch processing completion requires end-of-stream and complete counts`() {
        val cases =
            listOf(
                listOf("1", "2", "end"),
                listOf("1", "end", "2"),
                listOf("end", "1", "2"),
                listOf("end", "2", "1"),
                listOf("2", "1", "end"),
                listOf("2", "end", "1"),
            )

        cases.forEach { steps ->
            val manager = StreamManager(stream1)
            val ck1 = checkpoint("c1")
            val ck2 = checkpoint("c2")

            repeat(10) { manager.incrementReadCount(ck1) }
            repeat(20) { manager.incrementReadCount(ck2) }

            steps.forEachIndexed { index, step ->
                when (step) {
                    "1" ->
                        manager.incrementCheckpointCounts(
                            BatchState.COMPLETE,
                            mapOf(
                                ck1 to
                                    CheckpointValue(
                                        records = 9,
                                        serializedBytes = 10,
                                        rejectedRecords = 1,
                                    )
                            ),
                        )
                    "2" ->
                        manager.incrementCheckpointCounts(
                            BatchState.COMPLETE,
                            mapOf(ck2 to CheckpointValue(20, 20)),
                        )
                    "end" -> manager.markEndOfStream(true)
                }
                if (index < 2) {
                    Assertions.assertFalse(
                        manager.isBatchProcessingCompleteForCheckpoints(),
                        "steps: $steps; step: $index"
                    )
                } else {
                    Assertions.assertTrue(
                        manager.isBatchProcessingCompleteForCheckpoints(),
                        "steps: $steps; final step"
                    )
                }
            }
        }
    }

    @Test
    fun `committedCount returns max across states`() {
        val manager = StreamManager(stream1)
        val ck = checkpoint("c1")

        repeat(10) { manager.incrementReadCount(ck) }

        manager.incrementCheckpointCounts(
            BatchState.PERSISTED,
            mapOf(ck to CheckpointValue(records = 4, serializedBytes = 100, rejectedRecords = 1)),
        )
        manager.incrementCheckpointCounts(
            BatchState.COMPLETE,
            mapOf(ck to CheckpointValue(records = 5, serializedBytes = 90, rejectedRecords = 2)),
        )

        val committed = manager.committedCount(ck)
        Assertions.assertEquals(5, committed.records)
        Assertions.assertEquals(100, committed.serializedBytes)
        Assertions.assertEquals(2, committed.rejectedRecords)
    }

    @Test
    fun `hadNonzeroRecords reflects read state`() {
        val m1 = StreamManager(stream1)
        val ck1 = checkpoint("c1")
        Assertions.assertFalse(m1.hadNonzeroRecords())
        m1.incrementReadCount(ck1)
        Assertions.assertTrue(m1.hadNonzeroRecords())
    }

    @Test
    fun `areRecordsPersistedForCheckpoint does not throw`() {
        val manager = StreamManager(stream2)
        val ck = checkpoint("c-socket")
        // No read counts set, but should not throw
        Assertions.assertDoesNotThrow { manager.areRecordsPersistedForCheckpoint(ck) }
    }
}
