/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.github.oshai.kotlinlogging.KotlinLogging

private val LOGGER = KotlinLogging.logger {}

/**
 * Defensive pre-processor that rewrites a [ConfiguredAirbyteCatalog] so that cursor and primary-key
 * entries referencing columns that are not present in the stream's JSON schema (or that are empty /
 * blank strings) do not reach the SQL generator.
 *
 * Without this pass, invalid entries propagate into the generated dedup SQL and surface as
 * Redshift-level errors such as:
 * * `ERROR: column "id" does not exist in intermediate_data` (primary key references a column that
 * is not in the stream schema), or
 * * `ERROR: zero-length delimited identifier at or near """"` (cursor field is `[""]`).
 *
 * Both variants are reported against destination-redshift but originate from invalid
 * `ConfiguredAirbyteCatalog` state (a blank cursor or a stale primary key after a source schema
 * change). The catalog is cloned so the caller's instance is not mutated.
 */
object RedshiftCatalogSanitizer {

    fun sanitize(catalog: ConfiguredAirbyteCatalog): ConfiguredAirbyteCatalog {
        val cloned = Jsons.clone(catalog)
        for (stream in cloned.streams) {
            sanitizeStream(stream)
        }
        return cloned
    }

    private fun sanitizeStream(stream: ConfiguredAirbyteStream) {
        val streamLabel = describeStream(stream)
        val schemaColumns = topLevelSchemaColumns(stream.stream?.jsonSchema)

        // Cursor: drop blank entries; drop entries that are not present in the schema.
        val originalCursor: List<String> = stream.cursorField ?: emptyList()
        val sanitizedCursor = originalCursor.filter { it.isNotBlank() }
        val blankCursorDropped = originalCursor.size - sanitizedCursor.size
        if (blankCursorDropped > 0) {
            LOGGER.warn {
                "Dropping $blankCursorDropped blank cursor field entr" +
                    (if (blankCursorDropped == 1) "y" else "ies") +
                    " for stream $streamLabel; treating as no cursor."
            }
        }
        val missingCursorFromSchema =
            if (schemaColumns != null) {
                sanitizedCursor.filter { it !in schemaColumns }
            } else {
                emptyList()
            }
        if (missingCursorFromSchema.isNotEmpty()) {
            LOGGER.warn {
                "Cursor field(s) $missingCursorFromSchema for stream $streamLabel are not present in the stream JSON schema; treating as no cursor."
            }
        }
        val finalCursor =
            if (schemaColumns != null) {
                sanitizedCursor.filter { it in schemaColumns }
            } else {
                sanitizedCursor
            }
        if (finalCursor != originalCursor) {
            stream.cursorField = finalCursor
        }

        // Primary key: drop entries whose top-level column is blank or not in the schema. In DEDUP
        // mode, throw a clear config error if no valid PK columns remain.
        val originalPk: List<List<String>> = stream.primaryKey ?: emptyList()
        val sanitizedPk =
            originalPk.filter { path ->
                path.isNotEmpty() && path[0].isNotBlank() && isPkInSchema(path, schemaColumns)
            }
        if (sanitizedPk.size != originalPk.size) {
            val dropped =
                (originalPk - sanitizedPk.toSet()).map { it.joinToString(".", prefix = "[", postfix = "]") }
            LOGGER.warn {
                "Dropping primary key entr${if (dropped.size == 1) "y" else "ies"} $dropped for stream $streamLabel: column is blank or not present in the stream JSON schema."
            }
            stream.primaryKey = sanitizedPk
        }

        if (
            stream.destinationSyncMode == DestinationSyncMode.APPEND_DEDUP && sanitizedPk.isEmpty()
        ) {
            val originalPkDescription =
                originalPk.joinToString(prefix = "[", postfix = "]") {
                    it.joinToString(".", prefix = "[", postfix = "]")
                }
            throw ConfigErrorException(
                "Stream $streamLabel is configured for deduplication but no configured primary key column is present in the stream schema (configured primary key: $originalPkDescription). Re-discover the source schema or correct the primary key configuration."
            )
        }
    }

    private fun isPkInSchema(path: List<String>, schemaColumns: Set<String>?): Boolean {
        if (schemaColumns == null) {
            // Schema could not be parsed; trust the configured PK rather than mass-dropping it.
            return true
        }
        // Typing-deduping in the Java CDK only supports top-level primary keys, so it is sufficient
        // to verify the first element of the path.
        return path[0] in schemaColumns
    }

    /**
     * Returns the set of top-level column names declared in the stream JSON schema, or null if the
     * schema is unavailable or does not declare an `object` with `properties`.
     */
    private fun topLevelSchemaColumns(jsonSchema: JsonNode?): Set<String>? {
        if (jsonSchema == null) {
            return null
        }
        val properties = jsonSchema.get("properties")
        if (properties == null || !properties.isObject) {
            return null
        }
        val columns = LinkedHashSet<String>()
        properties.fieldNames().forEachRemaining { columns.add(it) }
        return columns
    }

    private fun describeStream(stream: ConfiguredAirbyteStream): String {
        val namespace = stream.stream?.namespace
        val name = stream.stream?.name ?: "<unknown>"
        return if (namespace.isNullOrEmpty()) name else "$namespace.$name"
    }
}
