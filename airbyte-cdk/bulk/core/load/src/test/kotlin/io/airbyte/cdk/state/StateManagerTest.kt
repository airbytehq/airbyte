/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.state

import com.google.common.collect.Range
import com.google.common.collect.RangeSet
import com.google.common.collect.TreeRangeSet
import io.airbyte.cdk.command.DestinationCatalog
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.command.MockCatalogFactory.Companion.stream1
import io.airbyte.cdk.command.MockCatalogFactory.Companion.stream2
import io.airbyte.cdk.message.Batch
import io.airbyte.cdk.message.BatchEnvelope
import io.airbyte.cdk.message.MessageConverter
import io.micronaut.context.annotation.Prototype
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.util.function.Consumer
import java.util.stream.Stream
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.extension.ExtensionContext
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.ArgumentsProvider
import org.junit.jupiter.params.provider.ArgumentsSource

@MicronautTest(environments = ["StateManagerTest"])
class StateManagerTest {
    @Inject lateinit var stateManager: TestStateManager

    /**
     * Test state messages.
     *
     * StateIn: What is passed to the manager. StateOut: What is sent from the manager to the output
     * consumer.
     */
    sealed class MockStateIn
    data class MockStreamStateIn(val stream: DestinationStream, val payload: Int) : MockStateIn()
    data class MockGlobalStateIn(val payload: Int) : MockStateIn()

    sealed class MockStateOut
    data class MockStreamStateOut(val stream: DestinationStream, val payload: String) :
        MockStateOut()
    data class MockGlobalStateOut(val payload: String) : MockStateOut()

    @Singleton
    class MockStateMessageFactory : MessageConverter<MockStateIn, MockStateOut> {
        override fun from(message: MockStateIn): MockStateOut {
            return when (message) {
                is MockStreamStateIn ->
                    MockStreamStateOut(message.stream, message.payload.toString())
                is MockGlobalStateIn -> MockGlobalStateOut(message.payload.toString())
            }
        }
    }

    @Prototype
    class MockOutputConsumer : Consumer<MockStateOut> {
        val collectedStreamOutput = mutableMapOf<DestinationStream, MutableList<String>>()
        val collectedGlobalOutput = mutableListOf<String>()
        override fun accept(t: MockStateOut) {
            when (t) {
                is MockStreamStateOut ->
                    collectedStreamOutput.getOrPut(t.stream) { mutableListOf() }.add(t.payload)
                is MockGlobalStateOut -> collectedGlobalOutput.add(t.payload)
            }
        }
    }

    /**
     * The only thing we really need is `areRecordsPersistedUntil`. (Technically we're emulating the
     * @[StreamManager] behavior here, since the state manager doesn't actually know what ranges are
     * closed, but less than that would make the test unrealistic.)
     */
    class MockStreamManager : StreamManager {
        var persistedRanges: RangeSet<Long> = TreeRangeSet.create()

        override fun countRecordIn(): Long {
            throw NotImplementedError()
        }

        override fun countEndOfStream(): Long {
            throw NotImplementedError()
        }

        override fun markCheckpoint(): Pair<Long, Long> {
            throw NotImplementedError()
        }

        override fun <B : Batch> updateBatchState(batch: BatchEnvelope<B>) {
            throw NotImplementedError()
        }

        override fun isBatchProcessingComplete(): Boolean {
            throw NotImplementedError()
        }

        override fun areRecordsPersistedUntil(index: Long): Boolean {
            return persistedRanges.encloses(Range.closedOpen(0, index))
        }

        override fun markClosed() {
            throw NotImplementedError()
        }

        override fun streamIsClosed(): Boolean {
            throw NotImplementedError()
        }

        override suspend fun awaitStreamClosed() {
            throw NotImplementedError()
        }
    }

    @Prototype
    @Requires(env = ["StateManagerTest"])
    class MockStreamsManager(@Named("mockCatalog") catalog: DestinationCatalog) : StreamsManager {
        private val mockManagers = catalog.streams.associateWith { MockStreamManager() }

        fun addPersistedRanges(stream: DestinationStream, ranges: List<Range<Long>>) {
            mockManagers[stream]!!.persistedRanges.addAll(ranges)
        }

        override fun getManager(stream: DestinationStream): StreamManager {
            return mockManagers[stream]
                ?: throw IllegalArgumentException("Stream not found: $stream")
        }

        override suspend fun awaitAllStreamsClosed() {
            throw NotImplementedError()
        }
    }

    @Prototype
    class TestStateManager(
        @Named("mockCatalog") override val catalog: DestinationCatalog,
        override val streamsManager: MockStreamsManager,
        override val outputFactory: MessageConverter<MockStateIn, MockStateOut>,
        override val outputConsumer: MockOutputConsumer
    ) : StreamsStateManager<MockStateIn, MockStateOut>()

    sealed class TestEvent
    data class TestStreamMessage(val stream: DestinationStream, val index: Long, val message: Int) :
        TestEvent() {
        fun toMockStateIn() = MockStreamStateIn(stream, message)
    }
    data class TestGlobalMessage(
        val streamIndexes: List<Pair<DestinationStream, Long>>,
        val message: Int
    ) : TestEvent() {
        fun toMockStateIn() = MockGlobalStateIn(message)
    }
    data class FlushPoint(
        val persistedRanges: Map<DestinationStream, List<Range<Long>>> = mapOf()
    ) : TestEvent()

    data class TestCase(
        val name: String,
        val events: List<TestEvent>,
        // Order matters, but only per stream
        val expectedStreamOutput: Map<DestinationStream, List<String>> = mapOf(),
        val expectedGlobalOutput: List<String> = listOf(),
        val expectedException: Class<out Throwable>? = null
    )

    class StateManagerTestArgumentsProvider : ArgumentsProvider {
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
                        expectedStreamOutput = mapOf(stream1 to listOf("1", "2"))
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
                        expectedStreamOutput = mapOf(stream1 to listOf("1"))
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
                            mapOf(stream1 to listOf("11", "12"), stream2 to listOf("22", "21"))
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
                        name = "Global state, two messages, flush all",
                        events =
                            listOf(
                                TestGlobalMessage(listOf(stream1 to 10L, stream2 to 20L), 1),
                                TestGlobalMessage(listOf(stream1 to 20L, stream2 to 30L), 2),
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
                        name = "Global state, two messages, range only covers the first",
                        events =
                            listOf(
                                TestGlobalMessage(listOf(stream1 to 10L, stream2 to 20L), 1),
                                TestGlobalMessage(listOf(stream1 to 20L, stream2 to 30L), 2),
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
                            "Global state, two messages, where the range only covers *one stream*",
                        events =
                            listOf(
                                TestGlobalMessage(listOf(stream1 to 10L, stream2 to 20L), 1),
                                TestGlobalMessage(listOf(stream1 to 20L, stream2 to 30L), 2),
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
                        name = "Global state, out of order (should fail)",
                        events =
                            listOf(
                                TestGlobalMessage(listOf(stream1 to 20L, stream2 to 30L), 2),
                                TestGlobalMessage(listOf(stream1 to 10L, stream2 to 20L), 1),
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
                        name = "Mixed: first stream state, then global (should fail)",
                        events =
                            listOf(
                                TestStreamMessage(stream1, 10L, 1),
                                TestGlobalMessage(listOf(stream1 to 20L, stream2 to 30L), 2),
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
                        name = "Mixed: first global, then stream state (should fail)",
                        events =
                            listOf(
                                TestGlobalMessage(listOf(stream1 to 10L, stream2 to 20L), 1),
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
                        name = "Stream state, multiple flush points",
                        events =
                            listOf(
                                TestStreamMessage(stream1, 10L, 1),
                                FlushPoint(),
                                TestStreamMessage(stream1, 20L, 2),
                                FlushPoint(mapOf(stream1 to listOf(Range.closed(0L, 10L)))),
                                TestStreamMessage(stream1, 30L, 3),
                                FlushPoint(mapOf(stream1 to listOf(Range.closed(10L, 30L))))
                            ),
                        expectedStreamOutput = mapOf(stream1 to listOf("1", "2", "3"))
                    ),
                    TestCase(
                        name = "Global state, multiple flush points, no output",
                        events =
                            listOf(
                                TestGlobalMessage(listOf(stream1 to 10L, stream2 to 20L), 1),
                                FlushPoint(),
                                TestGlobalMessage(listOf(stream1 to 20L, stream2 to 30L), 2),
                                FlushPoint(
                                    mapOf(
                                        stream1 to listOf(Range.closed(0L, 20L)),
                                    )
                                ),
                                TestGlobalMessage(listOf(stream1 to 30L, stream2 to 40L), 3),
                                FlushPoint(mapOf(stream2 to listOf(Range.closed(20L, 30L))))
                            ),
                        expectedGlobalOutput = listOf()
                    ),
                    TestCase(
                        name = "Global state, multiple flush points, no output until end",
                        events =
                            listOf(
                                TestGlobalMessage(listOf(stream1 to 10L, stream2 to 20L), 1),
                                FlushPoint(),
                                TestGlobalMessage(listOf(stream1 to 20L, stream2 to 30L), 2),
                                FlushPoint(
                                    mapOf(
                                        stream1 to listOf(Range.closed(0L, 20L)),
                                    )
                                ),
                                TestGlobalMessage(listOf(stream1 to 30L, stream2 to 40L), 3),
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
    @ArgumentsSource(StateManagerTestArgumentsProvider::class)
    fun testAddingAndFlushingState(testCase: TestCase) {
        if (testCase.expectedException != null) {
            Assertions.assertThrows(testCase.expectedException) { runTestCase(testCase) }
        } else {
            runTestCase(testCase)
            Assertions.assertEquals(
                testCase.expectedStreamOutput,
                stateManager.outputConsumer.collectedStreamOutput,
                testCase.name
            )
            Assertions.assertEquals(
                testCase.expectedGlobalOutput,
                stateManager.outputConsumer.collectedGlobalOutput,
                testCase.name
            )
        }
    }

    private fun runTestCase(testCase: TestCase) {
        testCase.events.forEach {
            when (it) {
                is TestStreamMessage -> {
                    stateManager.addStreamState(it.stream, it.index, it.toMockStateIn())
                }
                is TestGlobalMessage -> {
                    stateManager.addGlobalState(it.streamIndexes, it.toMockStateIn())
                }
                is FlushPoint -> {
                    it.persistedRanges.forEach { (stream, ranges) ->
                        stateManager.streamsManager.addPersistedRanges(stream, ranges)
                    }
                    stateManager.flushStates()
                }
            }
        }
    }
}
