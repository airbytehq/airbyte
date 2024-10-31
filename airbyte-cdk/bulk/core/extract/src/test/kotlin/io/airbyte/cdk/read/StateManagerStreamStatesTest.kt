/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.InputState
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.output.BufferingCatalogValidationFailureHandler
import io.airbyte.cdk.output.CatalogValidationFailure
import io.airbyte.cdk.output.StreamHasNoFields
import io.airbyte.cdk.output.StreamNotFound
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.micronaut.context.annotation.Property
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(rebuildContext = true)
@Property(name = "airbyte.connector.config.host", value = "localhost")
@Property(name = "airbyte.connector.config.database", value = "testdb")
@Property(name = "airbyte.connector.config.cursor.cursor_method", value = "user_defined")
@Property(name = "metadata.resource", value = "discover/metadata-valid.json")
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
        "source_defined_primary_key": [["ID"]],
        "namespace": "PUBLIC"
    },
    "sync_mode": "full_refresh", 
    "destination_sync_mode": "overwrite"
}]}""",
    )
    @Property(name = "airbyte.connector.state.json", value = "[]")
    fun testBadStreamName() {
        // test current state
        Assertions.assertEquals(listOf<Feed>(), stateManager.feeds)
        Assertions.assertEquals(listOf(StreamNotFound(streamID("BLAH"))), handler.get())
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
        "source_defined_primary_key": [["ID"]],
        "namespace": "PUBLIC"
    },
    "sync_mode": "full_refresh", 
    "destination_sync_mode": "overwrite"
}]}""",
    )
    @Property(name = "airbyte.connector.state.json", value = "[]")
    fun testBadSchema() {
        // test current state
        Assertions.assertEquals(listOf<Feed>(), stateManager.feeds)
        Assertions.assertEquals(
            listOf(StreamHasNoFields(streamID("EVENTS"))),
            handler.get(),
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
}]}""",
    )
    @Property(name = "airbyte.connector.state.json", value = "[]")
    fun testFullRefreshColdStart() {
        // test current state
        val stream: Stream = prelude(ConfiguredSyncMode.FULL_REFRESH, listOf("ID"))
        Assertions.assertNull(stateManager.scoped(stream).current())
        Assertions.assertEquals(listOf<CatalogValidationFailure>(), handler.get())
        // update state manager with fake work result
        stateManager
            .scoped(stream)
            .set(Jsons.readTree("{\"cursor_incremental\":\"initial_sync_ongoing\"}"), 123L)
        // test checkpoint messages
        val checkpoint: List<AirbyteStateMessage> = stateManager.checkpoint()
        Assertions.assertEquals(
            listOf(
                    """{
                    |"type":"STREAM",
                    |"stream":{"stream_descriptor":{"name":"EVENTS","namespace":"PUBLIC"},
                    |"stream_state":{"cursor_incremental":"initial_sync_ongoing"}},
                    |"sourceStats":{"recordCount":123.0}
                    |}
                """.trimMargin(),
                )
                .map { Jsons.readTree(it) },
            checkpoint.map { Jsons.valueToTree<JsonNode>(it) },
        )
        Assertions.assertEquals(emptyList<AirbyteStateMessage>(), stateManager.checkpoint())
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
}]}""",
    )
    @Property(
        name = "airbyte.connector.state.json",
        value =
            """
[{"type": "STREAM", "stream": {
    "stream_descriptor": { "name": "EVENTS", "namespace": "PUBLIC" },
    "stream_state": { "cursor_incremental": "initial_sync_ongoing" }
}}]""",
    )
    fun testFullRefreshWarmStart() {
        // test current state
        val stream: Stream = prelude(ConfiguredSyncMode.FULL_REFRESH, listOf("ID"))
        Assertions.assertEquals(
            Jsons.readTree("{\"cursor_incremental\": \"initial_sync_ongoing\"}"),
            stateManager.scoped(stream).current(),
        )
        Assertions.assertEquals(listOf<CatalogValidationFailure>(), handler.get())
        // update state manager with fake work result
        stateManager
            .scoped(stream)
            .set(Jsons.readTree("{\"cursor_incremental\":\"cursor_checkpoint\"}"), 456)
        // test checkpoint messages
        val checkpoint: List<AirbyteStateMessage> = stateManager.checkpoint()
        Assertions.assertEquals(
            listOf(
                    """{
                    |"type":"STREAM",
                    |"stream":{"stream_descriptor":{"name":"EVENTS","namespace":"PUBLIC"},
                    |"stream_state":{"cursor_incremental":"cursor_checkpoint"}},
                    |"sourceStats":{"recordCount":456.0}
                    |}
                """.trimMargin(),
                )
                .map { Jsons.readTree(it) },
            checkpoint.map { Jsons.valueToTree<JsonNode>(it) },
        )
        Assertions.assertEquals(emptyList<AirbyteStateMessage>(), stateManager.checkpoint())
    }

    private fun prelude(
        expectedSyncMode: ConfiguredSyncMode,
        expectedPrimaryKey: List<String>? = null,
        expectedCursor: String? = null,
    ): Stream {
        Assertions.assertEquals(1, stateManager.feeds.size)
        Assertions.assertEquals(1, stateManager.feeds.mapNotNull { it as? Stream }.size)
        val eventsStream: Stream = stateManager.feeds.mapNotNull { it as? Stream }.first()
        Assertions.assertEquals("EVENTS", eventsStream.name)
        Assertions.assertEquals(listOf("MSG", "ID", "TS"), eventsStream.fields.map { it.id })
        Assertions.assertEquals(expectedSyncMode, eventsStream.configuredSyncMode)
        Assertions.assertEquals(
            expectedPrimaryKey,
            eventsStream.configuredPrimaryKey?.map { it.id },
        )
        Assertions.assertEquals(expectedCursor, eventsStream.configuredCursor?.id)
        return eventsStream
    }

    private fun streamID(name: String): StreamIdentifier =
        StreamIdentifier.from(StreamDescriptor().withName(name).withNamespace("PUBLIC"))

    companion object {
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
    }
}
