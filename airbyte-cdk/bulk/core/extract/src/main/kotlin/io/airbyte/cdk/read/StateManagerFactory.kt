/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.asProtocolStreamDescriptor
import io.airbyte.cdk.command.EmptyInputState
import io.airbyte.cdk.command.GlobalInputState
import io.airbyte.cdk.command.InputState
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.StreamInputState
import io.airbyte.cdk.data.AirbyteType
import io.airbyte.cdk.data.ArrayAirbyteType
import io.airbyte.cdk.data.LeafAirbyteType
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldOrMetaField
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.output.CatalogValidationFailureHandler
import io.airbyte.cdk.output.FieldNotFound
import io.airbyte.cdk.output.FieldTypeMismatch
import io.airbyte.cdk.output.InvalidIncrementalSyncMode
import io.airbyte.cdk.output.InvalidPrimaryKey
import io.airbyte.cdk.output.MultipleStreamsFound
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.output.StreamHasNoFields
import io.airbyte.cdk.output.StreamNotFound
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import jakarta.inject.Singleton

/**
 * A factory for instantiating [StateManager] based on the inputs of a READ. These inputs are
 * deliberately not injected here to make testing easier.
 */
@Singleton
class StateManagerFactory(
    val metadataQuerierFactory: MetadataQuerier.Factory<SourceConfiguration>,
    val outputConsumer: OutputConsumer,
    val handler: CatalogValidationFailureHandler,
) {
    /** Generates a [StateManager] instance based on the provided inputs. */
    fun create(
        config: SourceConfiguration,
        configuredCatalog: ConfiguredAirbyteCatalog,
        inputState: InputState,
    ): StateManager {
        val allStreams: List<Stream> =
            metadataQuerierFactory.session(config).use { mq ->
                configuredCatalog.streams.mapNotNull { toStream(mq, it) }
            }
        return if (config.global) {
            when (inputState) {
                is StreamInputState ->
                    throw ConfigErrorException("input state unexpectedly of type STREAM")
                is GlobalInputState -> forGlobal(allStreams, inputState)
                is EmptyInputState -> forGlobal(allStreams)
            }
        } else {
            when (inputState) {
                is GlobalInputState ->
                    throw ConfigErrorException("input state unexpectedly of type GLOBAL")
                is StreamInputState -> forStream(allStreams, inputState)
                is EmptyInputState -> forStream(allStreams)
            }
        }
    }

    private fun forGlobal(
        streams: List<Stream>,
        inputState: GlobalInputState? = null,
    ) =
        StateManager(
            global =
                Global(streams.filter { it.configuredSyncMode == ConfiguredSyncMode.INCREMENTAL }),
            initialGlobalState = inputState?.global,
            initialStreamStates =
                streams.associateWith { stream: Stream ->
                    when (stream.configuredSyncMode) {
                        ConfiguredSyncMode.INCREMENTAL -> inputState?.globalStreams?.get(stream.id)
                        ConfiguredSyncMode.FULL_REFRESH ->
                            inputState?.nonGlobalStreams?.get(stream.id)
                    }
                },
        )

    private fun forStream(
        streams: List<Stream>,
        inputState: StreamInputState? = null,
    ) =
        StateManager(
            initialStreamStates =
                streams.associateWith { stream: Stream -> inputState?.streams?.get(stream.id) },
        )

    private fun toStream(
        metadataQuerier: MetadataQuerier,
        configuredStream: ConfiguredAirbyteStream,
    ): Stream? {
        val stream: AirbyteStream = configuredStream.stream
        val jsonSchemaProperties: JsonNode = stream.jsonSchema["properties"]
        val streamID: StreamIdentifier = StreamIdentifier.from(configuredStream.stream)
        val name: String = streamID.name
        val namespace: String? = streamID.namespace
        val streamLabel: String = streamID.toString()
        when (metadataQuerier.streamNames(namespace).filter { it.name == name }.size) {
            0 -> {
                handler.accept(StreamNotFound(streamID))
                outputConsumer.accept(
                    AirbyteErrorTraceMessage()
                        .withStreamDescriptor(streamID.asProtocolStreamDescriptor())
                        .withFailureType(AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR)
                        .withMessage("Stream '$streamLabel' not found or not accessible in source.")
                )
                return null
            }
            1 -> Unit
            else -> {
                handler.accept(MultipleStreamsFound(streamID))
                outputConsumer.accept(
                    AirbyteErrorTraceMessage()
                        .withStreamDescriptor(streamID.asProtocolStreamDescriptor())
                        .withFailureType(AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR)
                        .withMessage("Multiple streams '$streamLabel' found in source.")
                )
                return null
            }
        }

        val expectedSchema: Map<String, AirbyteType> =
            jsonSchemaProperties.properties().associate { (id: String, schema: JsonNode) ->
                id to airbyteTypeFromJsonSchema(schema)
            }
        val actualDataColumns: Map<String, Field> =
            metadataQuerier.fields(streamID).associateBy { it.id }

        fun dataColumnOrNull(id: String): Field? {
            if (MetaField.isMetaFieldID(id)) {
                // Ignore airbyte metadata columns.
                // These aren't actually present in the table.
                return null
            }
            val actualColumn: Field? = actualDataColumns[id]
            if (actualColumn == null) {
                handler.accept(FieldNotFound(streamID, id))
                return null
            }
            val expectedAirbyteType: AirbyteType = expectedSchema[id] ?: return null
            val actualAirbyteType: AirbyteType = actualColumn.type.airbyteType
            if (expectedAirbyteType != actualAirbyteType) {
                handler.accept(
                    FieldTypeMismatch(
                        streamID,
                        id,
                        expectedAirbyteType,
                        actualAirbyteType,
                    ),
                )
                return null
            }
            return actualColumn
        }
        val streamFields: List<Field> =
            expectedSchema.keys.toList().filterNot(MetaField::isMetaFieldID).map {
                dataColumnOrNull(it) ?: return@toStream null
            }
        if (streamFields.isEmpty()) {
            handler.accept(StreamHasNoFields(streamID))
            outputConsumer.accept(
                AirbyteErrorTraceMessage()
                    .withStreamDescriptor(streamID.asProtocolStreamDescriptor())
                    .withFailureType(AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR)
                    .withMessage("Stream '$streamLabel' has no accessible fields.")
            )
            return null
        }

        fun pkOrNull(pkColumnIDComponents: List<List<String>>): List<Field>? {
            if (pkColumnIDComponents.isEmpty()) {
                return null
            }
            val pkColumnIDs: List<String> =
                pkColumnIDComponents.map { it.joinToString(separator = ".") }
            val pk: List<Field> = pkColumnIDs.mapNotNull(::dataColumnOrNull)
            if (pk.size < pkColumnIDComponents.size) {
                handler.accept(InvalidPrimaryKey(streamID, pkColumnIDs))
                return null
            }
            return pk
        }

        fun cursorOrNull(cursorColumnIDComponents: List<String>): FieldOrMetaField? {
            if (cursorColumnIDComponents.isEmpty()) {
                return null
            }
            val cursorColumnID: String = cursorColumnIDComponents.joinToString(separator = ".")
            if (cursorColumnID == CommonMetaField.CDC_LSN.id) {
                return CommonMetaField.CDC_LSN
            }
            return dataColumnOrNull(cursorColumnID)
        }
        val configuredPrimaryKey: List<Field>? =
            configuredStream.primaryKey?.asSequence()?.let { pkOrNull(it.toList()) }
        val configuredCursor: FieldOrMetaField? =
            configuredStream.cursorField?.asSequence()?.let { cursorOrNull(it.toList()) }
        val configuredSyncMode: ConfiguredSyncMode =
            when (configuredStream.syncMode) {
                SyncMode.INCREMENTAL ->
                    if (configuredCursor == null) {
                        handler.accept(InvalidIncrementalSyncMode(streamID))
                        ConfiguredSyncMode.FULL_REFRESH
                    } else {
                        ConfiguredSyncMode.INCREMENTAL
                    }
                else -> ConfiguredSyncMode.FULL_REFRESH
            }
        return Stream(
            streamID,
            streamFields,
            configuredSyncMode,
            configuredPrimaryKey,
            configuredCursor,
        )
    }

    /**
     * Recursively re-generates the original [AirbyteType] from a catalog stream field's JSON
     * schema.
     */
    private fun airbyteTypeFromJsonSchema(jsonSchema: JsonNode): AirbyteType {
        fun value(key: String): String = jsonSchema[key]?.asText() ?: ""
        return when (value("type")) {
            "array" -> ArrayAirbyteType(airbyteTypeFromJsonSchema(jsonSchema["items"]))
            "null" -> LeafAirbyteType.NULL
            "boolean" -> LeafAirbyteType.BOOLEAN
            "number" ->
                when (value("airbyte_type")) {
                    "integer",
                    "big_integer", -> LeafAirbyteType.INTEGER
                    else -> LeafAirbyteType.NUMBER
                }
            "string" ->
                when (value("format")) {
                    "date" -> LeafAirbyteType.DATE
                    "date-time" ->
                        if (value("airbyte_type") == "timestamp_with_timezone") {
                            LeafAirbyteType.TIMESTAMP_WITH_TIMEZONE
                        } else {
                            LeafAirbyteType.TIMESTAMP_WITHOUT_TIMEZONE
                        }
                    "time" ->
                        if (value("airbyte_type") == "time_with_timezone") {
                            LeafAirbyteType.TIME_WITH_TIMEZONE
                        } else {
                            LeafAirbyteType.TIME_WITHOUT_TIMEZONE
                        }
                    else ->
                        if (value("contentEncoding") == "base64") {
                            LeafAirbyteType.BINARY
                        } else {
                            LeafAirbyteType.STRING
                        }
                }
            else -> LeafAirbyteType.JSONB
        }
    }
}
