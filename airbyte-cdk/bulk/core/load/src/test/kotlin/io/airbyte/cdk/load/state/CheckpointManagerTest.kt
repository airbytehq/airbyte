/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import com.google.common.collect.Range
import com.google.common.collect.TreeRangeSet
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory.Companion.stream1
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory.Companion.stream2
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.SimpleBatch
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.util.stream.Stream
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtensionContext
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.ArgumentsProvider
import org.junit.jupiter.params.provider.ArgumentsSource

@MicronautTest(
    rebuildContext = true,
    environments =
        [
            "CheckpointManagerTest",
            "MockDestinationCatalog",
        ]
)
class CheckpointManagerTest {
    @Inject lateinit var checkpointManager: TestCheckpointManager
    @Inject lateinit var syncManager: SyncManager
    /**
     * Test state messages.
     *
     * StateIn: What is passed to the manager. StateOut: What is sent from the manager to the output
     * consumer.
     */
    sealed class MockCheckpoint
    data class MockStreamCheckpoint(val stream: DestinationStream, val payload: Int) :
        MockCheckpoint()
    data class MockGlobalCheckpoint(val payload: Int) : MockCheckpoint()

    @Singleton
    @Requires(env = ["CheckpointManagerTest"])
    class MockOutputConsumer : suspend (MockCheckpoint) -> Unit {
        val collectedStreamOutput =
            mutableMapOf<DestinationStream.Descriptor, MutableList<String>>()
        val collectedGlobalOutput = mutableListOf<String>()
        override suspend fun invoke(t: MockCheckpoint) {
            when (t) {
                is MockStreamCheckpoint ->
                    collectedStreamOutput
                        .getOrPut(t.stream.descriptor) { mutableListOf() }
                        .add(t.payload.toString())
                is MockGlobalCheckpoint -> collectedGlobalOutput.add(t.payload.toString())
            }
        }
    }

    @Singleton
    @Requires(env = ["CheckpointManagerTest"])
    class TestCheckpointManager(
        override val catalog: DestinationCatalog,
        override val syncManager: SyncManager,
        override val outputConsumer: MockOutputConsumer,
        override val timeProvider: TimeProvider,
    ) : StreamsCheckpointManager<MockCheckpoint>() {
        override val checkpointById: Boolean = false
    }

    sealed class TestEvent
    data class TestStreamMessage(val stream: DestinationStream, val index: Long, val message: Int) :
        TestEvent() {
        fun toMockCheckpointIn() = MockStreamCheckpoint(stream, message)
    }
    data class TestGlobalMessage(
        val streamIndexes: List<Pair<DestinationStream.Descriptor, Long>>,
        val message: Int
    ) : TestEvent() {
        fun toMockCheckpointIn() = MockGlobalCheckpoint(message)
    }
    data class FlushPoint(
        val persistedRanges: Map<DestinationStream, List<Range<Long>>> = mapOf()
    ) : TestEvent()

    data class TestCase(
        val name: String,
        val events: List<TestEvent>,
        // Order matters, but only per stream
        val expectedStreamOutput: Map<DestinationStream.Descriptor, List<String>> = mapOf(),
        val expectedGlobalOutput: List<String> = listOf(),
        val expectedException: Class<out Throwable>? = null
    )

    class CheckpointManagerTestArgumentsProvider : ArgumentsProvider {
        override fun provideArguments(context: ExtensionContext?): Stream<out Arguments> {
            return listOf(
                    TestCase(
                        name =
                            "One stream, two stream messages, flush all if all ranges are persisted",
                        events =
                            listOf(
                                TestStreamMessage(stream1, 10L, 1),
                                TestStreamMessage(stream1, 20L, 2),
                                FlushPoint(
                                    persistedRanges =
                                        mapOf(stream1 to listOf(Range.closed(0L, 20L)))
                                )
                            ),
                        expectedStreamOutput = mapOf(stream1.descriptor to listOf("1", "2"))
                    ),
                    TestCase(
                        name = "One stream, two messages, flush only the first",
                        events =
                            listOf(
                                TestStreamMessage(stream1, 10L, 1),
                                TestStreamMessage(stream1, 20L, 2),
                                FlushPoint(
                                    persistedRanges =
                                        mapOf(stream1 to listOf(Range.closed(0L, 10L)))
                                )
                            ),
                        expectedStreamOutput = mapOf(stream1.descriptor to listOf("1"))
                    ),
                    TestCase(
                        name = "Two streams, two messages each, flush all",
                        events =
                            listOf(
                                TestStreamMessage(stream1, 10L, 11),
                                TestStreamMessage(stream2, 30L, 21),
                                TestStreamMessage(stream1, 20L, 12),
                                TestStreamMessage(stream2, 40L, 22),
                                FlushPoint(
                                    persistedRanges =
                                        mapOf(
                                            stream1 to listOf(Range.closed(0L, 20L)),
                                            stream2 to listOf(Range.closed(0L, 40L))
                                        )
                                )
                            ),
                        expectedStreamOutput =
                            mapOf(
                                stream1.descriptor to listOf("11", "12"),
                                stream2.descriptor to listOf("21", "22")
                            )
                    ),
                    TestCase(
                        name = "One stream, only later range persisted",
                        events =
                            listOf(
                                TestStreamMessage(stream1, 10L, 1),
                                TestStreamMessage(stream1, 20L, 2),
                                FlushPoint(
                                    persistedRanges =
                                        mapOf(stream1 to listOf(Range.closed(10L, 20L)))
                                )
                            ),
                        expectedStreamOutput = mapOf()
                    ),
                    TestCase(
                        name = "One stream, out of order (should fail)",
                        events =
                            listOf(
                                TestStreamMessage(stream1, 20L, 2),
                                TestStreamMessage(stream1, 10L, 1),
                                FlushPoint(
                                    persistedRanges =
                                        mapOf(stream1 to listOf(Range.closed(0L, 20L)))
                                )
                            ),
                        expectedException = IllegalStateException::class.java
                    ),
                    TestCase(
                        name = "Global checkpoint, two messages, flush all",
                        events =
                            listOf(
                                TestGlobalMessage(
                                    listOf(stream1.descriptor to 10L, stream2.descriptor to 20L),
                                    1
                                ),
                                TestGlobalMessage(
                                    listOf(stream1.descriptor to 20L, stream2.descriptor to 30L),
                                    2
                                ),
                                FlushPoint(
                                    persistedRanges =
                                        mapOf(
                                            stream1 to listOf(Range.closed(0L, 20L)),
                                            stream2 to listOf(Range.closed(0L, 30L))
                                        )
                                )
                            ),
                        expectedGlobalOutput = listOf("1", "2")
                    ),
                    TestCase(
                        name = "Global checkpoint, two messages, range only covers the first",
                        events =
                            listOf(
                                TestGlobalMessage(
                                    listOf(stream1.descriptor to 10L, stream2.descriptor to 20L),
                                    1
                                ),
                                TestGlobalMessage(
                                    listOf(stream1.descriptor to 20L, stream2.descriptor to 30L),
                                    2
                                ),
                                FlushPoint(
                                    persistedRanges =
                                        mapOf(
                                            stream1 to listOf(Range.closed(0L, 10L)),
                                            stream2 to listOf(Range.closed(0L, 20L))
                                        )
                                )
                            ),
                        expectedGlobalOutput = listOf("1")
                    ),
                    TestCase(
                        name =
                            "Global checkpoint, two messages, where the range only covers *one stream*",
                        events =
                            listOf(
                                TestGlobalMessage(
                                    listOf(stream1.descriptor to 10L, stream2.descriptor to 20L),
                                    1
                                ),
                                TestGlobalMessage(
                                    listOf(stream1.descriptor to 20L, stream2.descriptor to 30L),
                                    2
                                ),
                                FlushPoint(
                                    mapOf(
                                        stream1 to listOf(Range.closed(0L, 20L)),
                                        stream2 to listOf(Range.closed(0L, 20L))
                                    )
                                )
                            ),
                        expectedGlobalOutput = listOf("1")
                    ),
                    TestCase(
                        name = "Global checkpoint, out of order (should fail)",
                        events =
                            listOf(
                                TestGlobalMessage(
                                    listOf(stream1.descriptor to 20L, stream2.descriptor to 30L),
                                    2
                                ),
                                TestGlobalMessage(
                                    listOf(stream1.descriptor to 10L, stream2.descriptor to 20L),
                                    1
                                ),
                                FlushPoint(
                                    mapOf(
                                        stream1 to listOf(Range.closed(0L, 20L)),
                                        stream2 to listOf(Range.closed(0L, 30L))
                                    )
                                ),
                            ),
                        expectedException = IllegalStateException::class.java
                    ),
                    TestCase(
                        name = "Mixed: first stream checkpoint, then global (should fail)",
                        events =
                            listOf(
                                TestStreamMessage(stream1, 10L, 1),
                                TestGlobalMessage(
                                    listOf(stream1.descriptor to 20L, stream2.descriptor to 30L),
                                    2
                                ),
                                FlushPoint(
                                    mapOf(
                                        stream1 to listOf(Range.closed(0L, 20L)),
                                        stream2 to listOf(Range.closed(0L, 30L))
                                    )
                                )
                            ),
                        expectedException = IllegalStateException::class.java
                    ),
                    TestCase(
                        name = "Mixed: first global, then stream checkpoint (should fail)",
                        events =
                            listOf(
                                TestGlobalMessage(
                                    listOf(stream1.descriptor to 10L, stream2.descriptor to 20L),
                                    1
                                ),
                                TestStreamMessage(stream1, 20L, 2),
                                FlushPoint(
                                    persistedRanges =
                                        mapOf(
                                            stream1 to listOf(Range.closed(0L, 20L)),
                                            stream2 to listOf(Range.closed(0L, 30L))
                                        )
                                )
                            ),
                        expectedException = IllegalStateException::class.java
                    ),
                    TestCase(
                        name = "No messages, just a flush",
                        events = listOf(FlushPoint()),
                        expectedStreamOutput = mapOf(),
                        expectedGlobalOutput = listOf()
                    ),
                    TestCase(
                        name = "Two stream messages, flush against empty ranges",
                        events =
                            listOf(
                                TestStreamMessage(stream1, 10L, 1),
                                TestStreamMessage(stream1, 20L, 2),
                                FlushPoint()
                            ),
                        expectedStreamOutput = mapOf()
                    ),
                    TestCase(
                        name = "Stream checkpoint, multiple flush points",
                        events =
                            listOf(
                                TestStreamMessage(stream1, 10L, 1),
                                FlushPoint(),
                                TestStreamMessage(stream1, 20L, 2),
                                FlushPoint(mapOf(stream1 to listOf(Range.closed(0L, 10L)))),
                                TestStreamMessage(stream1, 30L, 3),
                                FlushPoint(mapOf(stream1 to listOf(Range.closed(10L, 30L))))
                            ),
                        expectedStreamOutput = mapOf(stream1.descriptor to listOf("1", "2", "3"))
                    ),
                    TestCase(
                        name = "Global checkpoint, multiple flush points, no output",
                        events =
                            listOf(
                                TestGlobalMessage(
                                    listOf(stream1.descriptor to 10L, stream2.descriptor to 20L),
                                    1
                                ),
                                FlushPoint(),
                                TestGlobalMessage(
                                    listOf(stream1.descriptor to 20L, stream2.descriptor to 30L),
                                    2
                                ),
                                FlushPoint(
                                    mapOf(
                                        stream1 to listOf(Range.closed(0L, 20L)),
                                    )
                                ),
                                TestGlobalMessage(
                                    listOf(stream1.descriptor to 30L, stream2.descriptor to 40L),
                                    3
                                ),
                                FlushPoint(mapOf(stream2 to listOf(Range.closed(20L, 30L))))
                            ),
                        expectedGlobalOutput = listOf()
                    ),
                    TestCase(
                        name = "Global checkpoint, multiple flush points, no output until end",
                        events =
                            listOf(
                                TestGlobalMessage(
                                    listOf(stream1.descriptor to 10L, stream2.descriptor to 20L),
                                    1
                                ),
                                FlushPoint(),
                                TestGlobalMessage(
                                    listOf(stream1.descriptor to 20L, stream2.descriptor to 30L),
                                    2
                                ),
                                FlushPoint(
                                    mapOf(
                                        stream1 to listOf(Range.closed(0L, 20L)),
                                    )
                                ),
                                TestGlobalMessage(
                                    listOf(stream1.descriptor to 30L, stream2.descriptor to 40L),
                                    3
                                ),
                                FlushPoint(
                                    mapOf(
                                        stream1 to listOf(Range.closed(20L, 30L)),
                                        stream2 to listOf(Range.closed(0L, 40L))
                                    )
                                )
                            ),
                        expectedGlobalOutput = listOf("1", "2", "3")
                    )
                )
                .stream()
                .map { Arguments.of(it) }
        }
    }

    @ParameterizedTest
    @ArgumentsSource(CheckpointManagerTestArgumentsProvider::class)
    fun testAddingAndFlushingCheckpoints(testCase: TestCase) = runTest {
        if (testCase.expectedException != null) {
            try {
                runTestCase(testCase)
                Assertions.fail<Unit>("Expected exception ${testCase.expectedException}")
            } catch (e: Throwable) {
                Assertions.assertEquals(testCase.expectedException, e::class.java)
            }
        } else {
            runTestCase(testCase)
            Assertions.assertEquals(
                testCase.expectedStreamOutput,
                checkpointManager.outputConsumer.collectedStreamOutput,
                testCase.name
            )
            Assertions.assertEquals(
                testCase.expectedGlobalOutput,
                checkpointManager.outputConsumer.collectedGlobalOutput,
                testCase.name
            )
        }
    }

    private suspend fun runTestCase(testCase: TestCase) {
        testCase.events.forEach {
            when (it) {
                is TestStreamMessage -> {
                    /**
                     * Mock the correct state of the stream manager by advancing the record count to
                     * the index of the message.
                     */
                    val streamManager = syncManager.getStreamManager(it.stream.descriptor)
                    val recordCount = streamManager.readCount()
                    (recordCount until it.index).forEach { _ ->
                        syncManager.getStreamManager(it.stream.descriptor).incrementReadCount()
                    }
                    checkpointManager.addStreamCheckpoint(
                        it.stream.descriptor,
                        it.index,
                        it.toMockCheckpointIn()
                    )
                }
                is TestGlobalMessage -> {
                    checkpointManager.addGlobalCheckpoint(it.streamIndexes, it.toMockCheckpointIn())
                }
                is FlushPoint -> {
                    // Mock the persisted ranges by updating the state of the stream managers
                    it.persistedRanges.forEach { (stream, ranges) ->
                        val mockBatch = SimpleBatch(state = Batch.State.PERSISTED)
                        val rangeSet = TreeRangeSet.create(ranges)
                        val mockBatchEnvelope =
                            BatchEnvelope(
                                batch = mockBatch,
                                ranges = rangeSet,
                                streamDescriptor = stream.descriptor
                            )
                        syncManager
                            .getStreamManager(stream.descriptor)
                            .updateBatchState(mockBatchEnvelope)
                    }
                    checkpointManager.flushReadyCheckpointMessages()
                }
            }
        }
    }

    @Test
    fun testGetLastFlushTimeMs() = runTest {
        val startTime = System.currentTimeMillis()
        checkpointManager.addStreamCheckpoint(
            stream1.descriptor,
            1L,
            MockStreamCheckpoint(stream1, 1)
        )
        syncManager.markPersisted(stream1, Range.closed(0L, 1L))
        Assertions.assertTrue(startTime >= checkpointManager.getLastSuccessfulFlushTimeMs())
        checkpointManager.flushReadyCheckpointMessages()
        Assertions.assertTrue(startTime < checkpointManager.getLastSuccessfulFlushTimeMs())
    }

    @Test
    fun testGetNextStreamCheckpoints() = runTest {
        Assertions.assertEquals(
            emptyMap<DestinationStream.Descriptor, Long>(),
            checkpointManager.getNextCheckpointIndexes()
        )

        checkpointManager.addStreamCheckpoint(
            stream1.descriptor,
            1L,
            MockStreamCheckpoint(stream1, 1)
        )
        Assertions.assertEquals(
            mapOf(stream1.descriptor to 1L),
            checkpointManager.getNextCheckpointIndexes()
        )

        checkpointManager.addStreamCheckpoint(
            stream2.descriptor,
            10L,
            MockStreamCheckpoint(stream2, 10)
        )
        Assertions.assertEquals(
            mapOf(stream1.descriptor to 1L, stream2.descriptor to 10L),
            checkpointManager.getNextCheckpointIndexes()
        )

        checkpointManager.addStreamCheckpoint(
            stream1.descriptor,
            2L,
            MockStreamCheckpoint(stream1, 2)
        )
        Assertions.assertEquals(
            mapOf(stream1.descriptor to 1L, stream2.descriptor to 10L),
            checkpointManager.getNextCheckpointIndexes(),
            "only the first checkpoint is returned"
        )

        syncManager.markPersisted(stream1, Range.singleton(0))
        Assertions.assertEquals(
            mapOf(stream1.descriptor to 1L, stream2.descriptor to 10L),
            checkpointManager.getNextCheckpointIndexes(),
            "marking persisted is not sufficient"
        )

        checkpointManager.flushReadyCheckpointMessages()
        Assertions.assertEquals(
            mapOf(stream1.descriptor to 2L, stream2.descriptor to 10L),
            checkpointManager.getNextCheckpointIndexes(),
            "flushing the first checkpoint reveals the second one"
        )

        checkpointManager.addStreamCheckpoint(
            stream2.descriptor,
            20L,
            MockStreamCheckpoint(stream2, 20)
        )
        checkpointManager.flushReadyCheckpointMessages()
        Assertions.assertEquals(
            mapOf(stream1.descriptor to 2L, stream2.descriptor to 10L),
            checkpointManager.getNextCheckpointIndexes(),
            "but only on the stream that was flushed"
        )

        syncManager.markPersisted(stream2, Range.closed(0L, 19L))
        checkpointManager.flushReadyCheckpointMessages()
        Assertions.assertEquals(
            mapOf(stream1.descriptor to 2L),
            checkpointManager.getNextCheckpointIndexes(),
            "flushing all the checkpoints clears the stream from the map"
        )

        syncManager.markPersisted(stream1, Range.singleton(1))
        checkpointManager.flushReadyCheckpointMessages()
        Assertions.assertEquals(
            emptyMap<DestinationStream.Descriptor, Long>(),
            checkpointManager.getNextCheckpointIndexes(),
            "flushing all the checkpoints clears the map"
        )
    }

    @Test
    fun testGetNextGlobalCheckpoints() = runTest {
        Assertions.assertEquals(
            emptyMap<DestinationStream.Descriptor, Long>(),
            checkpointManager.getNextCheckpointIndexes()
        )

        checkpointManager.addGlobalCheckpoint(
            listOf(stream1.descriptor to 1L, stream2.descriptor to 10L),
            MockGlobalCheckpoint(1)
        )
        Assertions.assertEquals(
            mapOf(stream1.descriptor to 1L, stream2.descriptor to 10L),
            checkpointManager.getNextCheckpointIndexes()
        )

        checkpointManager.addGlobalCheckpoint(
            listOf(stream1.descriptor to 2L, stream2.descriptor to 20L),
            MockGlobalCheckpoint(2)
        )
        Assertions.assertEquals(
            mapOf(stream1.descriptor to 1L, stream2.descriptor to 10L),
            checkpointManager.getNextCheckpointIndexes(),
            "only the first checkpoint is returned"
        )

        syncManager.markPersisted(stream1, Range.singleton(0))
        checkpointManager.flushReadyCheckpointMessages()
        Assertions.assertEquals(
            mapOf(stream1.descriptor to 1L, stream2.descriptor to 10L),
            checkpointManager.getNextCheckpointIndexes(),
            "if only 1 stream is persisted, neither are returned"
        )

        syncManager.markPersisted(stream2, Range.closed(0L, 19L))
        checkpointManager.flushReadyCheckpointMessages()
        Assertions.assertEquals(
            mapOf(stream1.descriptor to 2L, stream2.descriptor to 20L),
            checkpointManager.getNextCheckpointIndexes(),
            "persisting the second stream triggers both to flush, revealing the next pair"
        )

        syncManager.markPersisted(stream1, Range.singleton(1))
        checkpointManager.flushReadyCheckpointMessages()
        Assertions.assertEquals(
            emptyMap<DestinationStream.Descriptor, Long>(),
            checkpointManager.getNextCheckpointIndexes(),
            "flushing all the checkpoints clears the map"
        )
    }
}
