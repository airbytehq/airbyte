/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.state

import com.google.common.collect.Range
import io.airbyte.cdk.command.DestinationCatalog
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.command.MockCatalogFactory.Companion.stream1
import io.airbyte.cdk.command.MockCatalogFactory.Companion.stream2
import io.airbyte.cdk.message.MessageConverter
import io.airbyte.cdk.message.MockStreamsManager
import io.micronaut.context.annotation.Prototype
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.util.function.Consumer
import java.util.stream.Stream
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.extension.ExtensionContext
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.ArgumentsProvider
import org.junit.jupiter.params.provider.ArgumentsSource

@MicronautTest(environments = ["MockStreamsManager"])
class CheckpointManagerTest {
    @Inject lateinit var checkpointManager: TestCheckpointManager
    /**
     * Test state messages.
     *
     * StateIn: What is passed to the manager. StateOut: What is sent from the manager to the output
     * consumer.
     */
    sealed class MockCheckpointIn
    data class MockStreamCheckpointIn(val stream: DestinationStream, val payload: Int) :
        MockCheckpointIn()
    data class MockGlobalCheckpointIn(val payload: Int) : MockCheckpointIn()

    sealed class MockCheckpointOut
    data class MockStreamCheckpointOut(val stream: DestinationStream, val payload: String) :
        MockCheckpointOut()
    data class MockGlobalCheckpointOut(val payload: String) : MockCheckpointOut()

    @Singleton
    class MockStateMessageFactory : MessageConverter<MockCheckpointIn, MockCheckpointOut> {
        override fun from(message: MockCheckpointIn): MockCheckpointOut {
            return when (message) {
                is MockStreamCheckpointIn ->
                    MockStreamCheckpointOut(message.stream, message.payload.toString())
                is MockGlobalCheckpointIn -> MockGlobalCheckpointOut(message.payload.toString())
            }
        }
    }

    @Prototype
    class MockOutputConsumer : Consumer<MockCheckpointOut> {
        val collectedStreamOutput = mutableMapOf<DestinationStream, MutableList<String>>()
        val collectedGlobalOutput = mutableListOf<String>()
        override fun accept(t: MockCheckpointOut) {
            when (t) {
                is MockStreamCheckpointOut ->
                    collectedStreamOutput.getOrPut(t.stream) { mutableListOf() }.add(t.payload)
                is MockGlobalCheckpointOut -> collectedGlobalOutput.add(t.payload)
            }
        }
    }

    @Prototype
    class TestCheckpointManager(
        @Named("mockCatalog") override val catalog: DestinationCatalog,
        override val streamsManager: MockStreamsManager,
        override val outputFactory: MessageConverter<MockCheckpointIn, MockCheckpointOut>,
        override val outputConsumer: MockOutputConsumer
    ) : StreamsCheckpointManager<MockCheckpointIn, MockCheckpointOut>()

    sealed class TestEvent
    data class TestStreamMessage(val stream: DestinationStream, val index: Long, val message: Int) :
        TestEvent() {
        fun toMockCheckpointIn() = MockStreamCheckpointIn(stream, message)
    }
    data class TestGlobalMessage(
        val streamIndexes: List<Pair<DestinationStream, Long>>,
        val message: Int
    ) : TestEvent() {
        fun toMockCheckpointIn() = MockGlobalCheckpointIn(message)
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
                        name = "Global checkpoint, two messages, flush all",
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
                        name = "Global checkpoint, two messages, range only covers the first",
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
                            "Global checkpoint, two messages, where the range only covers *one stream*",
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
                        name = "Global checkpoint, out of order (should fail)",
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
                        name = "Mixed: first stream checkpoint, then global (should fail)",
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
                        name = "Mixed: first global, then stream checkpoint (should fail)",
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
                        expectedStreamOutput = mapOf(stream1 to listOf("1", "2", "3"))
                    ),
                    TestCase(
                        name = "Global checkpoint, multiple flush points, no output",
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
                        name = "Global checkpoint, multiple flush points, no output until end",
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
    @ArgumentsSource(CheckpointManagerTestArgumentsProvider::class)
    suspend fun testAddingAndFlushingCheckpoints(testCase: TestCase) = runTest {
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
                    checkpointManager.addStreamCheckpoint(
                        it.stream,
                        it.index,
                        it.toMockCheckpointIn()
                    )
                }
                is TestGlobalMessage -> {
                    checkpointManager.addGlobalCheckpoint(it.streamIndexes, it.toMockCheckpointIn())
                }
                is FlushPoint -> {
                    it.persistedRanges.forEach { (stream, ranges) ->
                        checkpointManager.streamsManager.addPersistedRanges(stream, ranges)
                    }
                    checkpointManager.flushReadyCheckpointMessages()
                }
            }
        }
    }
}
