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
            Assertions.assertTrue(state["scan"]["exclusive_start_key"].has("id"), state.toString())
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
            Assertions.assertTrue(state["scan"]["exclusive_start_key"].has("id"), state.toString())
            Assertions.assertTrue(state["scan"].has("max_cursor"), state.toString())
        }
        Assertions.assertEquals(
            Jsons.readTree("""{"cursor_field":["v"],"cursor":"$ITEMS","cursor_record_count":1}"""),
            run.checkpoints.last().opaqueStateValue,
        )
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
                val partition: DynamoDbPartition =
                    DynamoDbPartition.plan(feedBootstrap, sharedState) ?: break
                val reader = DynamoDbPartitionReader(partition, feedBootstrap, sharedState)
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
