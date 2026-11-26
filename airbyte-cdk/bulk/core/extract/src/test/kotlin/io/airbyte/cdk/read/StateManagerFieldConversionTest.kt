/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.InputState
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.output.BufferingCatalogValidationFailureHandler
import io.airbyte.cdk.output.CatalogValidationFailure
import io.airbyte.cdk.output.FieldSourceTypeMismatch
import io.airbyte.cdk.output.UnsupportedFieldConversion
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.micronaut.context.annotation.Property
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * Validation of the `airbyte_source_type` key against the `KV` table of
 * `discover/metadata-valid.json`, where `K` is an integer column and `V` is a string column.
 */
@MicronautTest(rebuildContext = true)
@Property(name = "airbyte.connector.config.host", value = "localhost")
@Property(name = "airbyte.connector.config.database", value = "testdb")
@Property(name = "airbyte.connector.config.cursor.cursor_method", value = "user_defined")
@Property(name = "metadata.resource", value = "discover/metadata-valid.json")
@Property(name = "airbyte.connector.data-channel.medium", value = "STDIO")
@Property(name = "airbyte.connector.data-channel.format", value = "JSONL")
@Property(name = "airbyte.connector.state.json", value = "[]")
class StateManagerFieldConversionTest {
    @Inject lateinit var config: SourceConfiguration

    @Inject lateinit var configuredCatalog: ConfiguredAirbyteCatalog

    @Inject lateinit var inputState: InputState

    @Inject lateinit var stateManagerFactory: StateManagerFactory

    @Inject lateinit var handler: BufferingCatalogValidationFailureHandler

    val stateManager: StateManager by lazy {
        stateManagerFactory.create(config, configuredCatalog, inputState)
    }

    val streams: List<Stream>
        get() = stateManager.feeds.filterIsInstance<Stream>()

    @Test
    @Property(
        name = "airbyte.connector.catalog.json",
        value =
            """
{"streams": [{
    "stream": {
        "name": "KV",
        "json_schema": {"type": "object", "properties": {
            "K": {"type": "string", "airbyte_source_type": "integer"},
            "V": {"type": "string"}
        }},
        "supported_sync_modes": ["full_refresh", "incremental"],
        "namespace": "PUBLIC"
    },
    "sync_mode": "full_refresh",
    "destination_sync_mode": "overwrite"
}]}""",
    )
    fun testConversion() {
        Assertions.assertEquals(listOf<CatalogValidationFailure>(), handler.get())
        val stream: Stream = streams.single()
        Assertions.assertEquals(
            mapOf(
                "K" to FieldConversion(LeafAirbyteSchemaType.INTEGER, LeafAirbyteSchemaType.STRING),
            ),
            stream.fieldConversions,
        )
        // The reader keeps the source type, the records get the configured type.
        Assertions.assertEquals(
            LeafAirbyteSchemaType.INTEGER,
            stream.schema.single { it.id == "K" }.type.airbyteSchemaType,
        )
        Assertions.assertEquals(
            LeafAirbyteSchemaType.STRING,
            stream.outputSchema.single { it.id == "K" }.type.airbyteSchemaType,
        )
    }

    @Test
    @Property(
        name = "airbyte.connector.catalog.json",
        value =
            """
{"streams": [{
    "stream": {
        "name": "KV",
        "json_schema": {"type": "object", "properties": {
            "K": {"type": "number", "airbyte_type": "integer", "airbyte_source_type": "integer"},
            "V": {"type": "string", "airbyte_source_type": "string"}
        }},
        "supported_sync_modes": ["full_refresh", "incremental"],
        "namespace": "PUBLIC"
    },
    "sync_mode": "full_refresh",
    "destination_sync_mode": "overwrite"
}]}""",
    )
    fun testSourceTypeSameAsConfiguredType() {
        Assertions.assertEquals(listOf<CatalogValidationFailure>(), handler.get())
        Assertions.assertEquals(
            emptyMap<String, FieldConversion>(),
            streams.single().fieldConversions,
        )
    }

    @Test
    @Property(
        name = "airbyte.connector.catalog.json",
        value =
            """
{"streams": [{
    "stream": {
        "name": "KV",
        "json_schema": {"type": "object", "properties": {
            "K": {"type": "string", "airbyte_source_type": "boolean"},
            "V": {"type": "string"}
        }},
        "supported_sync_modes": ["full_refresh", "incremental"],
        "namespace": "PUBLIC"
    },
    "sync_mode": "full_refresh",
    "destination_sync_mode": "overwrite"
}]}""",
    )
    fun testSourceTypeChangedAgain() {
        Assertions.assertEquals(listOf<Stream>(), streams)
        Assertions.assertEquals(
            listOf(FieldSourceTypeMismatch(KV, "K", "boolean", LeafAirbyteSchemaType.INTEGER)),
            handler.get(),
        )
    }

    @Test
    @Property(
        name = "airbyte.connector.catalog.json",
        value =
            """
{"streams": [{
    "stream": {
        "name": "KV",
        "json_schema": {"type": "object", "properties": {
            "K": {"type": "string", "airbyte_source_type": "bogus"},
            "V": {"type": "string"}
        }},
        "supported_sync_modes": ["full_refresh", "incremental"],
        "namespace": "PUBLIC"
    },
    "sync_mode": "full_refresh",
    "destination_sync_mode": "overwrite"
}]}""",
    )
    fun testUnknownSourceType() {
        Assertions.assertEquals(listOf<Stream>(), streams)
        Assertions.assertEquals(
            listOf(FieldSourceTypeMismatch(KV, "K", "bogus", LeafAirbyteSchemaType.INTEGER)),
            handler.get(),
        )
    }

    @Test
    @Property(
        name = "airbyte.connector.catalog.json",
        value =
            """
{"streams": [{
    "stream": {
        "name": "KV",
        "json_schema": {"type": "object", "properties": {
            "K": {"type": "boolean", "airbyte_source_type": "integer"},
            "V": {"type": "string"}
        }},
        "supported_sync_modes": ["full_refresh", "incremental"],
        "namespace": "PUBLIC"
    },
    "sync_mode": "full_refresh",
    "destination_sync_mode": "overwrite"
}]}""",
    )
    fun testUnsupportedConversion() {
        Assertions.assertEquals(listOf<Stream>(), streams)
        Assertions.assertEquals(
            listOf(
                UnsupportedFieldConversion(
                    KV,
                    "K",
                    LeafAirbyteSchemaType.INTEGER,
                    LeafAirbyteSchemaType.BOOLEAN,
                ),
            ),
            handler.get(),
        )
    }

    @Test
    @Property(
        name = "airbyte.connector.catalog.json",
        value =
            """
{"streams": [{
    "stream": {
        "name": "KV",
        "json_schema": {"type": "object", "properties": {
            "K": {"type": "string", "airbyte_source_type": "integer"},
            "V": {"type": "string"}
        }},
        "supported_sync_modes": ["full_refresh", "incremental"],
        "namespace": "PUBLIC"
    },
    "sync_mode": "full_refresh",
    "primary_key": [["K"]],
    "destination_sync_mode": "append_dedup"
}]}""",
    )
    fun testDedupPrimaryKeyIsNotConverted() {
        Assertions.assertEquals(listOf<Stream>(), streams)
        Assertions.assertEquals(
            listOf(
                UnsupportedFieldConversion(
                    KV,
                    "K",
                    LeafAirbyteSchemaType.INTEGER,
                    LeafAirbyteSchemaType.STRING,
                    isPrimaryKeyOrCursor = true,
                ),
            ),
            handler.get(),
        )
    }

    @Test
    @Property(
        name = "airbyte.connector.catalog.json",
        value =
            """
{"streams": [{
    "stream": {
        "name": "KV",
        "json_schema": {"type": "object", "properties": {
            "K": {"type": "string", "airbyte_source_type": "integer"},
            "V": {"type": "string"}
        }},
        "supported_sync_modes": ["full_refresh", "incremental"],
        "namespace": "PUBLIC"
    },
    "sync_mode": "full_refresh",
    "primary_key": [["K"]],
    "destination_sync_mode": "overwrite"
}]}""",
    )
    fun testPrimaryKeyWithoutDedupIsConverted() {
        Assertions.assertEquals(listOf<CatalogValidationFailure>(), handler.get())
        Assertions.assertEquals(setOf("K"), streams.single().fieldConversions.keys)
    }

    @Test
    @Property(
        name = "airbyte.connector.catalog.json",
        value =
            """
{"streams": [{
    "stream": {
        "name": "KV",
        "json_schema": {"type": "object", "properties": {
            "K": {"type": "string", "airbyte_source_type": "integer"},
            "V": {"type": "string"}
        }},
        "supported_sync_modes": ["full_refresh", "incremental"],
        "namespace": "PUBLIC"
    },
    "sync_mode": "incremental",
    "cursor_field": ["K"],
    "destination_sync_mode": "append"
}]}""",
    )
    fun testIncrementalCursorIsNotConverted() {
        Assertions.assertEquals(listOf<Stream>(), streams)
        Assertions.assertEquals(
            listOf(
                UnsupportedFieldConversion(
                    KV,
                    "K",
                    LeafAirbyteSchemaType.INTEGER,
                    LeafAirbyteSchemaType.STRING,
                    isPrimaryKeyOrCursor = true,
                ),
            ),
            handler.get(),
        )
    }

    companion object {
        val KV: StreamIdentifier =
            StreamIdentifier.from(StreamDescriptor().withName("KV").withNamespace("PUBLIC"))
    }
}
