/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.command.GlobalStateValue
import io.airbyte.cdk.command.InputState
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.StreamStateValue
import io.airbyte.cdk.consumers.BufferingCatalogValidationFailureHandler
import io.airbyte.cdk.consumers.CatalogValidationFailure
import io.airbyte.cdk.source.TableName
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.SyncMode
import io.micronaut.context.annotation.Property
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(rebuildContext = true)
@Property(name = "airbyte.connector.config.host", value = "localhost")
@Property(name = "airbyte.connector.config.database", value = "testdb")
@Property(name = "airbyte.connector.config.cursor.cursor_method", value = "cdc")
@Property(name = "metadata.resource", value = "read/metadata.json")
class StateManagerGlobalStatesTest {

    @Inject lateinit var config: SourceConfiguration
    @Inject lateinit var configuredCatalog: ConfiguredAirbyteCatalog
    @Inject lateinit var inputState: InputState
    @Inject lateinit var stateManagerFactory: StateManagerFactory
    @Inject lateinit var handler: BufferingCatalogValidationFailureHandler

    val stateManager: StateManager by lazy {
        stateManagerFactory.create(config, configuredCatalog, inputState)
    }

    @Test
    @Property(name = "airbyte.connector.catalog.resource", value = "read/cdc-catalog.json")
    @Property(
        name = "airbyte.connector.state.json",
        value =
            """
{"type": "GLOBAL", "global": {
    "shared_state": { "cdc": {} },
    "stream_states": [{
        "stream_descriptor": { "name": "BAR", "namespace": "FOO" },
        "stream_state": { "primary_key": {} }
}]}}"""
    )
    fun testStreamInStateButNotInCatalog() {
        prelude()
        Assertions.assertEquals(listOf<CatalogValidationFailure>(), handler.get())
    }

    @Test
    @Property(name = "airbyte.connector.catalog.resource", value = "read/cdc-catalog.json")
    @Property(name = "airbyte.connector.state.json", value = "[]")
    fun testColdStart() {
        val (untypedGlobalState: GlobalState, untypedStreamStates) = prelude()
        val (untypedEventsState: StreamState, untypedKvState: StreamState) = untypedStreamStates
        // test current state
        Assertions.assertNotNull(untypedGlobalState as? CdcNotStarted)
        val globalState = untypedGlobalState as CdcNotStarted
        Assertions.assertNotNull(untypedEventsState as? FullRefreshNotStarted)
        Assertions.assertNotNull(untypedKvState as? CdcInitialSyncNotStarted)
        val kvState = untypedKvState as CdcInitialSyncNotStarted
        Assertions.assertEquals(listOf<CatalogValidationFailure>(), handler.get())
        // update state manager with fake work results
        val globalFakeWorkResult: WorkResult<GlobalKey, *, out GlobalState> =
            globalState.completed(GlobalStateValue(Jsons.emptyObject()))
        stateManager.set(globalFakeWorkResult.output, globalFakeWorkResult.numRecords)
        val kvFakeWorkResult: WorkResult<StreamKey, *, out StreamState> =
            kvState
                .resumable(LimitState.minimum, kvState.key.configuredPrimaryKey!!)
                .output
                .ongoing(LimitState.minimum, listOf(nodeFactory.numberNode(1)), 123L)
        stateManager.set(kvFakeWorkResult.output, kvFakeWorkResult.numRecords)
        // test checkpoint messages
        val checkpoint: List<AirbyteStateMessage> = stateManager.checkpoint()
        Assertions.assertEquals(listOf(123.0), checkpoint.map { it.sourceStats?.recordCount })
        Assertions.assertEquals(
            mapOf(
                "KV" to
                    Jsons.jsonNode(
                        StreamStateValue(primaryKey = mapOf("K" to nodeFactory.numberNode(1)))
                    )
            ),
            checkpoint.first().global.streamStates.associate {
                it.streamDescriptor.name to it.streamState
            }
        )
    }

    @Test
    @Property(name = "airbyte.connector.catalog.resource", value = "read/cdc-catalog.json")
    @Property(
        name = "airbyte.connector.state.json",
        value =
            """
{"type": "GLOBAL", "global": {
    "shared_state": { "cdc": {} },
    "stream_states": [{
        "stream_descriptor": { "name": "KV", "namespace": "PUBLIC" },
        "stream_state": { "primary_key": { "K": "1" } }
}]}}"""
    )
    fun testInitialSyncWarmStart() {
        val (untypedGlobalState: GlobalState, untypedStreamStates) = prelude()
        val (untypedEventsState: StreamState, untypedKvState: StreamState) = untypedStreamStates
        // test current state
        Assertions.assertNotNull(untypedGlobalState as? CdcStarting)
        val globalState = untypedGlobalState as CdcStarting
        Assertions.assertNotNull(untypedEventsState as? FullRefreshNotStarted)
        Assertions.assertNotNull(untypedKvState as? CdcResumableInitialSyncOngoing)
        val kvState = untypedKvState as CdcResumableInitialSyncOngoing
        Assertions.assertEquals(listOf<CatalogValidationFailure>(), handler.get())
        // update state manager with fake work results
        val globalFakeWorkResult: WorkResult<GlobalKey, *, out GlobalState> =
            globalState.ongoing(GlobalStateValue(Jsons.emptyObject())).output.completed(456L)
        stateManager.set(globalFakeWorkResult.output, globalFakeWorkResult.numRecords)
        val kvFakeWorkResult: WorkResult<StreamKey, *, out StreamState> = kvState.completed(123L)
        stateManager.set(kvFakeWorkResult.output, kvFakeWorkResult.numRecords)
        // test checkpoint messages
        val checkpoint: List<AirbyteStateMessage> = stateManager.checkpoint()
        Assertions.assertEquals(listOf(579.0), checkpoint.map { it.sourceStats?.recordCount })
        Assertions.assertEquals(
            mapOf("KV" to Jsons.jsonNode(StreamStateValue(primaryKey = mapOf()))),
            checkpoint.first().global.streamStates.associate {
                it.streamDescriptor.name to it.streamState
            }
        )
    }

    @Test
    @Property(name = "airbyte.connector.catalog.resource", value = "read/cdc-catalog.json")
    @Property(
        name = "airbyte.connector.state.json",
        value =
            """
{"type": "GLOBAL", "global": {
    "shared_state": { "cdc": {} },
    "stream_states": [{
        "stream_descriptor": { "name": "KV", "namespace": "PUBLIC" },
        "stream_state": { "primary_key": {} }
}]}}"""
    )
    fun testIncrementalWarmStart() {
        val (untypedGlobalState: GlobalState, untypedStreamStates) = prelude()
        val (untypedEventsState: StreamState, untypedKvState: StreamState) = untypedStreamStates
        // test current state
        Assertions.assertNotNull(untypedGlobalState as? CdcStarting)
        val globalState = untypedGlobalState as CdcStarting
        Assertions.assertNotNull(untypedEventsState as? FullRefreshNotStarted)
        Assertions.assertNotNull(untypedKvState as? CdcInitialSyncCompleted)
        Assertions.assertEquals(listOf<CatalogValidationFailure>(), handler.get())
        // update state manager with fake work results
        val globalFakeWorkResult: WorkResult<GlobalKey, *, out GlobalState> =
            globalState.ongoing(GlobalStateValue(Jsons.emptyObject())).output.completed(789L)
        stateManager.set(globalFakeWorkResult.output, globalFakeWorkResult.numRecords)
        // test checkpoint messages
        val checkpoint: List<AirbyteStateMessage> = stateManager.checkpoint()
        Assertions.assertEquals(listOf(789.0), checkpoint.map { it.sourceStats?.recordCount })
        Assertions.assertEquals(
            mapOf("KV" to Jsons.jsonNode(StreamStateValue(primaryKey = mapOf()))),
            checkpoint.first().global.streamStates.associate {
                it.streamDescriptor.name to it.streamState
            }
        )
    }

    private fun prelude(): Pair<GlobalState, Pair<StreamState, StreamState>> {
        val actualCurrentStates: Map<String?, State<*>> =
            stateManager.currentStates().associateBy {
                (it as? StreamState)?.key?.namePair?.toString()
            }
        val untypedGlobalState = actualCurrentStates[null]
        Assertions.assertNotNull(untypedGlobalState, actualCurrentStates.keys.toString())
        val untypedEventsStreamState = actualCurrentStates["PUBLIC_EVENTS"]
        Assertions.assertNotNull(untypedEventsStreamState, actualCurrentStates.keys.toString())
        val untypedKvStreamState = actualCurrentStates["PUBLIC_KV"]
        Assertions.assertNotNull(untypedKvStreamState, actualCurrentStates.keys.toString())
        Assertions.assertEquals(3, actualCurrentStates.size, actualCurrentStates.keys.toString())
        val actualGlobalState: GlobalState = untypedGlobalState as GlobalState
        val actualKvState: StreamState = untypedKvStreamState as StreamState
        Assertions.assertEquals(
            TableName("TESTDB", "PUBLIC", "KV", "BASE TABLE"),
            actualKvState.key.table
        )
        Assertions.assertEquals(
            listOf("V", "K"),
            actualKvState.key.fields.map { it.id }
        )
        Assertions.assertEquals(
            listOf(listOf("K")),
            actualKvState.key.primaryKeyCandidates.map { col -> col.map { it.id } }
        )
        Assertions.assertEquals(listOf("K"), actualKvState.key.cursorCandidates.map { it.id })
        Assertions.assertEquals(SyncMode.INCREMENTAL, actualKvState.key.configuredSyncMode)
        val actualEventsState: StreamState = untypedEventsStreamState as StreamState
        Assertions.assertEquals(
            TableName("TESTDB", "PUBLIC", "EVENTS", "BASE TABLE"),
            actualEventsState.key.table
        )
        Assertions.assertEquals(
            listOf("MSG", "ID", "TS"),
            actualEventsState.key.fields.map { it.id }
        )
        Assertions.assertEquals(
            listOf(listOf("ID")),
            actualEventsState.key.primaryKeyCandidates.map { col -> col.map { it.id } }
        )
        Assertions.assertEquals(
            listOf("ID", "TS"),
            actualEventsState.key.cursorCandidates.map { it.id }
        )
        Assertions.assertEquals(SyncMode.FULL_REFRESH, actualEventsState.key.configuredSyncMode)
        Assertions.assertEquals(listOf(actualKvState.key), actualGlobalState.key.streamKeys)
        return actualGlobalState to (actualEventsState to actualKvState)
    }

    companion object {
        val nodeFactory: JsonNodeFactory = MoreMappers.initMapper().nodeFactory
    }
}
