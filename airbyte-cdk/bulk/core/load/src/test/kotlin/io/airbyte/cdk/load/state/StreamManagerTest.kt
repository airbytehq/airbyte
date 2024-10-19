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

        // Incrementing once yields (n, n)
        repeat(10) { manager1.countRecordIn() }
        val (index, count) = manager1.markCheckpoint()

        Assertions.assertEquals(10, index)
        Assertions.assertEquals(10, count)

        // Incrementing a second time yields (n + m, m)
        repeat(5) { manager1.countRecordIn() }
        val (index2, count2) = manager1.markCheckpoint()

        Assertions.assertEquals(15, index2)
        Assertions.assertEquals(5, count2)

        // Never incrementing yields (0, 0)
        val (index3, count3) = manager2.markCheckpoint()

        Assertions.assertEquals(0, index3)
        Assertions.assertEquals(0, count3)

        // Incrementing twice in a row yields (n + m + 0, 0)
        val (index4, count4) = manager1.markCheckpoint()

        Assertions.assertEquals(15, index4)
        Assertions.assertEquals(0, count4)
    }

    @Test
    fun testMarkSucceeded() = runTest {
        val manager = DefaultStreamManager(stream1)
        val channel = Channel<Boolean>(Channel.UNLIMITED)

        launch { channel.send(manager.awaitStreamResult() is StreamSucceeded) }

        delay(500)
        Assertions.assertTrue(channel.tryReceive().isFailure)
        Assertions.assertThrows(IllegalStateException::class.java) { manager.markSucceeded() }
        manager.markEndOfStream()

        manager.markSucceeded()
        Assertions.assertTrue(channel.receive())

        Assertions.assertEquals(StreamSucceeded, manager.awaitStreamResult())
    }

    @Test
    fun testMarkFailure() = runTest {
        val manager = DefaultStreamManager(stream1)
        val channel = Channel<Boolean>(Channel.UNLIMITED)

        launch { channel.send(manager.awaitStreamResult() is StreamSucceeded) }

        delay(500)
        Assertions.assertTrue(channel.tryReceive().isFailure)
        manager.markFailed(Exception("test"))
        Assertions.assertFalse(channel.receive())

        Assertions.assertTrue(manager.awaitStreamResult() is StreamFailed)
    }

    @Test
    fun testMarkKilled() = runTest {
        val manager = DefaultStreamManager(stream1)
        val channel = Channel<Boolean>(Channel.UNLIMITED)

        launch { channel.send(manager.awaitStreamResult() is StreamSucceeded) }

        delay(500)
        Assertions.assertTrue(channel.tryReceive().isFailure)
        manager.markKilled(Exception("test"))
        Assertions.assertFalse(channel.receive())

        Assertions.assertTrue(manager.awaitStreamResult() is StreamKilled)
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
                    )
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
                is SetRecordCount -> repeat(event.count.toInt()) { manager.countRecordIn() }
                is SetEndOfStream -> manager.markEndOfStream()
                is AddPersisted ->
                    manager.updateBatchState(
                        BatchEnvelope(
                            SimpleBatch(Batch.State.PERSISTED),
                            Range.closed(event.firstIndex, event.lastIndex)
                        )
                    )
                is AddComplete ->
                    manager.updateBatchState(
                        BatchEnvelope(
                            SimpleBatch(Batch.State.COMPLETE),
                            Range.closed(event.firstIndex, event.lastIndex)
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
        Assertions.assertThrows(IllegalStateException::class.java) { manager.markSucceeded() }

        manager.countRecordIn()
        manager.markEndOfStream()

        // Can't update after end-of-stream
        Assertions.assertThrows(IllegalStateException::class.java) { manager.countRecordIn() }
        Assertions.assertThrows(IllegalStateException::class.java) { manager.markEndOfStream() }

        // Can close now
        Assertions.assertDoesNotThrow(manager::markSucceeded)
    }
}
