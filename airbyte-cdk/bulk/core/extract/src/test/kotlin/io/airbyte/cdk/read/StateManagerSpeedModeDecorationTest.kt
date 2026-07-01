/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import io.airbyte.cdk.command.InputState
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.output.BufferingCatalogValidationFailureHandler
import io.airbyte.cdk.output.CatalogValidationFailure
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.micronaut.context.annotation.Property
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * Tests for meta field decoration of full refresh streams in a global (CDC) sync, across the
 * various data channel medium/format combinations.
 *
 * The key behavior under test is the "speed mode" (`SOCKET` + `PROTOBUF`) branch of
 * [StateManagerFactory.forGlobal], where records do not carry field names and therefore must match
 * the catalog schema exactly. A full refresh stream is only decorated with the global meta fields
 * (`_ab_cdc_lsn`, `_ab_cdc_updated_at`, `_ab_cdc_deleted_at`) when the stream has BOTH a
 * source-defined primary key AND a configured primary key.
 *
 * The edge case this guards against: a table with no source-defined primary key (hence ineligible
 * for CDC incremental) that is configured as full refresh append+dedup. Such a stream has a
 * configured primary key but no source-defined one, and its catalog schema does NOT contain the
 * meta fields. Decorating its records would misalign fields the destination cannot resolve in
 * speed mode.
 */
@MicronautTest(rebuildContext = true)
@Property(name = "airbyte.connector.config.host", value = "localhost")
@Property(name = "airbyte.connector.config.database", value = "testdb")
@Property(name = "airbyte.connector.config.cursor.cursor_method", value = "cdc")
@Property(name = "metadata.resource", value = "discover/metadata-speed-mode.json")
@Property(name = "airbyte.connector.data-channel.medium", value = "SOCKET")
@Property(name = "airbyte.connector.data-channel.format", value = "PROTOBUF")
class StateManagerSpeedModeDecorationTest {
    @Inject lateinit var config: SourceConfiguration

    @Inject lateinit var configuredCatalog: ConfiguredAirbyteCatalog

    @Inject lateinit var inputState: InputState

    @Inject lateinit var stateManagerFactory: StateManagerFactory

    @Inject lateinit var handler: BufferingCatalogValidationFailureHandler

    val stateManager: StateManager by lazy {
        stateManagerFactory.create(config, configuredCatalog, inputState)
    }

    /**
     * The edge case from the PR: SOCKET/PROTOBUF full refresh stream with a configured primary key
     * but NO source-defined primary key must NOT be decorated.
     */
    @Test
    @Property(name = "airbyte.connector.state.json", value = "[]")
    @Property(
        name = "airbyte.connector.catalog.json",
        value = FULL_REFRESH_NO_PK_WITH_CONFIGURED_PK,
    )
    fun testProtobufFullRefreshNoSourcePkNotDecorated() {
        assertNoValidationFailures()
        assertNotDecorated("NO_PK")
    }

    /** SOCKET/PROTOBUF full refresh stream with both source and configured primary keys: decorated. */
    @Test
    @Property(name = "airbyte.connector.state.json", value = "[]")
    @Property(
        name = "airbyte.connector.catalog.json",
        value = FULL_REFRESH_WITH_SOURCE_AND_CONFIGURED_PK,
    )
    fun testProtobufFullRefreshWithBothPksDecorated() {
        assertNoValidationFailures()
        assertDecorated("EVENTS")
    }

    /**
     * SOCKET/PROTOBUF full refresh stream with a source-defined primary key but no configured
     * primary key must NOT be decorated.
     */
    @Test
    @Property(name = "airbyte.connector.state.json", value = "[]")
    @Property(
        name = "airbyte.connector.catalog.json",
        value = FULL_REFRESH_WITH_SOURCE_PK_NO_CONFIGURED_PK,
    )
    fun testProtobufFullRefreshNoConfiguredPkNotDecorated() {
        assertNoValidationFailures()
        assertNotDecorated("EVENTS")
    }

    /** SOCKET/PROTOBUF full refresh stream with neither primary key must NOT be decorated. */
    @Test
    @Property(name = "airbyte.connector.state.json", value = "[]")
    @Property(
        name = "airbyte.connector.catalog.json",
        value = FULL_REFRESH_NO_PK_NO_CONFIGURED_PK,
    )
    fun testProtobufFullRefreshNoPksNotDecorated() {
        assertNoValidationFailures()
        assertNotDecorated("NO_PK")
    }

    /**
     * Control: an incremental stream in global mode is always decorated regardless of medium/format
     * or the source-defined primary key check.
     */
    @Test
    @Property(
        name = "airbyte.connector.state.json",
        value = """{"type": "GLOBAL", "global": { "shared_state": { "cdc": "starting" } } }""",
    )
    @Property(name = "airbyte.connector.catalog.json", value = INCREMENTAL_KV)
    fun testProtobufIncrementalAlwaysDecorated() {
        assertNoValidationFailures()
        assertDecorated("KV")
    }

    /**
     * SOCKET/JSONL keys decoration off the configured primary key ONLY (the source-defined primary
     * key is not consulted). This documents the intentional divergence from PROTOBUF for the edge
     * case above.
     */
    @Test
    @Property(name = "airbyte.connector.data-channel.format", value = "JSONL")
    @Property(name = "airbyte.connector.state.json", value = "[]")
    @Property(
        name = "airbyte.connector.catalog.json",
        value = FULL_REFRESH_NO_PK_WITH_CONFIGURED_PK,
    )
    fun testJsonlFullRefreshNoSourcePkStillDecorated() {
        assertNoValidationFailures()
        assertDecorated("NO_PK")
    }

    /** Legacy STDIO/JSONL never decorates full refresh streams. */
    @Test
    @Property(name = "airbyte.connector.data-channel.medium", value = "STDIO")
    @Property(name = "airbyte.connector.data-channel.format", value = "JSONL")
    @Property(name = "airbyte.connector.state.json", value = "[]")
    @Property(
        name = "airbyte.connector.catalog.json",
        value = FULL_REFRESH_WITH_SOURCE_AND_CONFIGURED_PK,
    )
    fun testStdioFullRefreshNotDecorated() {
        assertNoValidationFailures()
        assertNotDecorated("EVENTS")
    }

    private fun assertNoValidationFailures() {
        Assertions.assertEquals(listOf<CatalogValidationFailure>(), handler.get())
    }

    private fun streamByName(name: String): Stream =
        stateManager.feeds.mapNotNull { it as? Stream }.first { it.name == name }

    private fun schemaIds(name: String): List<String> = streamByName(name).schema.map { it.id }

    private fun assertDecorated(name: String) {
        val ids = schemaIds(name)
        Assertions.assertTrue(
            ids.containsAll(META_FIELD_IDS),
            "expected stream $name schema $ids to contain meta fields $META_FIELD_IDS",
        )
    }

    private fun assertNotDecorated(name: String) {
        val ids = schemaIds(name)
        Assertions.assertTrue(
            META_FIELD_IDS.none { it in ids },
            "expected stream $name schema $ids to contain no meta fields $META_FIELD_IDS",
        )
    }

    companion object {
        val META_FIELD_IDS = listOf("_ab_cdc_lsn", "_ab_cdc_updated_at", "_ab_cdc_deleted_at")

        // EVENTS has a source-defined primary key ([["ID"]]) in the metadata resource.
        const val FULL_REFRESH_WITH_SOURCE_AND_CONFIGURED_PK =
            """{"streams": [{
    "stream": {
        "name": "EVENTS",
        "json_schema": { "type": "object", "properties": {
            "MSG": { "type": "string" },
            "ID": { "type": "string" },
            "TS": { "type": "string", "format": "date-time", "airbyte_type": "timestamp_with_timezone" }
        }},
        "supported_sync_modes": ["full_refresh", "incremental"],
        "source_defined_cursor": false,
        "default_cursor_field": [],
        "source_defined_primary_key": [["ID"]],
        "namespace": "PUBLIC"
    },
    "sync_mode": "full_refresh",
    "cursor_field": [],
    "destination_sync_mode": "append_dedup",
    "primary_key": [["ID"]]
}]}"""

        const val FULL_REFRESH_WITH_SOURCE_PK_NO_CONFIGURED_PK =
            """{"streams": [{
    "stream": {
        "name": "EVENTS",
        "json_schema": { "type": "object", "properties": {
            "MSG": { "type": "string" },
            "ID": { "type": "string" },
            "TS": { "type": "string", "format": "date-time", "airbyte_type": "timestamp_with_timezone" }
        }},
        "supported_sync_modes": ["full_refresh", "incremental"],
        "source_defined_cursor": false,
        "default_cursor_field": [],
        "source_defined_primary_key": [["ID"]],
        "namespace": "PUBLIC"
    },
    "sync_mode": "full_refresh",
    "cursor_field": [],
    "destination_sync_mode": "overwrite",
    "primary_key": []
}]}"""

        // NO_PK has no source-defined primary key ([]) in the metadata resource.
        const val FULL_REFRESH_NO_PK_WITH_CONFIGURED_PK =
            """{"streams": [{
    "stream": {
        "name": "NO_PK",
        "json_schema": { "type": "object", "properties": {
            "MSG": { "type": "string" },
            "ID": { "type": "string" },
            "TS": { "type": "string", "format": "date-time", "airbyte_type": "timestamp_with_timezone" }
        }},
        "supported_sync_modes": ["full_refresh", "incremental"],
        "source_defined_cursor": false,
        "default_cursor_field": [],
        "source_defined_primary_key": [],
        "namespace": "PUBLIC"
    },
    "sync_mode": "full_refresh",
    "cursor_field": [],
    "destination_sync_mode": "append_dedup",
    "primary_key": [["ID"]]
}]}"""

        const val FULL_REFRESH_NO_PK_NO_CONFIGURED_PK =
            """{"streams": [{
    "stream": {
        "name": "NO_PK",
        "json_schema": { "type": "object", "properties": {
            "MSG": { "type": "string" },
            "ID": { "type": "string" },
            "TS": { "type": "string", "format": "date-time", "airbyte_type": "timestamp_with_timezone" }
        }},
        "supported_sync_modes": ["full_refresh", "incremental"],
        "source_defined_cursor": false,
        "default_cursor_field": [],
        "source_defined_primary_key": [],
        "namespace": "PUBLIC"
    },
    "sync_mode": "full_refresh",
    "cursor_field": [],
    "destination_sync_mode": "overwrite",
    "primary_key": []
}]}"""

        const val INCREMENTAL_KV =
            """{"streams": [{
    "stream": {
        "name": "KV",
        "json_schema": { "type": "object", "properties": {
            "V": { "type": "string" },
            "K": { "type": "number", "airbyte_type": "integer" }
        }},
        "supported_sync_modes": ["full_refresh", "incremental"],
        "source_defined_cursor": false,
        "default_cursor_field": [],
        "source_defined_primary_key": [["K"]],
        "namespace": "PUBLIC"
    },
    "sync_mode": "incremental",
    "cursor_field": ["_ab_cdc_lsn"],
    "destination_sync_mode": "append_dedup",
    "primary_key": [["K"]]
}]}"""
    }
}
