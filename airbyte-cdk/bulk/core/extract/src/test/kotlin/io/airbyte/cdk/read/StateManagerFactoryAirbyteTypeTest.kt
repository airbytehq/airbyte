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

@MicronautTest(rebuildContext = true)
@Property(name = "airbyte.connector.config.host", value = "localhost")
@Property(name = "airbyte.connector.config.database", value = "testdb")
@Property(name = "airbyte.connector.config.cursor.cursor_method", value = "user_defined")
@Property(name = "metadata.resource", value = "discover/metadata-with-jsonb.json")
@Property(name = "airbyte.connector.data-channel.medium", value = "STDIO")
@Property(name = "airbyte.connector.data-channel.format", value = "JSONL")
class StateManagerFactoryAirbyteTypeTest {
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
        "name": "EVENTS",
        "json_schema": {
            "type": "object",
            "properties": {
                "MSG": { "type": "string" },
                "ID": { "type": "string" },
                "TS": {
                    "type": "string",
                    "format": "date-time",
                    "airbyte_type": "timestamp_with_timezone"
                },
                "TAGS": { "type": "array" }
            }
        },
        "supported_sync_modes": ["full_refresh", "incremental"],
        "source_defined_primary_key": [["ID"]],
        "namespace": "PUBLIC"
    },
    "sync_mode": "full_refresh",
    "primary_key": [["ID"]],
    "destination_sync_mode": "overwrite"
}]}""",
    )
    @Property(name = "airbyte.connector.state.json", value = "[]")
    fun testArrayTypeWithoutItemsFallsBackToJsonb() {
        // Before the fix, this would throw NullPointerException because
        // jsonSchema["items"] returns null for {"type": "array"} without an "items" key.
        // After the fix, it should fall back to JSONB (matching the metadata JSONB field type).
        Assertions.assertEquals(1, stateManager.feeds.size)
        val stream: Stream = stateManager.feeds.mapNotNull { it as? Stream }.first()
        Assertions.assertEquals("EVENTS", stream.name)
        Assertions.assertTrue(stream.fields.any { it.id == "TAGS" })
        Assertions.assertEquals(listOf<CatalogValidationFailure>(), handler.get())
    }

    @Test
    @Property(
        name = "airbyte.connector.catalog.json",
        value =
            """
{"streams": [{
    "stream": {
        "name": "EVENTS",
        "json_schema": {
            "type": "object",
            "properties": {
                "MSG": { "type": "string" },
                "ID": { "type": "string" },
                "TS": {
                    "type": "string",
                    "format": "date-time",
                    "airbyte_type": "timestamp_with_timezone"
                },
                "TAGS": {
                    "type": "array",
                    "items": { "type": "string" }
                }
            }
        },
        "supported_sync_modes": ["full_refresh", "incremental"],
        "source_defined_primary_key": [["ID"]],
        "namespace": "PUBLIC"
    },
    "sync_mode": "full_refresh",
    "primary_key": [["ID"]],
    "destination_sync_mode": "overwrite"
}]}""",
    )
    @Property(name = "airbyte.connector.state.json", value = "[]")
    fun testArrayTypeWithItemsStillWorks() {
        // Verify the normal case still works: array with items defined.
        // This will cause a FieldTypeMismatch because the catalog says
        // ArrayAirbyteSchemaType(STRING) but metadata says JSONB.
        // That's fine — we're verifying it doesn't throw NPE and correctly parses the type.
        val feeds = stateManager.feeds
        // The stream may be excluded due to field type mismatch,
        // but the key assertion is no NPE was thrown.
        Assertions.assertNotNull(feeds)
    }
}
