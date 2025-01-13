/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.InputState
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.output.BufferingCatalogValidationFailureHandler
import io.airbyte.cdk.output.CatalogValidationFailure
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.micronaut.context.annotation.Property
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(rebuildContext = true)
@Property(name = "airbyte.connector.config.host", value = "localhost")
@Property(name = "airbyte.connector.config.database", value = "testdb")
@Property(name = "airbyte.connector.config.cursor.cursor_method", value = "cdc")
@Property(name = "metadata.resource", value = "discover/metadata-valid.json")
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
    @Property(name = "airbyte.connector.catalog.resource", value = "fakesource/cdc-catalog.json")
    @Property(
        name = "airbyte.connector.state.json",
        value =
            """
{"type": "GLOBAL", "global": {
    "shared_state": { "cdc": {} },
    "stream_states": [{
        "stream_descriptor": { "name": "BAR", "namespace": "FOO" },
        "stream_state": { "primary_key": {} }
}]}}""",
    )
    fun testStreamInStateButNotInCatalog() {
        prelude()
        Assertions.assertEquals(listOf<CatalogValidationFailure>(), handler.get())
    }

    @Test
    @Property(name = "airbyte.connector.catalog.resource", value = "fakesource/cdc-catalog.json")
    @Property(name = "airbyte.connector.state.json", value = "[]")
    fun testColdStart() {
        val streams: Streams = prelude()
        // test current state
        Assertions.assertNull(stateManager.scoped(streams.global).current())
        Assertions.assertNull(stateManager.scoped(streams.kv).current())
        Assertions.assertNull(stateManager.scoped(streams.events).current())
        Assertions.assertEquals(listOf<CatalogValidationFailure>(), handler.get())
        // update state manager with fake work results
        stateManager.scoped(streams.global).set(Jsons.readTree("{\"cdc\":\"starting\"}"), 0L)
        stateManager.scoped(streams.kv).set(Jsons.readTree("{\"initial_sync\":\"ongoing\"}"), 123L)
        stateManager
            .scoped(streams.events)
            .set(Jsons.readTree("{\"full_refresh\":\"ongoing\"}"), 456L)
        // test checkpoint messages
        val checkpoint: List<AirbyteStateMessage> = stateManager.checkpoint()
        Assertions.assertEquals(
            listOf(
                    """{
                    |"type":"GLOBAL",
                    |"global":{"shared_state":{"cdc":"starting"},
                    |"stream_states":[
                    |{"stream_descriptor":{"name":"KV","namespace":"PUBLIC"},
                    |"stream_state":{"initial_sync":"ongoing"}},
                    |{"stream_descriptor":{"name":"EVENTS","namespace":"PUBLIC"},
                    |"stream_state":{"full_refresh":"ongoing"}}
                    |]},
                    |"sourceStats":{"recordCount":579.0}
                    |}
                """.trimMargin(),
                )
                .map { Jsons.readTree(it) },
            checkpoint.map { Jsons.valueToTree<JsonNode>(it) },
        )
        Assertions.assertEquals(emptyList<AirbyteStateMessage>(), stateManager.checkpoint())
    }

    @Test
    @Property(name = "airbyte.connector.catalog.resource", value = "fakesource/cdc-catalog.json")
    @Property(
        name = "airbyte.connector.state.json",
        value = """{"type": "GLOBAL", "global": { "shared_state": { "cdc": "starting" } } }""",
    )
    fun testInitialSyncColdStart() {
        val streams: Streams = prelude()
        // test current state
        Assertions.assertEquals(
            Jsons.readTree("{ \"cdc\": \"starting\" }"),
            stateManager.scoped(streams.global).current(),
        )
        Assertions.assertNull(stateManager.scoped(streams.kv).current())
        Assertions.assertNull(stateManager.scoped(streams.events).current())
        Assertions.assertEquals(listOf<CatalogValidationFailure>(), handler.get())
        // update state manager with fake work results for the kv stream
        stateManager.scoped(streams.kv).set(Jsons.readTree("{\"initial_sync\":\"ongoing\"}"), 123L)
        // test checkpoint messages
        val checkpointOngoing: List<AirbyteStateMessage> = stateManager.checkpoint()
        Assertions.assertEquals(
            listOf(
                    """{
                    |"type":"GLOBAL",
                    |"global":{"shared_state":{"cdc":"starting"},
                    |"stream_states":[
                    |{"stream_descriptor":{"name":"KV","namespace":"PUBLIC"},
                    |"stream_state":{"initial_sync":"ongoing"}},
                    |{"stream_descriptor":{"name":"EVENTS","namespace":"PUBLIC"},
                    |"stream_state":{}}
                    |]},"sourceStats":{"recordCount":123.0}
                    |}
                """.trimMargin(),
                )
                .map { Jsons.readTree(it) },
            checkpointOngoing.map { Jsons.valueToTree<JsonNode>(it) },
        )
        Assertions.assertEquals(emptyList<AirbyteStateMessage>(), stateManager.checkpoint())
        // update state manager with more fake work results for the kv stream
        stateManager.scoped(streams.kv).set(Jsons.readTree("{\"initial_sync\":\"ongoing\"}"), 456L)
        stateManager
            .scoped(streams.kv)
            .set(Jsons.readTree("{\"initial_sync\":\"completed\"}"), 789L)
        // test checkpoint messages
        val checkpointCompleted: List<AirbyteStateMessage> = stateManager.checkpoint()
        Assertions.assertEquals(
            listOf(
                    """{
                    |"type":"GLOBAL",
                    |"global":{"shared_state":{"cdc":"starting"},
                    |"stream_states":[
                    |{"stream_descriptor":{"name":"KV","namespace":"PUBLIC"},
                    |"stream_state":{"initial_sync":"completed"}},
                    |{"stream_descriptor":{"name":"EVENTS","namespace":"PUBLIC"},
                    |"stream_state":{}}
                    |]},"sourceStats":{"recordCount":1245.0}
                    |}
                """.trimMargin(),
                )
                .map { Jsons.readTree(it) },
            checkpointCompleted.map { Jsons.valueToTree<JsonNode>(it) },
        )
        Assertions.assertEquals(emptyList<AirbyteStateMessage>(), stateManager.checkpoint())
    }

    @Test
    @Property(name = "airbyte.connector.catalog.resource", value = "fakesource/cdc-catalog.json")
    @Property(
        name = "airbyte.connector.state.json",
        value =
            """
{"type": "GLOBAL", "global": {
    "shared_state": { "cdc": "starting" },
    "stream_states": [{
        "stream_descriptor": { "name": "KV", "namespace": "PUBLIC" },
        "stream_state": { "initial_sync": "ongoing" }
}]}}""",
    )
    fun testInitialSyncWarmStart() {
        val streams: Streams = prelude()
        // test current state
        Assertions.assertEquals(
            Jsons.readTree("{ \"cdc\": \"starting\" }"),
            stateManager.scoped(streams.global).current(),
        )
        Assertions.assertEquals(
            Jsons.readTree("{ \"initial_sync\": \"ongoing\" }"),
            stateManager.scoped(streams.kv).current(),
        )
        Assertions.assertNull(stateManager.scoped(streams.events).current())
        Assertions.assertEquals(listOf<CatalogValidationFailure>(), handler.get())
        // update state manager with fake work results
        stateManager
            .scoped(streams.kv)
            .set(Jsons.readTree("{\"initial_sync\":\"completed\"}"), 789L)
        // test checkpoint messages
        val checkpoint: List<AirbyteStateMessage> = stateManager.checkpoint()
        Assertions.assertEquals(
            listOf(
                    """{
                    |"type":"GLOBAL",
                    |"global":{"shared_state":{"cdc":"starting"},
                    |"stream_states":[
                    |{"stream_descriptor":{"name":"KV","namespace":"PUBLIC"},
                    |"stream_state":{"initial_sync":"completed"}},
                    |{"stream_descriptor":{"name":"EVENTS","namespace":"PUBLIC"},
                    |"stream_state":{}}
                    |]},"sourceStats":{"recordCount":789.0}
                    |}
                """.trimMargin(),
                )
                .map { Jsons.readTree(it) },
            checkpoint.map { Jsons.valueToTree<JsonNode>(it) },
        )
        Assertions.assertEquals(emptyList<AirbyteStateMessage>(), stateManager.checkpoint())
    }

    @Test
    @Property(name = "airbyte.connector.catalog.resource", value = "fakesource/cdc-catalog.json")
    @Property(
        name = "airbyte.connector.state.json",
        value =
            """
{"type": "GLOBAL", "global": {
    "shared_state": { "cdc": "starting" },
    "stream_states": [{
        "stream_descriptor": { "name": "KV", "namespace": "PUBLIC" },
        "stream_state": { "initial_sync": "completed" }
}]}}""",
    )
    fun testIncrementalWarmStart() {
        val streams: Streams = prelude()
        // test current state
        Assertions.assertEquals(
            Jsons.readTree("{ \"cdc\": \"starting\" }"),
            stateManager.scoped(streams.global).current(),
        )
        Assertions.assertEquals(
            Jsons.readTree("{ \"initial_sync\": \"completed\" }"),
            stateManager.scoped(streams.kv).current(),
        )
        Assertions.assertNull(stateManager.scoped(streams.events).current())
        Assertions.assertEquals(listOf<CatalogValidationFailure>(), handler.get())
        // update state manager with fake work results
        stateManager.scoped(streams.global).set(Jsons.readTree("{\"cdc\":\"ongoing\"}"), 741L)
        // test checkpoint messages
        val checkpoint: List<AirbyteStateMessage> = stateManager.checkpoint()
        Assertions.assertEquals(
            listOf(
                    """{
                    |"type":"GLOBAL",
                    |"global":{"shared_state":{"cdc":"ongoing"},
                    |"stream_states":[
                    |{"stream_descriptor":{"name":"KV","namespace":"PUBLIC"},
                    |"stream_state":{"initial_sync":"completed"}},
                    |{"stream_descriptor":{"name":"EVENTS","namespace":"PUBLIC"},
                    |"stream_state":{}}
                    |]},
                    |"sourceStats":{"recordCount":741.0}
                    |}
                """.trimMargin(),
                )
                .map { Jsons.readTree(it) },
            checkpoint.map { Jsons.valueToTree<JsonNode>(it) },
        )
        Assertions.assertEquals(emptyList<AirbyteStateMessage>(), stateManager.checkpoint())
    }

    private fun prelude(): Streams {
        val globals: List<Global> = stateManager.feeds.mapNotNull { it as? Global }
        Assertions.assertEquals(1, globals.size)
        val global: Global = globals.first()
        val streams: List<Stream> = stateManager.feeds.mapNotNull { it as? Stream }
        Assertions.assertEquals(2, streams.size)
        Assertions.assertEquals(1, global.streams.size)
        val kv: Stream = global.streams.first()
        Assertions.assertEquals("KV", kv.name)
        Assertions.assertEquals(
            listOf("V", "K", "_ab_cdc_lsn", "_ab_cdc_updated_at", "_ab_cdc_deleted_at"),
            kv.schema.map { it.id },
        )
        Assertions.assertEquals(listOf("K"), kv.configuredPrimaryKey?.map { it.id })
        Assertions.assertEquals(ConfiguredSyncMode.INCREMENTAL, kv.configuredSyncMode)
        val events: Stream = streams.filter { it.id != kv.id }.first()
        Assertions.assertEquals("EVENTS", events.name)
        Assertions.assertEquals(listOf("MSG", "ID", "TS"), events.fields.map { it.id })
        Assertions.assertEquals(listOf("ID"), events.configuredPrimaryKey?.map { it.id })
        Assertions.assertEquals(ConfiguredSyncMode.FULL_REFRESH, events.configuredSyncMode)
        return Streams(global, kv, events)
    }

    data class Streams(
        val global: Global,
        val kv: Stream,
        val events: Stream,
    )
}
