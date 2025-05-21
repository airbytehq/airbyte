/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import io.airbyte.cdk.load.command.DestinationStream
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

        Assertions.assertEquals(0, manager1.getCurrentCheckpointId().id)
        Assertions.assertEquals(0, manager2.getCurrentCheckpointId().id)

        // Incrementing once yields (n, n)
        repeat(10) { manager1.incrementReadCount() }
        val (index, count) = manager1.markCheckpoint()

        Assertions.assertEquals(10, index)
        Assertions.assertEquals(10, count)

        Assertions.assertEquals(1, manager1.getCurrentCheckpointId().id)
        Assertions.assertEquals(0, manager2.getCurrentCheckpointId().id)

        // Incrementing a second time yields (n + m, m)
        repeat(5) { manager1.incrementReadCount() }
        val (index2, count2) = manager1.markCheckpoint()

        Assertions.assertEquals(15, index2)
        Assertions.assertEquals(5, count2)

        Assertions.assertEquals(2, manager1.getCurrentCheckpointId().id)
        Assertions.assertEquals(0, manager2.getCurrentCheckpointId().id)

        // Never incrementing yields (0, 0)
        val (index3, count3) = manager2.markCheckpoint()

        Assertions.assertEquals(2, manager1.getCurrentCheckpointId().id)
        Assertions.assertEquals(1, manager2.getCurrentCheckpointId().id)

        Assertions.assertEquals(0, index3)
        Assertions.assertEquals(0, count3)

        // Incrementing twice in a row yields (n + m + 0, 0)
        val (index4, count4) = manager1.markCheckpoint()

        Assertions.assertEquals(3, manager1.getCurrentCheckpointId().id)
        Assertions.assertEquals(1, manager2.getCurrentCheckpointId().id)

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

    // TODO: break these out into non-parameterized tests, factor out mixing streams.
    //  (It's irrelevant if testing at the single manager level.)
    sealed class TestEvent
    data class SetRecordCount(val count: Long) : TestEvent()
    data object SetEndOfStream : TestEvent()
    data class AddPersisted(val firstIndex: Long, val lastIndex: Long) : TestEvent()
    data class AddComplete(val firstIndex: Long, val lastIndex: Long) : TestEvent()
    data class ExpectPersistedUntil(val end: Long, val expectation: Boolean = true) : TestEvent()
    data class ExpectComplete(val expectation: Boolean = true) : TestEvent()

    data class TestCase(
        val name: String,
        val events: List<Pair<DestinationStream, TestEvent>>,
    )

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
        val checkpointId = manager.getCurrentCheckpointId()
        val taskName = "foo"
        val part = 1

        repeat(10) { manager.incrementReadCount() }
        manager.markCheckpoint()

        Assertions.assertFalse(manager.areRecordsPersistedUntilCheckpoint(checkpointId))
        manager.incrementCheckpointCounts(
            taskName,
            part,
            BatchState.PERSISTED,
            mapOf(checkpointId to 5),
            1
        )
        Assertions.assertFalse(manager.areRecordsPersistedUntilCheckpoint(checkpointId))
        manager.incrementCheckpointCounts(
            taskName,
            part,
            BatchState.PERSISTED,
            mapOf(checkpointId to 5),
            1
        )
        Assertions.assertTrue(manager.areRecordsPersistedUntilCheckpoint(checkpointId))
    }

    @Test
    fun `test persisted count for multiple checkpoints`() {
        val manager = StreamManager(stream1)
        val taskName = "foo"
        val part = 1

        val checkpointId1 = manager.getCurrentCheckpointId()
        repeat(10) { manager.incrementReadCount() }
        manager.markCheckpoint()

        val checkpointId2 = manager.getCurrentCheckpointId()
        repeat(15) { manager.incrementReadCount() }
        manager.markCheckpoint()

        Assertions.assertFalse(manager.areRecordsPersistedUntilCheckpoint(checkpointId1))
        Assertions.assertFalse(manager.areRecordsPersistedUntilCheckpoint(checkpointId2))

        manager.incrementCheckpointCounts(
            taskName,
            part,
            BatchState.PERSISTED,
            mapOf(checkpointId1 to 10),
            1
        )
        Assertions.assertTrue(manager.areRecordsPersistedUntilCheckpoint(checkpointId1))
        Assertions.assertFalse(manager.areRecordsPersistedUntilCheckpoint(checkpointId2))

        manager.incrementCheckpointCounts(
            taskName,
            part,
            BatchState.PERSISTED,
            mapOf(checkpointId2 to 15),
            1
        )
        Assertions.assertTrue(manager.areRecordsPersistedUntilCheckpoint(checkpointId1))
        Assertions.assertTrue(manager.areRecordsPersistedUntilCheckpoint(checkpointId2))
    }

    @Test
    fun `test persisted count for multiple checkpoints out of order`() {
        val manager = StreamManager(stream1)
        val taskName = "foo"
        val part = 1

        val checkpointId1 = manager.getCurrentCheckpointId()

        repeat(10) { manager.incrementReadCount() }
        manager.markCheckpoint()

        val checkpointId2 = manager.getCurrentCheckpointId()
        repeat(15) { manager.incrementReadCount() }

        manager.markCheckpoint()

        Assertions.assertFalse(manager.areRecordsPersistedUntilCheckpoint(checkpointId1))
        Assertions.assertFalse(manager.areRecordsPersistedUntilCheckpoint(checkpointId2))

        manager.incrementCheckpointCounts(
            taskName,
            part,
            BatchState.PERSISTED,
            mapOf(checkpointId2 to 15),
            1
        )
        Assertions.assertFalse(manager.areRecordsPersistedUntilCheckpoint(checkpointId1))
        Assertions.assertFalse(manager.areRecordsPersistedUntilCheckpoint(checkpointId2))

        manager.incrementCheckpointCounts(
            taskName,
            part,
            BatchState.PERSISTED,
            mapOf(checkpointId1 to 10),
            1
        )
        Assertions.assertTrue(manager.areRecordsPersistedUntilCheckpoint(checkpointId1))
        Assertions.assertTrue(manager.areRecordsPersistedUntilCheckpoint(checkpointId2))
    }

    @Test
    fun `test completion implies persistence`() {
        val manager = StreamManager(stream1)

        val checkpointId1 = manager.getCurrentCheckpointId()

        repeat(10) { manager.incrementReadCount() }
        manager.markCheckpoint()

        Assertions.assertFalse(manager.areRecordsPersistedUntilCheckpoint(checkpointId1))
        manager.incrementCheckpointCounts(
            "foo",
            1,
            BatchState.COMPLETE,
            mapOf(checkpointId1 to 4),
            1
        )
        Assertions.assertFalse(manager.areRecordsPersistedUntilCheckpoint(checkpointId1))
        manager.incrementCheckpointCounts(
            "foo",
            2,
            BatchState.COMPLETE,
            mapOf(checkpointId1 to 6),
            1
        )
        Assertions.assertTrue(manager.areRecordsPersistedUntilCheckpoint(checkpointId1))

        // Can still count persisted (but without effect)
        manager.incrementCheckpointCounts(
            "bar",
            1,
            BatchState.PERSISTED,
            mapOf(checkpointId1 to 10),
            1
        )
        Assertions.assertTrue(manager.areRecordsPersistedUntilCheckpoint(checkpointId1))
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
            val checkpointId1 = manager.getCurrentCheckpointId()

            repeat(10) { manager.incrementReadCount() }
            manager.markCheckpoint()

            val checkpointId2 = manager.getCurrentCheckpointId()
            repeat(20) { manager.incrementReadCount() }
            manager.markCheckpoint()

            steps.forEachIndexed { index, step ->
                when (step) {
                    "1" ->
                        manager.incrementCheckpointCounts(
                            "foo",
                            1,
                            BatchState.COMPLETE,
                            mapOf(checkpointId1 to 10),
                            1
                        )
                    "2" ->
                        manager.incrementCheckpointCounts(
                            "bar",
                            1,
                            BatchState.COMPLETE,
                            mapOf(checkpointId2 to 20),
                            1
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

        Assertions.assertEquals(0, manager1.getCurrentCheckpointId().id)

        repeat(10) { manager1.incrementReadCount() }
        manager1.incrementCheckpointCounts(
            "foo",
            1,
            BatchState.PERSISTED,
            mapOf(manager1.getCurrentCheckpointId() to 10),
            1
        )
        assertDoesNotThrow { manager1.markCheckpoint() }
    }
}
