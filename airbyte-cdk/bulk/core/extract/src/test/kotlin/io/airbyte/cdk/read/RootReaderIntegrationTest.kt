/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.SyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.lang.RuntimeException
import java.time.Duration
import kotlin.random.Random
import kotlin.time.toKotlinDuration
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.sync.Semaphore
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.DynamicNode
import org.junit.jupiter.api.DynamicTest
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestFactory
import org.junit.jupiter.api.Timeout

const val TEST_TIMEOUT_SECONDS = 10L

@Timeout(TEST_TIMEOUT_SECONDS)
class RootReaderIntegrationTest {
    val testCases: List<TestCase> =
        listOf(
            TestCase(
                "simple-1",
                Create(Read),
                Create(),
            ),
            TestCase(
                "simple-3",
                Create(Read, Read, Read),
                Create(),
            ),
            TestCase(
                "simple-3-2",
                Create(Read, Read, Read),
                Create(Read, Read),
                Create(),
            ),
            TestCase(
                "backoff-1",
                CreatorBackOff(Create(Read)),
                CreatorBackOff(CreatorBackOff(Create())),
            ),
            TestCase(
                "backoff-2",
                Create(ReaderBackOff(ReaderBackOff(Read)), ReaderBackOff(Read)),
                Create(),
            ),
            TestCase(
                "failure-1-c",
                Create(Read),
                CreatorFailure,
            ),
            TestCase(
                "failure-1-1r",
                Create(Read),
                Create(ReaderFailure),
            ),
            TestCase(
                "failure-2-2r",
                Create(Read, Read),
                Create(ReaderFailure, Read),
            ),
            TestCase(
                "failure-2-3r",
                Create(Read, Read),
                Create(Read, ReaderFailure, Read),
            ),
        )

    /** Simulates a READ operation for each test case, which corresponds to a one-stream catalog. */
    @TestFactory
    fun testConcurrent(): Iterable<DynamicNode> =
        testCases.map { DynamicTest.dynamicTest(it.name, it::run) }

    /** Similar to [testConcurrent] but with a resource which forces serial execution. */
    @TestFactory
    fun testSerial(): Iterable<DynamicNode> =
        testCases.map { it.copy(resource = 1) }.map { DynamicTest.dynamicTest(it.name, it::run) }

    /**
     * Similar to [testConcurrent] but with a resource which forces execution on at most 2 threads.
     */
    @TestFactory
    fun testConstrained(): Iterable<DynamicNode> =
        testCases
            .map { it.copy(resource = CONSTRAINED) }
            .map { DynamicTest.dynamicTest(it.name, it::run) }

    /**
     * Simulates a READ operation with a catalog with all the streams in [testCases]. Some of these
     * fail, so this test checks that a failure in one stream propagates to the others properly.
     */
    @Test
    fun testAllStreamsNonGlobal() {
        val stateManager =
            StateManager(initialStreamStates = testCases.associate { it.stream to null })
        val testOutputConsumer = BufferingOutputConsumer(ClockFactory().fixed())
        val rootReader =
            RootReader(
                stateManager,
                slowHeartbeat,
                excessiveTimeout,
                testOutputConsumer,
                TestPartitionsCreatorFactory(Semaphore(CONSTRAINED), *testCases.toTypedArray()),
            )
        Assertions.assertThrows(RuntimeException::class.java) {
            runBlocking(Dispatchers.Default) { rootReader.read() }
        }
        val log = KotlinLogging.logger {}
        for (msg in testOutputConsumer.messages()) {
            log.info { Jsons.writeValueAsString(msg) }
        }
        for (testCase in testCases) {
            log.info { "checking stream feed for ${testCase.name}" }
            val traceMessages: List<AirbyteTraceMessage> =
                testOutputConsumer.traces().filter {
                    it.streamStatus.streamDescriptor.name == testCase.name
                }
            testCase.verifyTraces(traceMessages)
            val stateMessages: List<AirbyteStateMessage> =
                testOutputConsumer.states().filter {
                    it.stream.streamDescriptor.name == testCase.name
                }
            testCase.verifyStates(stateMessages)
        }
    }

    /**
     * Similar to [testAllStreamsNonGlobal] but with a global feed. This test checks that the global
     * feed gets cancelled when one of its stream feeds fails. Otherwise, the test times out.
     */
    @Test
    fun testAllStreamsGlobal() {
        val stateManager =
            StateManager(
                global = Global(testCases.map { it.stream }),
                initialGlobalState = null,
                initialStreamStates = testCases.associate { it.stream to null },
            )
        val testOutputConsumer = BufferingOutputConsumer(ClockFactory().fixed())
        val rootReader =
            RootReader(
                stateManager,
                slowHeartbeat,
                excessiveTimeout,
                testOutputConsumer,
                TestPartitionsCreatorFactory(Semaphore(CONSTRAINED), *testCases.toTypedArray()),
            )
        Assertions.assertThrows(RuntimeException::class.java) {
            runBlocking(Dispatchers.Default) { rootReader.read() }
        }
        val log = KotlinLogging.logger {}
        for (msg in testOutputConsumer.messages()) {
            log.info { Jsons.writeValueAsString(msg) }
        }
        for (testCase in testCases) {
            log.info { "checking stream feed for ${testCase.name}" }
            val traceMessages: List<AirbyteTraceMessage> =
                testOutputConsumer.traces().filter {
                    it.streamStatus.streamDescriptor.name == testCase.name
                }
            testCase.verifyTraces(traceMessages)
            val streamStateMessages: List<AirbyteStateMessage> =
                testOutputConsumer.states().filter {
                    it.stream?.streamDescriptor?.name == testCase.name
                }
            Assertions.assertTrue(streamStateMessages.isEmpty())
        }
        log.info { "checking global feed" }
        val globalStateMessages: List<AirbyteStateMessage> =
            testOutputConsumer.states().filter {
                it.type == AirbyteStateMessage.AirbyteStateType.GLOBAL
            }
        Assertions.assertFalse(globalStateMessages.isEmpty())
    }

    companion object {
        const val CONSTRAINED = 2
    }
}

/** Each [TestCase] encodes a scenario for how a READ operation might proceed for a [Stream]. */
data class TestCase(
    val name: String,
    val creatorCases: List<CreatorCase>,
    val resource: Int = 100_000, // some arbitrary large value by default
) {
    constructor(
        name: String,
        vararg creatorCases: CreatorCase,
    ) : this(name, creatorCases.toList())

    val stream: Stream =
        Stream(
            name = name,
            namespace = "test",
            fields = listOf(),
            configuredSyncMode = SyncMode.FULL_REFRESH,
            configuredPrimaryKey = null,
            configuredCursor = null,
        )

    fun run() {
        val testOutputConsumer = BufferingOutputConsumer(ClockFactory().fixed())
        val rootReader =
            RootReader(
                StateManager(initialStreamStates = mapOf(stream to null)),
                slowHeartbeat,
                excessiveTimeout,
                testOutputConsumer,
                TestPartitionsCreatorFactory(Semaphore(resource), this),
            )
        try {
            runBlocking(Dispatchers.Default) { rootReader.read() }
            log.info { "read completed for $name" }
            Assertions.assertTrue(isSuccessful, name)
        } catch (e: Exception) {
            Assertions.assertFalse(isSuccessful, name)
            log.info(e) { "read failed for $name" }
        }
        for (msg in testOutputConsumer.messages()) {
            log.info { Jsons.writeValueAsString(msg) }
        }
        verify(testOutputConsumer)
    }

    private val log = KotlinLogging.logger {}

    fun verify(output: BufferingOutputConsumer) {
        var inTracePrefix = true
        var inTraceSuffix = false
        for (msg in output.messages()) {
            val json: String by lazy { Jsons.writeValueAsString(msg) }
            when (msg.type) {
                AirbyteMessage.Type.TRACE ->
                    if (!inTracePrefix && !inTraceSuffix) inTraceSuffix = true
                AirbyteMessage.Type.STATE -> {
                    if (inTracePrefix) inTracePrefix = false
                    Assertions.assertFalse(
                        inTraceSuffix,
                        "unexpected STATE message $json in case $name",
                    )
                }
                else ->
                    Assertions.fail(
                        "Unexpected Airbyte message type ${msg.type} in $json in case $name",
                    )
            }
        }
        verifyTraces(output.traces())
        verifyStates(output.states())
    }

    fun verifyTraces(traceMessages: List<AirbyteTraceMessage>) {
        var hasStarted = false
        var hasCompleted = false
        for (trace in traceMessages) {
            when (trace.type) {
                AirbyteTraceMessage.Type.STREAM_STATUS -> {
                    Assertions.assertEquals(name, trace.streamStatus?.streamDescriptor?.name)
                    when (trace.streamStatus.status) {
                        AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.STARTED -> {
                            hasStarted = true
                            Assertions.assertFalse(hasCompleted)
                        }
                        AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE -> {
                            hasCompleted = true
                            Assertions.assertTrue(hasStarted)
                        }
                        else ->
                            Assertions.fail(
                                "unexpected TRACE message status ${trace.streamStatus.status} " +
                                    "in case $name",
                            )
                    }
                }
                else ->
                    Assertions.fail(
                        "unexpected TRACE message type ${trace.type} in case $name",
                    )
            }
        }
        Assertions.assertTrue(hasStarted)
        Assertions.assertEquals(isSuccessful, hasCompleted)
    }

    fun verifyStates(stateMessages: List<AirbyteStateMessage>) {
        val actualStates = mutableListOf<MutableSet<JsonNode>>()
        var previousPartitionsCreatorID: Long = -1L
        for (stateMessage in stateMessages) {
            Assertions.assertEquals(name, stateMessage.stream?.streamDescriptor?.name)
            Assertions.assertEquals(true, stateMessage.stream?.streamState?.isArray, name)
            val stateValue: ArrayNode = stateMessage.stream.streamState as ArrayNode
            val currentID: Long = stateValue.get(0)?.asLong()!!
            if (currentID == previousPartitionsCreatorID) {
                actualStates.last().add(stateValue)
            } else {
                actualStates.add(mutableSetOf(stateValue))
                previousPartitionsCreatorID = currentID
            }
        }
        log.info { "actual states for $name: $actualStates" }
        // Compare expected and actual states.
        // Actual states are sensitive to timing within a partition creation round.
        // This means that a direct comparison is not possible.
        val maxID: Long = expectedStates.size.coerceAtLeast(actualStates.size).toLong()
        for (partitionsCreatorID in 1L..maxID) {
            val expected: Set<JsonNode>? = expectedStates.getOrNull(partitionsCreatorID.toInt() - 1)
            val actual: Set<JsonNode>? = actualStates.getOrNull(partitionsCreatorID.toInt() - 1)
            if (expected == null) {
                Assertions.assertNull(
                    actual,
                    "expected nothing in round $partitionsCreatorID, got $actual",
                )
                break
            }
            Assertions.assertNotNull(
                actual,
                "expected $expected in round $partitionsCreatorID, got nothing",
            )
            for (actualState in actual!!) {
                Assertions.assertTrue(
                    actualState.toString() in expected.map { it.toString() },
                    "$actualState should be in $expected",
                )
            }
        }
    }

    /** [isSuccessful] represents whether the READ operation is expected to be successful. */
    val isSuccessful: Boolean = creatorCases.all { it.isSuccessful() }

    private fun CreatorCase.isSuccessful(): Boolean =
        when (this) {
            is CreatorBackOff -> next.isSuccessful()
            CreatorFailure -> false
            is Create -> readerCases.all { it.isSuccessful() }
        }

    private fun ReaderCase.isSuccessful(): Boolean =
        when (this) {
            is ReaderBackOff -> next.isSuccessful()
            ReaderFailure -> false
            Read -> true
        }

    /**
     * [expectedStates] represent the expected state values in the messages. Sets are formed by the
     * state values emitted by concurrent [PartitionReader] instances.
     */
    val expectedStates: List<Set<JsonNode>> =
        mutableListOf<Set<JsonNode>>().apply {
            creatorCases.forEachIndexed { creatorIndex, creatorCase ->
                val set = creatorCase.states(1L + creatorIndex)
                val trimmed = set.takeWhile { it.isArray }.toSet()
                if (trimmed.isEmpty()) return@apply
                add(trimmed)
                if (trimmed.size < set.size) return@apply
            }
        }

    private fun CreatorCase.states(creatorID: Long): Set<JsonNode> =
        when (this) {
            is CreatorBackOff -> next.states(creatorID)
            CreatorFailure -> setOf()
            is Create ->
                readerCases
                    .mapIndexed { idx, readerCase -> readerCase.state(creatorID, 1L + idx) }
                    .toSet()
        }

    private fun ReaderCase.state(
        creatorID: Long,
        readerID: Long,
    ): JsonNode =
        when (this) {
            is ReaderBackOff -> next.state(creatorID, readerID)
            ReaderFailure -> Jsons.nullNode()
            Read -> Jsons.arrayNode().add(creatorID).add(readerID)
        }
}

/** A [CreatorCase] specifies how the [TestPartitionsCreator] should behave. */
sealed interface CreatorCase

data class CreatorBackOff(
    val next: CreatorCase,
) : CreatorCase

data object CreatorFailure : CreatorCase

data class Create(
    val readerCases: List<ReaderCase>,
) : CreatorCase {
    constructor(vararg readerCases: ReaderCase) : this(readerCases.toList())
}

/** A [ReaderCase] specifies how the [TestPartitionReader] should behave. */
sealed interface ReaderCase

data class ReaderBackOff(
    val next: ReaderCase,
) : ReaderCase

data object ReaderFailure : ReaderCase

data object Read : ReaderCase

class TestPartitionsCreator(
    private val creatorID: Long,
    private var case: CreatorCase,
    private val resource: Semaphore,
) : PartitionsCreator {
    private val log = KotlinLogging.logger {}

    override fun tryAcquireResources(): PartitionsCreator.TryAcquireResourcesStatus =
        when (val case = case) {
            is CreatorBackOff -> {
                log.info { "failed resource acquisition due to deliberate backoff" }
                this.case = case.next
                PartitionsCreator.TryAcquireResourcesStatus.RETRY_LATER
            }
            else -> {
                if (resource.tryAcquire()) {
                    log.info { "resource acquisition successful" }
                    PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN
                } else {
                    log.info { "failed resource acquisition due to resource starvation" }
                    PartitionsCreator.TryAcquireResourcesStatus.RETRY_LATER
                }
            }
        }

    override fun releaseResources() {
        resource.release()
    }

    override suspend fun run(): List<PartitionReader> {
        while (true) {
            when (val case = case) {
                is CreatorBackOff -> TODO("unreachable code")
                CreatorFailure -> {
                    log.info { "deliberately failing the partitioning" }
                    throw RuntimeException("boom")
                }
                is Create -> {
                    val partitionReaders: List<PartitionReader> =
                        case.readerCases.mapIndexed { idx: Int, readerCase: ReaderCase ->
                            TestPartitionReader(creatorID, 1L + idx, readerCase, resource)
                        }
                    log.info { "successfully created ${partitionReaders.size} partition(s)" }
                    return partitionReaders
                }
            }
        }
    }
}

class TestPartitionReader(
    private val creatorID: Long,
    private val readerID: Long,
    private var case: ReaderCase,
    private val resource: Semaphore,
) : PartitionReader {
    private val log = KotlinLogging.logger {}

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus =
        when (val case = case) {
            is ReaderBackOff -> {
                log.info { "failed resource acquisition due to deliberate backoff" }
                this.case = case.next
                PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
            }
            else -> {
                if (resource.tryAcquire()) {
                    log.info { "resource acquisition successful" }
                    PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
                } else {
                    log.info { "failed resource acquisition due to resource starvation" }
                    PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
                }
            }
        }

    override fun releaseResources() {
        resource.release()
    }

    override suspend fun run() {
        when (case) {
            is ReaderBackOff -> TODO("unreachable code")
            is ReaderFailure -> {
                log.info { "deliberately failing the read" }
                throw RuntimeException("boom")
            }
            is Read -> {
                delay(readDelay().toKotlinDuration())
                log.info { "partition read successful" }
            }
        }
    }

    override fun checkpoint(): PartitionReadCheckpoint =
        PartitionReadCheckpoint(
            opaqueStateValue = Jsons.arrayNode().add(creatorID).add(readerID),
            numRecords = 0L,
        )
}

class TestPartitionsCreatorFactory(
    val resource: Semaphore,
    vararg val testCases: TestCase,
) : PartitionsCreatorFactory {
    private val log = KotlinLogging.logger {}

    override fun make(
        stateQuerier: StateQuerier,
        feed: Feed,
    ): PartitionsCreator {
        if (feed is Global) {
            // For a global feed, return a bogus PartitionsCreator which backs off forever.
            // This tests that the corresponding coroutine gets canceled properly.
            return object : PartitionsCreator {
                override fun tryAcquireResources(): PartitionsCreator.TryAcquireResourcesStatus {
                    log.info { "failed to acquire resources for global feed, as always" }
                    return PartitionsCreator.TryAcquireResourcesStatus.RETRY_LATER
                }

                override suspend fun run(): List<PartitionReader> {
                    TODO("unreachable code")
                }

                override fun releaseResources() {
                    TODO("unreachable code")
                }
            }
        }
        // For a stream feed, pick the CreatorCase in the corresponding TestCase
        // which is the successor of the one whose corresponding state is in the StateQuerier.
        val testCase: TestCase = testCases.find { it.name == (feed as Stream).name }!!
        val checkpointedPartitionCreatorID: Long =
            when (val opaqueStateValue: OpaqueStateValue? = stateQuerier.current(feed)) {
                null -> 0L
                is ArrayNode -> opaqueStateValue.get(0).asLong()
                else -> TODO("unreachable code")
            }
        val nextCreatorCaseIndex: Int =
            checkpointedPartitionCreatorID.toInt() // the ID is off by 1 so this works
        if (nextCreatorCaseIndex >= testCase.creatorCases.size) TODO("unreachable code")
        return TestPartitionsCreator(
            1L + checkpointedPartitionCreatorID,
            testCase.creatorCases[nextCreatorCaseIndex],
            resource,
        )
    }
}

/** Tests should succeed and not timeout. */
val excessiveTimeout: Duration = Duration.ofSeconds(TEST_TIMEOUT_SECONDS * 2)

/** The heartbeat duration is set to allow enough room to back off many times. */
val slowHeartbeat: Duration = Duration.ofSeconds(TEST_TIMEOUT_SECONDS).dividedBy(100L)

fun readDelay(): Duration =
    Duration.ofSeconds(TEST_TIMEOUT_SECONDS)
        .dividedBy(1000L)
        .multipliedBy(Random.Default.nextLong(1L, 10L))
