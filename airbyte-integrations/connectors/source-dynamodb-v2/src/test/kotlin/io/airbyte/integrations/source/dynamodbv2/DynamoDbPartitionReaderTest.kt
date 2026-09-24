/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.output.DataChannelFormat
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.StateManager
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.dynamodbv2.DynamoDbLocalContainer.Companion.createTableWithItems
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.time.Clock
import java.time.Duration
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test

/**
 * Drives [DynamoDbPartitionReader] round by round the way the CDK's `FeedReader` does, with a zero
 * checkpoint interval so that every round stops after exactly one page. This makes the checkpoint /
 * resume cycle deterministic, which the timing of a real READ is not.
 */
class DynamoDbPartitionReaderTest {

    private val idField = EmittedField("id", DynamoDbFieldType.fromJsonSchema(nullable("string")))
    private val vField = EmittedField("v", DynamoDbFieldType.fromJsonSchema(nullable("integer")))

    @Test
    fun testFullRefreshRounds() {
        val stream =
            Stream(
                StreamIdentifier.from(StreamDescriptor().withName(TABLE)),
                setOf(idField, vField),
                ConfiguredSyncMode.FULL_REFRESH,
                listOf(idField),
                null,
            )
        val run: Rounds = readInRounds(stream, initialState = null)
        // 12 pages of 100 items, then an empty page without LastEvaluatedKey.
        Assertions.assertEquals(13, run.checkpoints.size)
        Assertions.assertEquals(ITEMS, run.output.records().size)
        Assertions.assertEquals(
            ITEMS,
            run.output.records().map { it.data["id"].asText() }.toSet().size
        )
        Assertions.assertEquals(List(12) { 100L } + 0L, run.checkpoints.map { it.numRecords })
        for (checkpoint in run.checkpoints.dropLast(1)) {
            val state: JsonNode = checkpoint.opaqueStateValue
            Assertions.assertEquals(1, state["scan"]["total_segments"].asInt(), state.toString())
            val segment: JsonNode = state["scan"]["segments"].single()
            Assertions.assertTrue(segment["exclusive_start_key"].has("id"), state.toString())
            Assertions.assertFalse(state.has("scan_complete"), state.toString())
        }
        Assertions.assertEquals(
            Jsons.readTree("""{"scan_complete":true}"""),
            run.checkpoints.last().opaqueStateValue,
        )
    }

    @Test
    fun testIncrementalRounds() {
        val stream =
            Stream(
                StreamIdentifier.from(StreamDescriptor().withName(TABLE)),
                setOf(idField, vField),
                ConfiguredSyncMode.INCREMENTAL,
                listOf(idField),
                vField,
            )
        val run: Rounds =
            readInRounds(
                stream,
                initialState = Jsons.readTree("""{"cursor_field":["v"],"cursor":"100"}"""),
            )
        Assertions.assertEquals(ITEMS - 100, run.output.records().size)
        Assertions.assertTrue(run.checkpoints.size > 2, run.checkpoints.toString())
        for (checkpoint in run.checkpoints.dropLast(1)) {
            val state: JsonNode = checkpoint.opaqueStateValue
            // The filter bound is unchanged until the scan completes.
            Assertions.assertEquals("100", state["cursor"].asText(), state.toString())
            val segment: JsonNode = state["scan"]["segments"].single()
            Assertions.assertTrue(segment["exclusive_start_key"].has("id"), state.toString())
            Assertions.assertTrue(segment.has("max_cursor"), state.toString())
        }
        Assertions.assertEquals(
            Jsons.readTree("""{"cursor_field":["v"],"cursor":"$ITEMS","cursor_record_count":1}"""),
            run.checkpoints.last().opaqueStateValue,
        )
    }

    @Test
    fun testSegmentCount() {
        val mib: Long = 1024L * 1024
        Assertions.assertEquals(1, DynamoDbTableScan.segmentCount(0, 64 * mib, 128))
        // A size DynamoDB has not refreshed yet (or an empty table): as many as the concurrency.
        Assertions.assertEquals(4, DynamoDbTableScan.segmentCount(0, 64 * mib, 128, 4))
        Assertions.assertEquals(2, DynamoDbTableScan.segmentCount(0, 64 * mib, 2, 4))
        Assertions.assertEquals(1, DynamoDbTableScan.segmentCount(1, 64 * mib, 128, 4))
        Assertions.assertEquals(1, DynamoDbTableScan.segmentCount(1, 64 * mib, 128))
        Assertions.assertEquals(1, DynamoDbTableScan.segmentCount(64 * mib, 64 * mib, 128))
        Assertions.assertEquals(2, DynamoDbTableScan.segmentCount(64 * mib + 1, 64 * mib, 128))
        Assertions.assertEquals(16, DynamoDbTableScan.segmentCount(1024 * mib, 64 * mib, 128))
        Assertions.assertEquals(
            128,
            DynamoDbTableScan.segmentCount(1024 * 1024 * mib, 64 * mib, 128),
        )
        Assertions.assertEquals(8, DynamoDbTableScan.segmentCount(14288, 1, 8))
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            DynamoDbTableScan.segmentCount(1, 0, 8)
        }
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            DynamoDbTableScan.segmentCount(1, 1, 0)
        }
    }

    /**
     * A segmented full refresh driven one page per segment per round. The third round's checkpoints
     * are lost (a crash after its records went out); a new "process" resumes from the state of
     * round two with another segment cap, which must not matter: the union of both runs is the
     * whole table and exactly the lost round's pages come out twice.
     */
    @Test
    fun testInterruptedSegmentedFullRefreshResumesFromTheLastState() {
        val stream: Stream = fullRefreshStream()
        val first = Driver(stream, initialState = null, pageLimit = 50, maxSegments = 8)
        try {
            val round1: List<PartitionReadCheckpoint> = first.round()!!
            Assertions.assertEquals(8, round1.size)
            val afterRound1: JsonNode = first.currentState()!!
            Assertions.assertEquals(8, afterRound1["scan"]["total_segments"].asInt())
            Assertions.assertEquals(8, afterRound1["scan"]["segments"].size())
            for (segment in afterRound1["scan"]["segments"]) {
                Assertions.assertTrue(
                    segment.has("exclusive_start_key") || segment["complete"]?.asBoolean() == true,
                    afterRound1.toString(),
                )
            }
            first.round()!!
            val stateBeforeCrash: JsonNode = first.currentState()!!
            val emittedBeforeCrash: Int = first.recordIds().size
            first.round(lose = true)!!
            val lost: List<String> = first.recordIds().drop(emittedBeforeCrash)
            Assertions.assertTrue(lost.isNotEmpty())

            val second = Driver(stream, stateBeforeCrash, pageLimit = 50, maxSegments = 3)
            try {
                val states = mutableListOf<JsonNode>()
                while (true) {
                    val checkpoints: List<PartitionReadCheckpoint> = second.round() ?: break
                    states += checkpoints.map { it.opaqueStateValue }
                    Assertions.assertTrue(states.size <= 200, "runaway read")
                }
                Assertions.assertEquals(Jsons.readTree("""{"scan_complete":true}"""), states.last())
                for (state in states.dropLast(1)) {
                    Assertions.assertEquals(
                        8,
                        state["scan"]["total_segments"].asInt(),
                        state.toString()
                    )
                }
                val all: List<String> = first.recordIds() + second.recordIds()
                Assertions.assertEquals(
                    (1..ITEMS).map { "item-%04d".format(it) }.toSet(),
                    all.toSet()
                )
                val counts: Map<String, Int> = all.groupingBy { it }.eachCount()
                Assertions.assertEquals(lost.toSet(), counts.filterValues { it == 2 }.keys)
                Assertions.assertTrue(counts.values.all { it <= 2 })
            } finally {
                second.close()
            }
        } finally {
            first.close()
        }
    }

    /** Same, for an incremental scan: the segments' running maxima survive the crash. */
    @Test
    fun testInterruptedSegmentedIncrementalScanResumesFromTheLastState() {
        val stream: Stream = incrementalStream()
        val initialState: JsonNode = Jsons.readTree("""{"cursor_field":["v"],"cursor":"100"}""")
        val first = Driver(stream, initialState, pageLimit = 50, maxSegments = 8)
        try {
            first.round()!!
            val stateBeforeCrash: JsonNode = first.currentState()!!
            Assertions.assertEquals("100", stateBeforeCrash["cursor"].asText())
            Assertions.assertTrue(
                stateBeforeCrash["scan"]["segments"].any { it.has("max_cursor") },
                stateBeforeCrash.toString(),
            )
            val emittedBeforeCrash: Int = first.recordIds().size
            first.round(lose = true)!!
            val lost: List<String> = first.recordIds().drop(emittedBeforeCrash)

            val second = Driver(stream, stateBeforeCrash, pageLimit = 50, maxSegments = 8)
            try {
                var last: JsonNode? = null
                var rounds = 0
                while (true) {
                    val checkpoints: List<PartitionReadCheckpoint> = second.round() ?: break
                    last = checkpoints.last().opaqueStateValue
                    Assertions.assertTrue(++rounds <= 200, "runaway read")
                }
                Assertions.assertEquals(
                    Jsons.readTree(
                        """{"cursor_field":["v"],"cursor":"$ITEMS","cursor_record_count":1}"""
                    ),
                    last,
                )
                val all: List<String> = first.recordIds() + second.recordIds()
                Assertions.assertEquals(
                    (101..ITEMS).map { "item-%04d".format(it) }.toSet(),
                    all.toSet(),
                )
                val counts: Map<String, Int> = all.groupingBy { it }.eachCount()
                Assertions.assertEquals(lost.toSet(), counts.filterValues { it == 2 }.keys)
            } finally {
                second.close()
            }
        } finally {
            first.close()
        }
    }

    /**
     * Every segment complete but the state applied last not terminal: the planner adds a reader
     * that emits nothing but the terminal state, then nothing more.
     */
    @Test
    fun testTerminalStateIsEmittedWhenEverySegmentIsAlreadyComplete() {
        val state: JsonNode =
            Jsons.readTree(
                """{"scan":{"total_segments":2,"segments":[
                     {"segment":0,"complete":true},{"segment":1,"complete":true}]}}"""
            )
        val driver = Driver(fullRefreshStream(), state, pageLimit = 50, maxSegments = 8)
        try {
            val checkpoints: List<PartitionReadCheckpoint> = driver.round()!!
            Assertions.assertTrue(driver.lastReaders.single() is DynamoDbTerminalStateReader)
            Assertions.assertEquals(
                Jsons.readTree("""{"scan_complete":true}"""),
                checkpoints.single().opaqueStateValue,
            )
            Assertions.assertEquals(0L, checkpoints.single().numRecords)
            Assertions.assertEquals(0, driver.recordIds().size)
            Assertions.assertNull(driver.round())
        } finally {
            driver.close()
        }
    }

    private fun fullRefreshStream(): Stream =
        Stream(
            StreamIdentifier.from(StreamDescriptor().withName(TABLE)),
            setOf(idField, vField),
            ConfiguredSyncMode.FULL_REFRESH,
            listOf(idField),
            null,
        )

    private fun incrementalStream(): Stream =
        Stream(
            StreamIdentifier.from(StreamDescriptor().withName(TABLE)),
            setOf(idField, vField),
            ConfiguredSyncMode.INCREMENTAL,
            listOf(idField),
            vField,
        )

    /**
     * Drives the partitions creator and its readers round by round like the CDK's `FeedReader`, one
     * reader at a time (as with `concurrency` 1), with a zero checkpoint interval so that every
     * reader stops after one page. Every table byte asks for a segment; [maxSegments] decides.
     */
    private inner class Driver(
        val stream: Stream,
        initialState: OpaqueStateValue?,
        pageLimit: Int,
        maxSegments: Int,
    ) {
        private val configuration: DynamoDbSourceConfiguration =
            DynamoDbSourceConfigurationFactory()
                .make(container.config())
                .copy(checkpointTargetInterval = Duration.ZERO)
        private val concurrencyResource = ConcurrencyResource(configuration)
        private val sharedState =
            DynamoDbSharedState(
                configuration,
                concurrencyResource,
                ResourceAcquirer(listOf(concurrencyResource)),
                scanPageLimit = pageLimit,
                segmentTargetBytes = 1,
                maxSegments = maxSegments,
            )
        private val output = BufferingOutputConsumer(Clock.systemUTC())
        private val stateManager = StateManager(initialStreamStates = mapOf(stream to initialState))
        private val feedBootstrap =
            StreamFeedBootstrap(
                output,
                DynamoDbMetaFieldDecorator(),
                stateManager,
                stream,
                DataChannelFormat.JSONL,
                DataChannelMedium.STDIO,
                8192,
                Clock.systemUTC(),
            )
        var lastReaders: List<PartitionReader> = emptyList()
            private set

        /**
         * One round: plans, runs every reader, returns their checkpoints, and applies them to the
         * state manager in order unless [lose] (a crash before the states were published). Null
         * when the planner has nothing left.
         */
        fun round(lose: Boolean = false): List<PartitionReadCheckpoint>? {
            val readers: List<PartitionReader> = runBlocking {
                DynamoDbPartitionsCreator(feedBootstrap, sharedState).run()
            }
            lastReaders = readers
            if (readers.isEmpty()) return null
            val checkpoints: List<PartitionReadCheckpoint> =
                readers.map { reader: PartitionReader ->
                    Assertions.assertEquals(
                        PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN,
                        reader.tryAcquireResources(),
                    )
                    try {
                        runBlocking { reader.run() }
                        reader.checkpoint()
                    } finally {
                        reader.releaseResources()
                    }
                }
            if (!lose) {
                for (checkpoint in checkpoints) {
                    stateManager
                        .scoped(stream)
                        .set(checkpoint.opaqueStateValue, checkpoint.numRecords, null, null)
                }
                stateManager.checkpoint()
            }
            return checkpoints
        }

        fun currentState(): OpaqueStateValue? = stateManager.scoped(stream).current()

        fun recordIds(): List<String> = output.records().map { it.data["id"].asText() }

        fun close() = sharedState.close()
    }

    class Rounds(
        val output: BufferingOutputConsumer,
        val checkpoints: List<PartitionReadCheckpoint>
    )

    /**
     * Plans a partition, reads it and feeds its checkpoint back into the state manager, until the
     * planner returns nothing; one page per round.
     */
    private fun readInRounds(stream: Stream, initialState: OpaqueStateValue?): Rounds {
        val configuration: DynamoDbSourceConfiguration =
            DynamoDbSourceConfigurationFactory()
                .make(container.config())
                .copy(checkpointTargetInterval = Duration.ZERO)
        val concurrencyResource = ConcurrencyResource(configuration)
        val sharedState =
            DynamoDbSharedState(
                configuration,
                concurrencyResource,
                ResourceAcquirer(listOf(concurrencyResource)),
                scanPageLimit = 100,
            )
        val output = BufferingOutputConsumer(Clock.systemUTC())
        val stateManager = StateManager(initialStreamStates = mapOf(stream to initialState))
        val feedBootstrap =
            StreamFeedBootstrap(
                output,
                DynamoDbMetaFieldDecorator(),
                stateManager,
                stream,
                DataChannelFormat.JSONL,
                DataChannelMedium.STDIO,
                8192,
                Clock.systemUTC(),
            )
        val checkpoints = mutableListOf<PartitionReadCheckpoint>()
        try {
            while (true) {
                // The table is far below one segment target, so every round has one partition.
                val readers: List<PartitionReader> = runBlocking {
                    DynamoDbPartitionsCreator(feedBootstrap, sharedState).run()
                }
                if (readers.isEmpty()) break
                val reader: PartitionReader = readers.single()
                Assertions.assertEquals(
                    PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN,
                    reader.tryAcquireResources(),
                )
                val checkpoint: PartitionReadCheckpoint =
                    try {
                        runBlocking { reader.run() }
                        reader.checkpoint()
                    } finally {
                        reader.releaseResources()
                    }
                checkpoints.add(checkpoint)
                stateManager
                    .scoped(stream)
                    .set(checkpoint.opaqueStateValue, checkpoint.numRecords, null, null)
                // Like FeedReader.maybeCheckpoint: publishes the pending state as the current one.
                stateManager.checkpoint()
                Assertions.assertTrue(checkpoints.size <= 100, "runaway read: $checkpoints")
            }
        } finally {
            sharedState.close()
        }
        return Rounds(output, checkpoints)
    }

    private fun nullable(type: String): JsonNode = Jsons.readTree("""{"type":["null","$type"]}""")

    companion object {
        const val TABLE = "many_items"
        const val ITEMS = 1200

        lateinit var container: DynamoDbLocalContainer

        @JvmStatic
        @BeforeAll
        fun startContainer() {
            container = DynamoDbLocalContainer().also { it.start() }
            val table: DynamoDbParitySeed.Table =
                DynamoDbParitySeed.tables().first { it.name == TABLE }
            Assertions.assertEquals(ITEMS, table.items.size)
            container.client().use {
                it.createTableWithItems(table.name, table.keySchema, table.items)
            }
        }

        @JvmStatic
        @AfterAll
        fun stopContainer() {
            container.stop()
        }
    }
}
