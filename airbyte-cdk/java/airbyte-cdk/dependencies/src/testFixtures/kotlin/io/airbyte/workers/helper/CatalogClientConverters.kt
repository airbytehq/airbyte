/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.helper

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.api.client.model.generated.*
import io.airbyte.commons.enums.Enums
import io.airbyte.commons.text.Names
import io.airbyte.protocol.models.SyncMode
import io.airbyte.validation.json.JsonValidationException
import java.util.*
import java.util.stream.Collectors

/**
 * Utilities to convert Catalog protocol to Catalog API client. This class was similar to existing
 * logic in CatalogConverter.java; But code can't be shared because the protocol model is
 * essentially converted to two different api models. Thus, if we need to change logic on either
 * place we have to take care of the other one too.
 */
object CatalogClientConverters {
    /**
     *
     * @param catalog
     * @return
     */
    fun toAirbyteProtocol(catalog: AirbyteCatalog): io.airbyte.protocol.models.AirbyteCatalog {
        val protoCatalog = io.airbyte.protocol.models.AirbyteCatalog()
        val airbyteStream =
            catalog.streams
                .stream()
                .map { stream: AirbyteStreamAndConfiguration ->
                    try {
                        return@map toConfiguredProtocol(stream.stream, stream.config)
                    } catch (e: JsonValidationException) {
                        return@map null
                    }
                }
                .toList()

        protoCatalog.withStreams(airbyteStream)
        return protoCatalog
    }

    @Throws(JsonValidationException::class)
    private fun toConfiguredProtocol(
        stream: AirbyteStream?,
        config: AirbyteStreamConfiguration?
    ): io.airbyte.protocol.models.AirbyteStream {
        if (config!!.fieldSelectionEnabled != null && config.fieldSelectionEnabled!!) {
            // Validate the selected field paths.
            if (config.selectedFields == null) {
                throw JsonValidationException(
                    "Requested field selection but no selected fields provided"
                )
            }
            val properties = stream!!.jsonSchema!!.findValue("properties")
            if (properties == null || !properties.isObject) {
                throw JsonValidationException(
                    "Requested field selection but no properties node found"
                )
            }
            for (selectedFieldInfo in config.selectedFields!!) {
                if (
                    selectedFieldInfo.fieldPath == null || selectedFieldInfo.fieldPath!!.isEmpty()
                ) {
                    throw JsonValidationException("Selected field path cannot be empty")
                }
                if (selectedFieldInfo.fieldPath!!.size > 1) {
                    // TODO(mfsiega-airbyte): support nested fields.
                    throw UnsupportedOperationException("Nested field selection not supported")
                }
            }
            // Only include the selected fields.
            // NOTE: we verified above that each selected field has at least one element in the
            // field path.
            val selectedFieldNames =
                config.selectedFields!!
                    .stream()
                    .map { field: SelectedFieldInfo -> field.fieldPath!![0] }
                    .collect(Collectors.toSet())
            // TODO(mfsiega-airbyte): we only check the top level of the cursor/primary key fields
            // because we
            // don't support filtering nested fields yet.
            if (
                config.syncMode == io.airbyte.api.client.model.generated.SyncMode.INCREMENTAL &&
                    !config.cursorField!!.isEmpty() // There is a cursor configured, AND
                    &&
                    !selectedFieldNames.contains(config.cursorField!![0])
            ) { // The cursor isn't in the selected fields.
                throw JsonValidationException(
                    "Cursor field cannot be de-selected in INCREMENTAL syncs"
                )
            }
            if (config.destinationSyncMode == DestinationSyncMode.APPEND_DEDUP) {
                for (primaryKeyComponent in config.primaryKey!!) {
                    if (!selectedFieldNames.contains(primaryKeyComponent[0])) {
                        throw JsonValidationException(
                            "Primary key field cannot be de-selected in DEDUP mode"
                        )
                    }
                }
            }
            for (selectedFieldName in selectedFieldNames) {
                if (!properties.has(selectedFieldName)) {
                    throw JsonValidationException(
                        String.format(
                            "Requested selected field %s not found in JSON schema",
                            selectedFieldName
                        )
                    )
                }
            }
            (properties as ObjectNode).retain(selectedFieldNames)
        }
        return io.airbyte.protocol.models
            .AirbyteStream()
            .withName(stream!!.name)
            .withJsonSchema(stream.jsonSchema)
            .withSupportedSyncModes(
                Enums.convertListTo(stream.supportedSyncModes!!, SyncMode::class.java)
            )
            .withSourceDefinedCursor(stream.sourceDefinedCursor)
            .withDefaultCursorField(stream.defaultCursorField)
            .withSourceDefinedPrimaryKey(
                Optional.ofNullable(stream.sourceDefinedPrimaryKey).orElse(emptyList())
            )
            .withNamespace(stream.namespace)
    }

    /** Converts a protocol AirbyteCatalog to an OpenAPI client versioned AirbyteCatalog. */
    fun toAirbyteCatalogClientApi(
        catalog: io.airbyte.protocol.models.AirbyteCatalog
    ): AirbyteCatalog {
        return AirbyteCatalog()
            .streams(
                catalog.streams
                    .stream()
                    .map { stream: io.airbyte.protocol.models.AirbyteStream ->
                        toAirbyteStreamClientApi(stream)
                    }
                    .map { s: AirbyteStream ->
                        AirbyteStreamAndConfiguration()
                            .stream(s)
                            .config(generateDefaultConfiguration(s))
                    }
                    .toList()
            )
    }

    private fun generateDefaultConfiguration(stream: AirbyteStream): AirbyteStreamConfiguration {
        val result =
            AirbyteStreamConfiguration()
                .aliasName(Names.toAlphanumericAndUnderscore(stream.name))
                .cursorField(stream.defaultCursorField)
                .destinationSyncMode(DestinationSyncMode.APPEND)
                .primaryKey(stream.sourceDefinedPrimaryKey)
                .selected(true)
        if (stream.supportedSyncModes!!.size > 0) {
            result.setSyncMode(
                Enums.convertTo(
                    stream.supportedSyncModes!![0],
                    io.airbyte.api.client.model.generated.SyncMode::class.java
                )
            )
        } else {
            result.syncMode = io.airbyte.api.client.model.generated.SyncMode.INCREMENTAL
        }
        return result
    }

    private fun toAirbyteStreamClientApi(
        stream: io.airbyte.protocol.models.AirbyteStream
    ): AirbyteStream {
        return AirbyteStream()
            .name(stream.name)
            .jsonSchema(stream.jsonSchema)
            .supportedSyncModes(
                Enums.convertListTo(
                    stream.supportedSyncModes,
                    io.airbyte.api.client.model.generated.SyncMode::class.java
                )
            )
            .sourceDefinedCursor(stream.sourceDefinedCursor)
            .defaultCursorField(stream.defaultCursorField)
            .sourceDefinedPrimaryKey(stream.sourceDefinedPrimaryKey)
            .namespace(stream.namespace)
    }
}
