/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.command.InputState
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.StreamStateValue
import io.airbyte.cdk.consumers.BufferingCatalogValidationFailureHandler
import io.airbyte.cdk.consumers.CatalogValidationFailure
import io.airbyte.cdk.consumers.InvalidCursor
import io.airbyte.cdk.consumers.InvalidPrimaryKey
import io.airbyte.cdk.consumers.ResetStream
import io.airbyte.cdk.consumers.TableHasNoDataColumns
import io.airbyte.cdk.consumers.TableNotFound
import io.airbyte.cdk.source.Field
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
@Property(name = "airbyte.connector.config.cursor.cursor_method", value = "user_defined")
@Property(name = "metadata.resource", value = "read/metadata.json")
class StateManagerStreamStatesTest {

    @Inject lateinit var config: SourceConfiguration
    @Inject lateinit var configuredCatalog: ConfiguredAirbyteCatalog
    @Inject lateinit var inputState: InputState
    @Inject lateinit var stateManagerFactory: StateManagerFactory
    @Inject lateinit var handler: BufferingCatalogValidationFailureHandler

    val stateManager: StateManager by lazy {
        stateManagerFactory.create(config, configuredCatalog, inputState)
    }

    @Test
    @Property(
        name = "airbyte.connector.catalog.json",
        value =
            """
{"streams": [{
    "stream": {
        "name": "BLAH",
        "json_schema": { "type": "object","properties": {} },
        "supported_sync_modes": ["full_refresh", "incremental"],
        "default_cursor_field": ["ID", "TS"],
        "source_defined_primary_key": [["ID"]],
        "namespace": "PUBLIC"
    },
    "sync_mode": "full_refresh", 
    "destination_sync_mode": "overwrite"
}]}"""
    )
    @Property(name = "airbyte.connector.state.json", value = "[]")
    fun testBadStreamName() {
        // test current state
        Assertions.assertEquals(listOf<State<*>>(), stateManager.currentStates())
        Assertions.assertEquals(listOf(TableNotFound("BLAH", "PUBLIC")), handler.get())
    }

    @Test
    @Property(
        name = "airbyte.connector.catalog.json",
        value =
            """
{"streams": [{
    "stream": {
        "name": "EVENTS",
        "json_schema": { "type": "object","properties": {} },
        "supported_sync_modes": ["full_refresh", "incremental"],
        "default_cursor_field": ["ID", "TS"],
        "source_defined_primary_key": [["ID"]],
        "namespace": "PUBLIC"
    },
    "sync_mode": "full_refresh", 
    "destination_sync_mode": "overwrite"
}]}"""
    )
    @Property(name = "airbyte.connector.state.json", value = "[]")
    fun testBadSchema() {
        // test current state
        Assertions.assertEquals(listOf<State<*>>(), stateManager.currentStates())
        Assertions.assertEquals(listOf(TableHasNoDataColumns("EVENTS", "PUBLIC")), handler.get())
    }

    @Test
    @Property(
        name = "airbyte.connector.catalog.json",
        value =
            """
{"streams": [{
    "stream": $STREAM,
    "sync_mode": "full_refresh",
    "primary_key": [["ID"]], 
    "destination_sync_mode": "overwrite"
}]}"""
    )
    @Property(name = "airbyte.connector.state.json", value = "[]")
    fun testFullRefreshColdStart() {
        // test current state
        val untypedState: StreamState = prelude(SyncMode.FULL_REFRESH, listOf("ID"))
        Assertions.assertNotNull(untypedState as? FullRefreshNotStarted)
        Assertions.assertEquals(listOf<CatalogValidationFailure>(), handler.get())
        val state = untypedState as FullRefreshNotStarted
        // update state manager with fake work result
        val fakeWorkResult: WorkResult<StreamKey, *, out StreamState> =
            state
                .resumable(LimitState.minimum, state.key.configuredPrimaryKey!!)
                .output
                .ongoing(LimitState.minimum, listOf(nodeFactory.textNode(UUID)), 123L)
        stateManager.set(fakeWorkResult.output, fakeWorkResult.numRecords)
        // test checkpoint messages
        val checkpoint: List<AirbyteStateMessage> = stateManager.checkpoint()
        Assertions.assertEquals(listOf(123.0), checkpoint.map { it.sourceStats?.recordCount })
        Assertions.assertEquals(
            Jsons.jsonNode(
                StreamStateValue(primaryKey = mapOf("ID" to nodeFactory.textNode(UUID)))
            ),
            checkpoint.first().stream.streamState
        )
    }

    @Test
    @Property(
        name = "airbyte.connector.catalog.json",
        value =
            """
{"streams": [{
    "stream": $STREAM,
    "sync_mode": "full_refresh",
    "primary_key": [["ID"]], 
    "destination_sync_mode": "overwrite"
}]}"""
    )
    @Property(
        name = "airbyte.connector.state.json",
        value =
            """
[{"type": "STREAM", "stream": {
    "stream_descriptor": { "name": "EVENTS", "namespace": "PUBLIC" },
    "stream_state": { "primary_key": { "ID": "$UUID" } }
}}]"""
    )
    fun testFullRefreshWarmStart() {
        // test current state
        val untypedState: StreamState = prelude(SyncMode.FULL_REFRESH, listOf("ID"))
        Assertions.assertNotNull(untypedState as? FullRefreshResumableOngoing)
        val state = untypedState as FullRefreshResumableOngoing
        Assertions.assertEquals(LimitState.minimum, state.limit)
        Assertions.assertEquals(listOf("ID"), state.primaryKey.map { it.id })
        Assertions.assertEquals(listOf(nodeFactory.textNode(UUID)), state.primaryKeyCheckpoint)
        Assertions.assertEquals(listOf<CatalogValidationFailure>(), handler.get())
        // update state manager with fake work result
        val fakeWorkResult: WorkResult<StreamKey, *, out StreamState> = state.completed(123L)
        stateManager.set(fakeWorkResult.output, fakeWorkResult.numRecords)
        // test checkpoint messages
        val checkpoint: List<AirbyteStateMessage> = stateManager.checkpoint()
        Assertions.assertEquals(listOf(123.0), checkpoint.map { it.sourceStats?.recordCount })
        Assertions.assertEquals(
            Jsons.jsonNode(StreamStateValue(primaryKey = mapOf())),
            checkpoint.first().stream.streamState
        )
    }

    @Test
    @Property(
        name = "airbyte.connector.catalog.json",
        value =
            """
{"streams": [{
    "stream": $STREAM,
    "sync_mode": "full_refresh",
    "primary_key": [["ID"]], 
    "destination_sync_mode": "overwrite"
}]}"""
    )
    @Property(
        name = "airbyte.connector.state.json",
        value =
            """
[{"type": "STREAM", "stream": {
    "stream_descriptor": { "name": "EVENTS", "namespace": "PUBLIC" },
    "stream_state": { "primary_key": { "FOO": "BAR" } }
}}]"""
    )
    fun testFullRefreshRestart() {
        val untypedState: StreamState = prelude(SyncMode.FULL_REFRESH, listOf("ID"))
        Assertions.assertNotNull(untypedState as? FullRefreshNotStarted)
        Assertions.assertEquals(
            listOf(
                InvalidPrimaryKey("EVENTS", "PUBLIC", listOf("FOO")),
                ResetStream("EVENTS", "PUBLIC")
            ),
            handler.get()
        )
    }

    @Test
    @Property(
        name = "airbyte.connector.catalog.json",
        value =
            """
{"streams": [{
    "stream": $STREAM,
    "sync_mode": "incremental",
    "cursor_field": ["TS"], 
    "primary_key": [["ID"]], 
    "destination_sync_mode": "overwrite"
}]}"""
    )
    @Property(name = "airbyte.connector.state.json", value = "[]")
    fun testCursorBasedColdStart() {
        // test current state
        val untypedState: StreamState = prelude(SyncMode.INCREMENTAL, listOf("ID"), "TS")
        Assertions.assertNotNull(untypedState as? CursorBasedNotStarted)
        Assertions.assertEquals(listOf<CatalogValidationFailure>(), handler.get())
        // update state manager with fake work result
        val state = untypedState as CursorBasedNotStarted
        val fakeWorkResult: WorkResult<StreamKey, *, out StreamState> =
            state
                .resumable(
                    LimitState.minimum,
                    state.key.configuredPrimaryKey!!,
                    state.key.configuredCursor as Field,
                    nodeFactory.textNode(TIMESTAMP)
                )
                .output
                .ongoing(LimitState.minimum, listOf(nodeFactory.textNode(UUID)), 123L)
        stateManager.set(fakeWorkResult.output, fakeWorkResult.numRecords)
        // test checkpoint messages
        val checkpoint: List<AirbyteStateMessage> = stateManager.checkpoint()
        Assertions.assertEquals(listOf(123.0), checkpoint.map { it.sourceStats?.recordCount })
        Assertions.assertEquals(
            Jsons.jsonNode(
                StreamStateValue(
                    primaryKey = mapOf("ID" to nodeFactory.textNode(UUID)),
                    cursors = mapOf("TS" to nodeFactory.textNode(TIMESTAMP))
                )
            ),
            checkpoint.first().stream.streamState
        )
    }

    @Test
    @Property(
        name = "airbyte.connector.catalog.json",
        value =
            """
{"streams": [{
    "stream": $STREAM,
    "sync_mode": "incremental",
    "cursor_field": ["TS"], 
    "primary_key": [["ID"]], 
    "destination_sync_mode": "overwrite"
}]}"""
    )
    @Property(
        name = "airbyte.connector.state.json",
        value =
            """
[{"type": "STREAM", "stream": {
    "stream_descriptor": { "name": "EVENTS", "namespace": "PUBLIC" },
    "stream_state": { "cursors": { "TS": "2024-04-28 00:00:00-04" } }
}}]"""
    )
    fun testCursorBasedWarmStart() {
        // test current state
        val untypedState: StreamState = prelude(SyncMode.INCREMENTAL, listOf("ID"), "TS")
        Assertions.assertNotNull(untypedState as? CursorBasedIncrementalStarting)
        Assertions.assertEquals(listOf<CatalogValidationFailure>(), handler.get())
        // update state manager with fake work result
        val state = untypedState as CursorBasedIncrementalStarting
        val fakeWorkResult: WorkResult<StreamKey, *, out StreamState> =
            state
                .resumable(LimitState.minimum, nodeFactory.nullNode())
                .output
                .ongoing(LimitState.minimum, nodeFactory.textNode(TIMESTAMP), 123L)
        stateManager.set(fakeWorkResult.output, fakeWorkResult.numRecords)
        // test checkpoint messages
        val checkpoint: List<AirbyteStateMessage> = stateManager.checkpoint()
        Assertions.assertEquals(listOf(123.0), checkpoint.map { it.sourceStats?.recordCount })
        Assertions.assertEquals(
            Jsons.jsonNode(
                StreamStateValue(cursors = mapOf("TS" to nodeFactory.textNode(TIMESTAMP)))
            ),
            checkpoint.first().stream.streamState
        )
    }

    @Test
    @Property(
        name = "airbyte.connector.catalog.json",
        value =
            """
{"streams": [{
    "stream": $STREAM,
    "sync_mode": "incremental",
    "cursor_field": ["TS"], 
    "primary_key": [["ID"]], 
    "destination_sync_mode": "overwrite"
}]}"""
    )
    @Property(
        name = "airbyte.connector.state.json",
        value =
            """
[{"type": "STREAM", "stream": {
    "stream_descriptor": { "name": "EVENTS", "namespace": "PUBLIC" },
    "stream_state": { "cursors": { "FOO": "BAR" } }
}}]"""
    )
    fun testCursorBasedResetCursor() {
        // test current state
        val untypedState: StreamState = prelude(SyncMode.INCREMENTAL, listOf("ID"), "TS")
        Assertions.assertNotNull(untypedState as? CursorBasedNotStarted)
        Assertions.assertEquals(
            listOf(InvalidCursor("EVENTS", "PUBLIC", "FOO"), ResetStream("EVENTS", "PUBLIC")),
            handler.get()
        )
    }

    @Test
    @Property(
        name = "airbyte.connector.catalog.json",
        value =
            """
{"streams": [{
    "stream": $STREAM,
    "sync_mode": "incremental",
    "cursor_field": ["TS"], 
    "primary_key": [["ID"]], 
    "destination_sync_mode": "overwrite"
}]}"""
    )
    @Property(
        name = "airbyte.connector.state.json",
        value =
            """
[{"type": "STREAM", "stream": {
    "stream_descriptor": { "name": "EVENTS", "namespace": "PUBLIC" },
    "stream_state": {  "primary_key": { "FOO": "BAR" }, "cursors": { "TS": "2024-04-28 00:00:00-04" } }
}}]"""
    )
    fun testCursorBasedResetPrimaryKey() {
        // test current state
        val untypedState: StreamState = prelude(SyncMode.INCREMENTAL, listOf("ID"), "TS")
        Assertions.assertNotNull(untypedState as? CursorBasedNotStarted)
        Assertions.assertEquals(
            listOf(
                InvalidPrimaryKey("EVENTS", "PUBLIC", listOf("FOO")),
                ResetStream("EVENTS", "PUBLIC")
            ),
            handler.get()
        )
    }

    private fun prelude(
        expectedSyncMode: SyncMode,
        expectedPrimaryKey: List<String>? = null,
        expectedCursor: String? = null
    ): StreamState {
        val actualCurrentStates: Map<String?, State<*>> =
            stateManager.currentStates().associateBy {
                (it as? StreamState)?.key?.namePair?.toString()
            }
        val untypedState = actualCurrentStates["PUBLIC_EVENTS"]
        Assertions.assertNotNull(untypedState, actualCurrentStates.keys.toString())
        Assertions.assertEquals(1, actualCurrentStates.size, actualCurrentStates.keys.toString())
        val actualState: StreamState = untypedState as StreamState
        val actualKey: StreamKey = actualState.key
        Assertions.assertEquals(
            TableName("TESTDB", "PUBLIC", "EVENTS", "BASE TABLE"),
            actualKey.table
        )
        Assertions.assertEquals(
            listOf("MSG", "ID", "TS"),
            actualKey.fields.map { it.id }
        )
        Assertions.assertEquals(
            listOf(listOf("ID")),
            actualKey.primaryKeyCandidates.map { col -> col.map { it.id } }
        )
        Assertions.assertEquals(listOf("ID", "TS"), actualKey.cursorCandidates.map { it.id })
        Assertions.assertEquals(expectedSyncMode, actualKey.configuredSyncMode)
        Assertions.assertEquals(
            expectedPrimaryKey,
            actualKey.configuredPrimaryKey?.map { it.id }
        )
        Assertions.assertEquals(expectedCursor, actualKey.configuredCursor?.id)
        return actualState
    }

    companion object {
        const val UUID = "fb059831-0130-42b6-9ba9-b316a33d32b9"
        const val TIMESTAMP = "2024-04-29 00:00:00-04"

        const val STREAM =
            """
{
    "name": "EVENTS",
    "json_schema": {
        "type": "object",
        "properties": {
            "MSG": {
                "type": "string"
            },
            "ID": {
                "type": "string"
            },
            "TS": {
                "type": "string",
                "format": "date-time",
                "airbyte_type": "timestamp_with_timezone"
            }
        }
    },
    "supported_sync_modes": ["full_refresh", "incremental"],
    "default_cursor_field": ["ID", "TS"],
    "source_defined_primary_key": [["ID"]],
    "namespace": "PUBLIC"
}"""

        val nodeFactory: JsonNodeFactory = MoreMappers.initMapper().nodeFactory
    }
}
