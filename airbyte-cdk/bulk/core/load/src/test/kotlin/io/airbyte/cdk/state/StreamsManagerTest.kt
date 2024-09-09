/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.state

import com.google.common.collect.Range
import io.airbyte.cdk.command.DestinationCatalog
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.command.MockCatalogFactory.Companion.stream1
import io.airbyte.cdk.command.MockCatalogFactory.Companion.stream2
import io.airbyte.cdk.message.Batch
import io.airbyte.cdk.message.BatchEnvelope
import io.airbyte.cdk.message.SimpleBatch
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Named
import java.util.concurrent.atomic.AtomicBoolean
import java.util.stream.Stream
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.withTimeout
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtensionContext
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.ArgumentsProvider
import org.junit.jupiter.params.provider.ArgumentsSource

@MicronautTest
class StreamsManagerTest {
    @Inject @Named("mockCatalog") lateinit var catalog: DestinationCatalog

    @Test
    fun testCountRecordsAndCheckpoint() {
        val streamsManager = StreamsManagerFactory(catalog).make()
        val manager1 = streamsManager.getManager(stream1)
        val manager2 = streamsManager.getManager(stream2)

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
    fun testGettingNonexistentManagerFails() {
        val streamsManager = StreamsManagerFactory(catalog).make()
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            streamsManager.getManager(
                DestinationStream(DestinationStream.Descriptor("test", "non-existent"))
            )
        }
    }

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

    @ParameterizedTest
    @ArgumentsSource(TestUpdateBatchStateProvider::class)
    fun testUpdateBatchState(testCase: TestCase) {
        val streamsManager = StreamsManagerFactory(catalog).make()
        testCase.events.forEach { (stream, event) ->
            val manager = streamsManager.getManager(stream)
            when (event) {
                is SetRecordCount -> repeat(event.count.toInt()) { manager.countRecordIn() }
                is SetEndOfStream -> manager.countEndOfStream()
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
        val streamsManager = StreamsManagerFactory(catalog).make()
        val manager = streamsManager.getManager(stream1)

        // Can't close before end-of-stream
        Assertions.assertThrows(IllegalStateException::class.java) { manager.markClosed() }

        manager.countEndOfStream()

        // Can't update after end-of-stream
        Assertions.assertThrows(IllegalStateException::class.java) { manager.countRecordIn() }

        Assertions.assertThrows(IllegalStateException::class.java) { manager.countEndOfStream() }

        // Can close now
        Assertions.assertDoesNotThrow(manager::markClosed)
    }

    @Test
    fun testAwaitStreamClosed() = runTest {
        val streamsManager = StreamsManagerFactory(catalog).make()
        val manager = streamsManager.getManager(stream1)
        val hasClosed = AtomicBoolean(false)

        val job = launch {
            manager.awaitStreamClosed()
            hasClosed.set(true)
        }

        Assertions.assertFalse(hasClosed.get())
        manager.countEndOfStream()
        manager.markClosed()
        try {
            withTimeout(5000) { job.join() }
        } catch (e: Exception) {
            Assertions.fail<Unit>("Stream did not close in time")
        }
        Assertions.assertTrue(hasClosed.get())
    }

    @Test
    fun testAwaitAllStreamsClosed() = runTest {
        val streamsManager = StreamsManagerFactory(catalog).make()
        val manager1 = streamsManager.getManager(stream1)
        val manager2 = streamsManager.getManager(stream2)
        val allHaveClosed = AtomicBoolean(false)

        val awaitStream1 = launch { manager1.awaitStreamClosed() }

        val awaitAllStreams = launch {
            streamsManager.awaitAllStreamsClosed()
            allHaveClosed.set(true)
        }

        Assertions.assertFalse(allHaveClosed.get())
        manager1.countEndOfStream()
        manager1.markClosed()
        try {
            withTimeout(5000) { awaitStream1.join() }
        } catch (e: Exception) {
            Assertions.fail<Unit>("Stream1 did not close in time")
        }
        Assertions.assertFalse(allHaveClosed.get())
        manager2.countEndOfStream()
        manager2.markClosed()
        try {
            withTimeout(5000) { awaitAllStreams.join() }
        } catch (e: Exception) {
            Assertions.fail<Unit>("Streams did not close in time")
        }
        Assertions.assertTrue(allHaveClosed.get())
    }
}
