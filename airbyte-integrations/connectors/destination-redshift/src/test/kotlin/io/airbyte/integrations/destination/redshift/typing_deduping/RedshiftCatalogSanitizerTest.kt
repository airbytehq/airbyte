/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

/**
 * Unit tests for [RedshiftCatalogSanitizer], covering the failure modes tracked in
 * airbytehq/oncall#10111 and airbytehq/oncall#10700:
 * * empty-string cursor (`cursor_field = [""]`) that produced the zero-length delimited identifier
 * Redshift error, and
 * * primary-key entries that reference columns not present in the stream JSON schema (e.g. `"id"`),
 * which produced `column "id" does not exist in intermediate_data`.
 */
internal class RedshiftCatalogSanitizerTest {

    @Test
    fun `empty string cursor field is dropped`() {
        val catalog = catalog(stream(cursorField = listOf("")))

        val sanitized = RedshiftCatalogSanitizer.sanitize(catalog)

        assertEquals(emptyList<String>(), sanitized.streams[0].cursorField)
    }

    @Test
    fun `cursor field not present in schema is dropped`() {
        val catalog =
            catalog(
                stream(cursorField = listOf("not_a_real_field")),
            )

        val sanitized = RedshiftCatalogSanitizer.sanitize(catalog)

        assertEquals(emptyList<String>(), sanitized.streams[0].cursorField)
    }

    @Test
    fun `valid cursor field is preserved`() {
        val catalog = catalog(stream(cursorField = listOf("updated_at")))

        val sanitized = RedshiftCatalogSanitizer.sanitize(catalog)

        assertEquals(listOf("updated_at"), sanitized.streams[0].cursorField)
    }

    @Test
    fun `primary key referencing missing column is dropped in append mode`() {
        val catalog =
            catalog(
                stream(
                    destinationSyncMode = DestinationSyncMode.APPEND,
                    primaryKey = listOf(listOf("id"), listOf("name")),
                ),
            )

        val sanitized = RedshiftCatalogSanitizer.sanitize(catalog)

        // "id" is not in the schema; "name" is.
        assertEquals(listOf(listOf("name")), sanitized.streams[0].primaryKey)
    }

    @Test
    fun `dedup stream with no valid primary key throws ConfigErrorException`() {
        val catalog =
            catalog(
                stream(
                    destinationSyncMode = DestinationSyncMode.APPEND_DEDUP,
                    primaryKey = listOf(listOf("id")),
                ),
            )

        val thrown =
            assertThrows(ConfigErrorException::class.java) {
                RedshiftCatalogSanitizer.sanitize(catalog)
            }
        // Surface the offending stream and original PK in the error, so users can self-service.
        assert(thrown.message!!.contains("test_namespace.test_stream"))
        assert(thrown.message!!.contains("id"))
    }

    @Test
    fun `dedup stream with valid primary key is preserved`() {
        val catalog =
            catalog(
                stream(
                    destinationSyncMode = DestinationSyncMode.APPEND_DEDUP,
                    primaryKey = listOf(listOf("name")),
                ),
            )

        val sanitized = RedshiftCatalogSanitizer.sanitize(catalog)

        assertEquals(listOf(listOf("name")), sanitized.streams[0].primaryKey)
        // Untouched cursor.
        assertEquals(emptyList<String>(), sanitized.streams[0].cursorField)
    }

    @Test
    fun `combined empty cursor and invalid primary key in dedup stream reports PK config error`() {
        // Mirrors oncall#10111: company_attributes had cursor_field=[""] and primary_key=["id"]
        // where "id" was not in the discovered schema.
        val catalog =
            catalog(
                stream(
                    destinationSyncMode = DestinationSyncMode.APPEND_DEDUP,
                    cursorField = listOf(""),
                    primaryKey = listOf(listOf("id")),
                ),
            )

        val thrown =
            assertThrows(ConfigErrorException::class.java) {
                RedshiftCatalogSanitizer.sanitize(catalog)
            }
        assert(thrown.message!!.contains("deduplication"))
    }

    @Test
    fun `original catalog is not mutated`() {
        val original =
            catalog(
                stream(
                    destinationSyncMode = DestinationSyncMode.APPEND,
                    cursorField = listOf(""),
                    primaryKey = listOf(listOf("id")),
                ),
            )
        val snapshot = Jsons.clone(original)

        RedshiftCatalogSanitizer.sanitize(original)

        assertEquals(snapshot, original)
    }

    @Test
    fun `missing JSON schema leaves primary key untouched`() {
        val catalog =
            catalog(
                stream(
                    schema = null,
                    destinationSyncMode = DestinationSyncMode.APPEND_DEDUP,
                    primaryKey = listOf(listOf("id")),
                ),
            )

        val sanitized = RedshiftCatalogSanitizer.sanitize(catalog)

        // Without a parseable schema we cannot safely filter, so we trust the configured PK.
        assertEquals(listOf(listOf("id")), sanitized.streams[0].primaryKey)
    }

    companion object {
        private val DEFAULT_SCHEMA: JsonNode =
            Jsons.deserialize(
                """
                {
                  "type": "object",
                  "properties": {
                    "name": {"type": "string"},
                    "updated_at": {"type": "string"}
                  }
                }
                """.trimIndent(),
            )

        private fun stream(
            namespace: String? = "test_namespace",
            name: String = "test_stream",
            schema: JsonNode? = DEFAULT_SCHEMA,
            syncMode: SyncMode = SyncMode.INCREMENTAL,
            destinationSyncMode: DestinationSyncMode = DestinationSyncMode.APPEND,
            cursorField: List<String> = emptyList(),
            primaryKey: List<List<String>> = emptyList(),
        ): ConfiguredAirbyteStream {
            val airbyteStream = AirbyteStream().withNamespace(namespace).withName(name)
            if (schema != null) {
                airbyteStream.withJsonSchema(schema)
            }
            return ConfiguredAirbyteStream()
                .withStream(airbyteStream)
                .withSyncMode(syncMode)
                .withDestinationSyncMode(destinationSyncMode)
                .withCursorField(cursorField)
                .withPrimaryKey(primaryKey)
                .withGenerationId(0)
                .withMinimumGenerationId(0)
                .withSyncId(0)
        }

        private fun catalog(vararg streams: ConfiguredAirbyteStream): ConfiguredAirbyteCatalog {
            return ConfiguredAirbyteCatalog().withStreams(streams.toList())
        }
    }
}
