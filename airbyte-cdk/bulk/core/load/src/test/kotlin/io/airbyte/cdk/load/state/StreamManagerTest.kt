/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import io.airbyte.cdk.load.command.MockDestinationCatalogFactory.Companion.stream1
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory.Companion.stream2
import io.airbyte.cdk.load.message.BatchState
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow

class StreamManagerTest {
    @Test
    fun testCountRecordsAndCheckpoint() {
        val manager1 = StreamManager(stream1)
        val manager2 = StreamManager(stream2)

        Assertions.assertEquals(1, manager1.inferNextCheckpointKey().checkpointIndex.value)
        Assertions.assertEquals(1, manager2.inferNextCheckpointKey().checkpointIndex.value)

        // Incrementing once yields (n, n)
        repeat(10) { manager1.incrementReadCount() }
        val (index, count) = manager1.markCheckpoint()

        Assertions.assertEquals(10, index)
        Assertions.assertEquals(10, count)

        Assertions.assertEquals(2, manager1.inferNextCheckpointKey().checkpointIndex.value)
        Assertions.assertEquals(1, manager2.inferNextCheckpointKey().checkpointIndex.value)

        // Incrementing a second time yields (n + m, m)
        repeat(5) { manager1.incrementReadCount() }
        val (index2, count2) = manager1.markCheckpoint()

        Assertions.assertEquals(15, index2)
        Assertions.assertEquals(5, count2)

        Assertions.assertEquals(3, manager1.inferNextCheckpointKey().checkpointIndex.value)
        Assertions.assertEquals(1, manager2.inferNextCheckpointKey().checkpointIndex.value)

        // Never incrementing yields (0, 0)
        val (index3, count3) = manager2.markCheckpoint()

        Assertions.assertEquals(3, manager1.inferNextCheckpointKey().checkpointIndex.value)
        Assertions.assertEquals(2, manager2.inferNextCheckpointKey().checkpointIndex.value)

        Assertions.assertEquals(0, index3)
        Assertions.assertEquals(0, count3)

        // Incrementing twice in a row yields (n + m + 0, 0)
        val (index4, count4) = manager1.markCheckpoint()

        Assertions.assertEquals(4, manager1.inferNextCheckpointKey().checkpointIndex.value)
        Assertions.assertEquals(2, manager2.inferNextCheckpointKey().checkpointIndex.value)

        Assertions.assertEquals(15, index4)
        Assertions.assertEquals(0, count4)
    }

    @Test
    fun testMarkSucceeded() = runTest {
        val manager = StreamManager(stream1)
        val channel = Channel<Boolean>(Channel.UNLIMITED)

        launch { channel.send(manager.awaitStreamResult() is StreamProcessingSucceeded) }

        delay(500)
        Assertions.assertTrue(channel.tryReceive().isFailure)
        Assertions.assertThrows(IllegalStateException::class.java) {
            manager.markProcessingSucceeded()
        }
        manager.markEndOfStream(true)

        manager.markProcessingSucceeded()
        Assertions.assertTrue(channel.receive())

        Assertions.assertEquals(StreamProcessingSucceeded, manager.awaitStreamResult())
    }

    @Test
    fun testMarkFailure() = runTest {
        val manager = StreamManager(stream1)
        val channel = Channel<Boolean>(Channel.UNLIMITED)

        launch { channel.send(manager.awaitStreamResult() is StreamProcessingSucceeded) }

        delay(500)
        Assertions.assertTrue(channel.tryReceive().isFailure)
        manager.markProcessingFailed(Exception("test"))
        Assertions.assertFalse(channel.receive())

        Assertions.assertTrue(manager.awaitStreamResult() is StreamProcessingFailed)
    }

    @Test
    fun testCannotUpdateOrCloseReadClosedStream() {
        val manager = StreamManager(stream1)

        // Can't mark success before end-of-stream
        Assertions.assertThrows(IllegalStateException::class.java) {
            manager.markProcessingSucceeded()
        }

        manager.incrementReadCount()
        manager.markEndOfStream(true)

        // Can't update after end-of-stream
        Assertions.assertThrows(IllegalStateException::class.java) { manager.incrementReadCount() }
        Assertions.assertThrows(IllegalStateException::class.java) { manager.markEndOfStream(true) }

        // Can close now
        Assertions.assertDoesNotThrow(manager::markProcessingSucceeded)
    }

    @Test
    fun `test persisted counts`() {
        val manager = StreamManager(stream1)
        val checkpointId = manager.inferNextCheckpointKey().checkpointId

        repeat(10) { manager.incrementReadCount() }
        manager.markCheckpoint()

        Assertions.assertFalse(manager.areRecordsPersistedForCheckpoint(checkpointId))
        manager.incrementCheckpointCounts(
            BatchState.PERSISTED,
            mapOf(checkpointId to CheckpointValue(5, 5)),
        )
        Assertions.assertFalse(manager.areRecordsPersistedForCheckpoint(checkpointId))
        manager.incrementCheckpointCounts(
            BatchState.PERSISTED,
            mapOf(checkpointId to CheckpointValue(5, 5)),
        )
        Assertions.assertTrue(manager.areRecordsPersistedForCheckpoint(checkpointId))
    }

    @Test
    fun `test persisted count for multiple checkpoints`() {
        val manager = StreamManager(stream1)

        val checkpointId1 = manager.inferNextCheckpointKey().checkpointId
        repeat(10) { manager.incrementReadCount() }
        manager.markCheckpoint()

        val checkpointId2 = manager.inferNextCheckpointKey().checkpointId
        repeat(15) { manager.incrementReadCount() }
        manager.markCheckpoint()

        Assertions.assertFalse(manager.areRecordsPersistedForCheckpoint(checkpointId1))
        Assertions.assertFalse(manager.areRecordsPersistedForCheckpoint(checkpointId2))

        manager.incrementCheckpointCounts(
            BatchState.PERSISTED,
            mapOf(checkpointId1 to CheckpointValue(10, 10)),
        )
        Assertions.assertTrue(manager.areRecordsPersistedForCheckpoint(checkpointId1))
        Assertions.assertFalse(manager.areRecordsPersistedForCheckpoint(checkpointId2))

        manager.incrementCheckpointCounts(
            BatchState.PERSISTED,
            mapOf(checkpointId2 to CheckpointValue(15, 15)),
        )
        Assertions.assertTrue(manager.areRecordsPersistedForCheckpoint(checkpointId1))
        Assertions.assertTrue(manager.areRecordsPersistedForCheckpoint(checkpointId2))
    }

    @Test
    fun `test persisted count for multiple checkpoints out of order`() {
        val manager = StreamManager(stream1)

        val checkpointId1 = manager.inferNextCheckpointKey().checkpointId

        repeat(10) { manager.incrementReadCount() }
        manager.markCheckpoint()

        val checkpointId2 = manager.inferNextCheckpointKey().checkpointId
        repeat(15) { manager.incrementReadCount() }

        manager.markCheckpoint()

        Assertions.assertFalse(manager.areRecordsPersistedForCheckpoint(checkpointId1))
        Assertions.assertFalse(manager.areRecordsPersistedForCheckpoint(checkpointId2))

        manager.incrementCheckpointCounts(
            BatchState.PERSISTED,
            mapOf(checkpointId2 to CheckpointValue(15, 15)),
        )
        Assertions.assertFalse(manager.areRecordsPersistedForCheckpoint(checkpointId1))
        Assertions.assertTrue(manager.areRecordsPersistedForCheckpoint(checkpointId2))

        manager.incrementCheckpointCounts(
            BatchState.PERSISTED,
            mapOf(checkpointId1 to CheckpointValue(10, 10)),
        )
        Assertions.assertTrue(manager.areRecordsPersistedForCheckpoint(checkpointId1))
        Assertions.assertTrue(manager.areRecordsPersistedForCheckpoint(checkpointId2))
    }

    @Test
    fun `test completion implies persistence`() {
        val manager = StreamManager(stream1)

        val checkpointId1 = manager.inferNextCheckpointKey().checkpointId

        repeat(10) { manager.incrementReadCount() }
        manager.markCheckpoint()

        Assertions.assertFalse(manager.areRecordsPersistedForCheckpoint(checkpointId1))
        manager.incrementCheckpointCounts(
            BatchState.COMPLETE,
            mapOf(checkpointId1 to CheckpointValue(4, 4)),
        )
        Assertions.assertFalse(manager.areRecordsPersistedForCheckpoint(checkpointId1))
        manager.incrementCheckpointCounts(
            BatchState.COMPLETE,
            mapOf(checkpointId1 to CheckpointValue(6, 6)),
        )
        Assertions.assertTrue(manager.areRecordsPersistedForCheckpoint(checkpointId1))

        // Can still count persisted (but without effect)
        manager.incrementCheckpointCounts(
            BatchState.PERSISTED,
            mapOf(checkpointId1 to CheckpointValue(10, 10)),
        )
        Assertions.assertTrue(manager.areRecordsPersistedForCheckpoint(checkpointId1))
    }

    @Test
    fun `test completion check`() {
        // All three steps are required, but they can happen in any order.
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
            val checkpointId1 = manager.inferNextCheckpointKey().checkpointId

            repeat(10) { manager.incrementReadCount() }
            manager.markCheckpoint()

            val checkpointId2 = manager.inferNextCheckpointKey().checkpointId
            repeat(20) { manager.incrementReadCount() }
            manager.markCheckpoint()

            steps.forEachIndexed { index, step ->
                when (step) {
                    "1" ->
                        manager.incrementCheckpointCounts(
                            BatchState.COMPLETE,
                            mapOf(checkpointId1 to CheckpointValue(10, 10)),
                        )
                    "2" ->
                        manager.incrementCheckpointCounts(
                            BatchState.COMPLETE,
                            mapOf(checkpointId2 to CheckpointValue(20, 20)),
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
    fun `do not throw when counting before marking`() {
        val manager1 = StreamManager(stream1)

        Assertions.assertEquals(1, manager1.inferNextCheckpointKey().checkpointIndex.value)

        repeat(10) { manager1.incrementReadCount() }
        manager1.incrementCheckpointCounts(
            BatchState.PERSISTED,
            mapOf(manager1.inferNextCheckpointKey().checkpointId to CheckpointValue(10, 10)),
        )
        assertDoesNotThrow { manager1.markCheckpoint() }
    }

    @Test
    fun `throw if inferNextCheckpointKey called when disabled`() {
        val manager1 = StreamManager(stream1, requireCheckpointKeyOnState = true)
        Assertions.assertThrows(IllegalStateException::class.java) {
            manager1.inferNextCheckpointKey()
        }
    }

    @Test
    fun `throw if force marking a checkpoint when disabled`() {
        val manager1 = StreamManager(stream1, requireCheckpointKeyOnState = true)
        Assertions.assertThrows(IllegalStateException::class.java) { manager1.markCheckpoint() }
    }
}
