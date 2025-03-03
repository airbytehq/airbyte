/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import com.google.common.collect.Range
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory.Companion.stream1
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory.Companion.stream2
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.SimpleBatch
import java.util.stream.Stream
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow
import org.junit.jupiter.api.extension.ExtensionContext
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.ArgumentsProvider
import org.junit.jupiter.params.provider.ArgumentsSource

class StreamManagerTest {
    @Test
    fun testCountRecordsAndCheckpoint() {
        val manager1 = DefaultStreamManager(stream1)
        val manager2 = DefaultStreamManager(stream2)

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
        val manager = DefaultStreamManager(stream1)
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
        val manager = DefaultStreamManager(stream1)
        val channel = Channel<Boolean>(Channel.UNLIMITED)

        launch { channel.send(manager.awaitStreamResult() is StreamProcessingSucceeded) }

        delay(500)
        Assertions.assertTrue(channel.tryReceive().isFailure)
        manager.markProcessingFailed(Exception("test"))
        Assertions.assertFalse(channel.receive())

        Assertions.assertTrue(manager.awaitStreamResult() is StreamProcessingFailed)
    }

    class TestUpdateBatchStateProvider : ArgumentsProvider {
        override fun provideArguments(context: ExtensionContext): Stream<out Arguments> {
            return listOf(
                    TestCase(
                        "Single stream, single batch",
                        listOf(
                            Pair(stream1, SetRecordCount(10)),
                            Pair(stream1, AddPersisted(0, 9)),
                            Pair(stream1, ExpectPersistedUntil(9)),
                            Pair(stream1, ExpectPersistedUntil(10)),
                            Pair(stream1, ExpectComplete(false)),
                            Pair(stream1, ExpectPersistedUntil(11, false)),
                            Pair(stream2, ExpectPersistedUntil(10, false)),
                        )
                    ),
                    TestCase(
                        "Single stream, multiple batches",
                        listOf(
                            Pair(stream1, SetRecordCount(10)),
                            Pair(stream1, AddPersisted(0, 4)),
                            Pair(stream1, ExpectPersistedUntil(4)),
                            Pair(stream1, AddPersisted(5, 9)),
                            Pair(stream1, ExpectPersistedUntil(9)),
                            Pair(stream1, ExpectPersistedUntil(10)),
                            Pair(stream1, ExpectComplete(false)),
                            Pair(stream1, AddComplete(0, 9)),
                            Pair(stream1, ExpectComplete(false)),
                            Pair(stream1, SetEndOfStream),
                            Pair(stream1, ExpectComplete(true)),
                            Pair(stream1, ExpectPersistedUntil(11, false)),
                            Pair(stream2, ExpectPersistedUntil(10, false)),
                        )
                    ),
                    TestCase(
                        "Single stream, multiple batches, out of order",
                        listOf(
                            Pair(stream1, SetRecordCount(10)),
                            Pair(stream1, AddPersisted(5, 9)),
                            Pair(stream1, ExpectPersistedUntil(10, false)),
                            Pair(stream1, AddPersisted(0, 4)),
                            Pair(stream1, ExpectPersistedUntil(10)),
                            Pair(stream1, ExpectComplete(false)),
                            Pair(stream1, SetEndOfStream),
                            Pair(stream1, AddComplete(5, 9)),
                            Pair(stream1, ExpectComplete(false)),
                            Pair(stream1, AddComplete(0, 4)),
                            Pair(stream1, ExpectComplete(true)),
                        )
                    ),
                    TestCase(
                        "Single stream, multiple batches, complete also persists",
                        listOf(
                            Pair(stream1, SetRecordCount(10)),
                            Pair(stream1, AddComplete(0, 4)),
                            Pair(stream1, ExpectPersistedUntil(5, true)),
                            Pair(stream1, ExpectComplete(false)),
                            Pair(stream1, SetEndOfStream),
                            Pair(stream1, AddComplete(5, 9)),
                            Pair(stream1, ExpectComplete(true)),
                        )
                    ),
                    TestCase(
                        "Single stream, multiple batches, persist/complete out of order",
                        listOf(
                            Pair(stream1, SetRecordCount(10)),
                            Pair(
                                stream1,
                                AddComplete(5, 9)
                            ), // complete a rangeset before the preceding rangeset is persisted
                            Pair(stream1, AddPersisted(0, 4)),
                            Pair(stream1, ExpectPersistedUntil(10, true)),
                            Pair(stream1, ExpectComplete(false)),
                            Pair(stream1, AddComplete(0, 4)),
                            Pair(stream1, SetEndOfStream),
                            Pair(stream1, ExpectComplete(true)),
                        )
                    ),
                    TestCase(
                        "multiple streams",
                        listOf(
                            Pair(stream1, SetRecordCount(10)),
                            Pair(stream2, SetRecordCount(20)),
                            Pair(stream2, AddPersisted(0, 9)),
                            Pair(stream2, ExpectPersistedUntil(10, true)),
                            Pair(stream1, ExpectPersistedUntil(10, false)),
                            Pair(stream2, SetEndOfStream),
                            Pair(stream2, ExpectComplete(false)),
                            Pair(stream1, AddPersisted(0, 9)),
                            Pair(stream1, ExpectPersistedUntil(10)),
                            Pair(stream1, ExpectComplete(false)),
                            Pair(stream2, AddComplete(10, 20)),
                            Pair(stream2, ExpectComplete(false)),
                            Pair(stream1, SetEndOfStream),
                            Pair(stream1, ExpectComplete(false)),
                            Pair(stream1, AddComplete(0, 9)),
                            Pair(stream1, ExpectComplete(true)),
                            Pair(stream2, AddComplete(0, 9)),
                            Pair(stream2, ExpectPersistedUntil(20, true)),
                            Pair(stream2, ExpectComplete(true)),
                        )
                    ),
                    TestCase(
                        "mingle streams, multiple batches, complete also persists",
                        listOf(
                            Pair(stream1, SetRecordCount(10)),
                            Pair(stream1, AddComplete(0, 4)),
                            Pair(stream1, ExpectPersistedUntil(5, true)),
                            Pair(stream2, AddComplete(0, 4)),
                            Pair(stream2, ExpectPersistedUntil(5, true)),
                            Pair(stream1, ExpectComplete(false)),
                            Pair(stream2, ExpectComplete(false)),
                            Pair(stream1, SetEndOfStream),
                            Pair(stream1, AddComplete(5, 9)),
                            Pair(stream2, AddComplete(5, 9)),
                            Pair(stream2, SetEndOfStream),
                            Pair(stream1, ExpectComplete(true)),
                            Pair(stream2, ExpectComplete(true)),
                        )
                    ),
                    TestCase(
                        "mingle streams, multiple batches, persist/complete out of order",
                        listOf(
                            Pair(stream1, SetRecordCount(10)),
                            Pair(stream1, AddComplete(5, 9)),
                            Pair(stream1, ExpectPersistedUntil(10, false)),
                            Pair(stream2, AddComplete(5, 9)),
                            Pair(stream2, ExpectPersistedUntil(10, false)),
                            Pair(stream1, ExpectComplete(false)),
                            Pair(stream2, ExpectComplete(false)),
                            Pair(stream1, SetEndOfStream),
                            Pair(stream1, AddComplete(0, 4)),
                            Pair(stream2, AddComplete(0, 4)),
                            Pair(stream2, SetEndOfStream),
                            Pair(stream1, ExpectComplete(true)),
                            Pair(stream2, ExpectComplete(true)),
                        )
                    ),
                )
                .map { Arguments.of(it) }
                .stream()
        }
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

    @ParameterizedTest
    @ArgumentsSource(TestUpdateBatchStateProvider::class)
    fun testUpdateBatchState(testCase: TestCase) {
        val managers =
            mapOf(
                stream1.descriptor to DefaultStreamManager(stream1),
                stream2.descriptor to DefaultStreamManager(stream2)
            )
        testCase.events.forEach { (stream, event) ->
            val manager = managers[stream.descriptor]!!
            when (event) {
                is SetRecordCount -> repeat(event.count.toInt()) { manager.incrementReadCount() }
                is SetEndOfStream -> manager.markEndOfStream(true)
                is AddPersisted ->
                    manager.updateBatchState(
                        BatchEnvelope(
                            SimpleBatch(Batch.State.PERSISTED),
                            Range.closed(event.firstIndex, event.lastIndex),
                            stream.descriptor
                        )
                    )
                is AddComplete ->
                    manager.updateBatchState(
                        BatchEnvelope(
                            SimpleBatch(Batch.State.COMPLETE),
                            Range.closed(event.firstIndex, event.lastIndex),
                            stream.descriptor
                        )
                    )
                is ExpectPersistedUntil ->
                    Assertions.assertEquals(
                        event.expectation,
                        manager.areRecordsPersistedUntil(event.end),
                        "$stream: ${testCase.name}: ${event.end}"
                    )
                is ExpectComplete ->
                    Assertions.assertEquals(
                        event.expectation,
                        manager.isBatchProcessingComplete(),
                        "$stream: ${testCase.name}"
                    )
            }
        }
    }

    @Test
    fun testCannotUpdateOrCloseReadClosedStream() {
        val manager = DefaultStreamManager(stream1)

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
    fun testEmptyCompletedStreamYieldsBatchProcessingComplete() {
        val manager = DefaultStreamManager(stream1)
        manager.markEndOfStream(true)
        Assertions.assertTrue(manager.isBatchProcessingComplete())
    }

    @Test
    fun `ranges with the same id conflate to latest state`() {
        val manager = DefaultStreamManager(stream1)
        val range1 = Range.closed(0L, 9L)
        val batch1 =
            BatchEnvelope(
                SimpleBatch(Batch.State.STAGED, groupId = "foo"),
                range1,
                stream1.descriptor
            )

        val range2 = Range.closed(10, 19L)
        val batch2 =
            BatchEnvelope(
                SimpleBatch(Batch.State.PERSISTED, groupId = "foo"),
                range2,
                stream1.descriptor
            )

        manager.updateBatchState(batch1)
        Assertions.assertFalse(manager.areRecordsPersistedUntil(10L), "local < persisted")
        manager.updateBatchState(batch2)
        Assertions.assertTrue(manager.areRecordsPersistedUntil(10L), "later state propagates back")
    }

    @Test
    fun `ranges with a different id conflate to latest state`() {
        val manager = DefaultStreamManager(stream1)
        val range1 = Range.closed(0L, 9L)
        val batch1 =
            BatchEnvelope(
                SimpleBatch(Batch.State.STAGED, groupId = "foo"),
                range1,
                stream1.descriptor
            )

        val range2 = Range.closed(10, 19L)
        val batch2 =
            BatchEnvelope(
                SimpleBatch(Batch.State.PERSISTED, groupId = "bar"),
                range2,
                stream1.descriptor
            )

        manager.updateBatchState(batch1)
        Assertions.assertFalse(manager.areRecordsPersistedUntil(10L), "local < persisted")
        manager.updateBatchState(batch2)
        Assertions.assertFalse(
            manager.areRecordsPersistedUntil(10L),
            "state does not propagate to other ids"
        )
    }

    @Test
    fun `state does not conflate between id and no id`() {
        val manager = DefaultStreamManager(stream1)
        val range1 = Range.closed(0L, 9L)
        val batch1 =
            BatchEnvelope(
                SimpleBatch(Batch.State.STAGED, groupId = null),
                range1,
                stream1.descriptor
            )

        val range2 = Range.closed(10, 19L)
        val batch2 =
            BatchEnvelope(
                SimpleBatch(Batch.State.PERSISTED, groupId = "bar"),
                range2,
                stream1.descriptor
            )

        manager.updateBatchState(batch1)
        Assertions.assertFalse(manager.areRecordsPersistedUntil(10L), "local < persisted")
        manager.updateBatchState(batch2)
        Assertions.assertFalse(
            manager.areRecordsPersistedUntil(10L),
            "state does not propagate to null ids"
        )
    }

    @Test
    fun `max of newer and older state is always used`() {
        val manager = DefaultStreamManager(stream1)
        val range1 = Range.closed(0L, 9L)
        val batch1 =
            BatchEnvelope(
                SimpleBatch(Batch.State.PERSISTED, groupId = "foo"),
                range1,
                stream1.descriptor
            )

        val range2 = Range.closed(10, 19L)
        val batch2 =
            BatchEnvelope(
                SimpleBatch(Batch.State.STAGED, groupId = "foo"),
                range2,
                stream1.descriptor
            )

        manager.updateBatchState(batch1)
        Assertions.assertFalse(manager.areRecordsPersistedUntil(20L), "local < persisted")
        manager.updateBatchState(batch2)
        Assertions.assertTrue(
            manager.areRecordsPersistedUntil(20L),
            "max of newer and older state is used"
        )
    }

    @Test
    fun `max of older and newer state is always used`() {
        val manager = DefaultStreamManager(stream1)
        val range1 = Range.closed(0L, 9L)
        val batch1 =
            BatchEnvelope(
                SimpleBatch(Batch.State.COMPLETE, groupId = "foo"),
                range1,
                stream1.descriptor
            )

        val range2 = Range.closed(10, 19L)
        val batch2 =
            BatchEnvelope(
                SimpleBatch(Batch.State.PERSISTED, groupId = "foo"),
                range2,
                stream1.descriptor
            )
        manager.markEndOfStream(true)

        manager.updateBatchState(batch2)
        manager.updateBatchState(batch1)
        Assertions.assertTrue(
            manager.isBatchProcessingComplete(),
            "max of older and newer state is used"
        )
    }

    @Test
    fun `test persisted counts`() {
        val manager = DefaultStreamManager(stream1)
        val checkpointId = manager.getCurrentCheckpointId()

        repeat(10) { manager.incrementReadCount() }
        manager.markCheckpoint()

        Assertions.assertFalse(manager.areRecordsPersistedUntilCheckpoint(checkpointId))
        manager.incrementPersistedCount(checkpointId, 5)
        Assertions.assertFalse(manager.areRecordsPersistedUntilCheckpoint(checkpointId))
        manager.incrementPersistedCount(checkpointId, 5)
        Assertions.assertTrue(manager.areRecordsPersistedUntilCheckpoint(checkpointId))
    }

    @Test
    fun `test persisted count for multiple checkpoints`() {
        val manager = DefaultStreamManager(stream1)

        val checkpointId1 = manager.getCurrentCheckpointId()
        repeat(10) { manager.incrementReadCount() }
        manager.markCheckpoint()

        val checkpointId2 = manager.getCurrentCheckpointId()
        repeat(15) { manager.incrementReadCount() }
        manager.markCheckpoint()

        Assertions.assertFalse(manager.areRecordsPersistedUntilCheckpoint(checkpointId1))
        Assertions.assertFalse(manager.areRecordsPersistedUntilCheckpoint(checkpointId2))

        manager.incrementPersistedCount(checkpointId1, 10)
        Assertions.assertTrue(manager.areRecordsPersistedUntilCheckpoint(checkpointId1))
        Assertions.assertFalse(manager.areRecordsPersistedUntilCheckpoint(checkpointId2))

        manager.incrementPersistedCount(checkpointId2, 15)
        Assertions.assertTrue(manager.areRecordsPersistedUntilCheckpoint(checkpointId1))
        Assertions.assertTrue(manager.areRecordsPersistedUntilCheckpoint(checkpointId2))
    }

    @Test
    fun `test persisted count for multiple checkpoints out of order`() {
        val manager = DefaultStreamManager(stream1)

        val checkpointId1 = manager.getCurrentCheckpointId()

        repeat(10) { manager.incrementReadCount() }
        manager.markCheckpoint()

        val checkpointId2 = manager.getCurrentCheckpointId()
        repeat(15) { manager.incrementReadCount() }

        manager.markCheckpoint()

        Assertions.assertFalse(manager.areRecordsPersistedUntilCheckpoint(checkpointId1))
        Assertions.assertFalse(manager.areRecordsPersistedUntilCheckpoint(checkpointId2))

        manager.incrementPersistedCount(checkpointId2, 15)
        Assertions.assertFalse(manager.areRecordsPersistedUntilCheckpoint(checkpointId1))
        Assertions.assertFalse(manager.areRecordsPersistedUntilCheckpoint(checkpointId2))

        manager.incrementPersistedCount(checkpointId1, 10)

        Assertions.assertTrue(manager.areRecordsPersistedUntilCheckpoint(checkpointId1))
        Assertions.assertTrue(manager.areRecordsPersistedUntilCheckpoint(checkpointId2))
    }

    @Test
    fun `test completion implies persistence`() {
        val manager = DefaultStreamManager(stream1)

        val checkpointId1 = manager.getCurrentCheckpointId()

        repeat(10) { manager.incrementReadCount() }
        manager.markCheckpoint()

        Assertions.assertFalse(manager.areRecordsPersistedUntilCheckpoint(checkpointId1))
        manager.incrementCompletedCount(checkpointId1, 4)
        Assertions.assertFalse(manager.areRecordsPersistedUntilCheckpoint(checkpointId1))
        manager.incrementCompletedCount(checkpointId1, 6)
        Assertions.assertTrue(manager.areRecordsPersistedUntilCheckpoint(checkpointId1))

        // Can still count persisted (but without effect)
        manager.incrementPersistedCount(checkpointId1, 10)
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
            val manager = DefaultStreamManager(stream1)
            val checkpointId1 = manager.getCurrentCheckpointId()

            repeat(10) { manager.incrementReadCount() }
            manager.markCheckpoint()

            val checkpointId2 = manager.getCurrentCheckpointId()
            repeat(20) { manager.incrementReadCount() }
            manager.markCheckpoint()

            steps.forEachIndexed { index, step ->
                when (step) {
                    "1" -> manager.incrementCompletedCount(checkpointId1, 10)
                    "2" -> manager.incrementCompletedCount(checkpointId2, 20)
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
        val manager1 = DefaultStreamManager(stream1)

        Assertions.assertEquals(0, manager1.getCurrentCheckpointId().id)

        repeat(10) { manager1.incrementReadCount() }
        manager1.incrementPersistedCount(manager1.getCurrentCheckpointId(), 10)
        assertDoesNotThrow { manager1.markCheckpoint() }
    }
}
