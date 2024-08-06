/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.EmptyInputState
import io.airbyte.cdk.command.GlobalInputState
import io.airbyte.cdk.command.InputState
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.StreamInputState
import io.airbyte.cdk.consumers.CatalogValidationFailureHandler
import io.airbyte.cdk.consumers.FieldNotFound
import io.airbyte.cdk.consumers.FieldTypeMismatch
import io.airbyte.cdk.consumers.InvalidIncrementalSyncMode
import io.airbyte.cdk.consumers.InvalidPrimaryKey
import io.airbyte.cdk.consumers.MultipleStreamsFound
import io.airbyte.cdk.consumers.StreamHasNoFields
import io.airbyte.cdk.consumers.StreamNotFound
import io.airbyte.cdk.data.AirbyteType
import io.airbyte.cdk.data.ArrayAirbyteType
import io.airbyte.cdk.data.LeafAirbyteType
import io.airbyte.cdk.exceptions.ConfigErrorException
import io.airbyte.cdk.source.CommonMetaField
import io.airbyte.cdk.source.Field
import io.airbyte.cdk.source.FieldOrMetaField
import io.airbyte.cdk.source.MetaField
import io.airbyte.cdk.source.MetadataQuerier
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
            global = Global(streams.filter { it.configuredSyncMode == SyncMode.INCREMENTAL }),
            initialGlobalState = inputState?.global,
            initialStreamStates =
                streams.associateWith { stream: Stream ->
                    when (stream.configuredSyncMode) {
                        SyncMode.INCREMENTAL -> inputState?.globalStreams?.get(stream.namePair)
                        SyncMode.FULL_REFRESH -> inputState?.nonGlobalStreams?.get(stream.namePair)
                    }
                },
        )

    private fun forStream(
        streams: List<Stream>,
        inputState: StreamInputState? = null,
    ) =
        StateManager(
            initialStreamStates =
                streams.associateWith { stream: Stream ->
                    inputState?.streams?.get(stream.namePair)
                },
        )

    private fun toStream(
        metadataQuerier: MetadataQuerier,
        configuredStream: ConfiguredAirbyteStream,
    ): Stream? {
        val stream: AirbyteStream = configuredStream.stream
        val jsonSchemaProperties: JsonNode = stream.jsonSchema["properties"]
        val name: String = stream.name!!
        val namespace: String? = stream.namespace
        when (metadataQuerier.streamNames(namespace).filter { it == name }.size) {
            0 -> {
                handler.accept(StreamNotFound(name, namespace))
                return null
            }
            1 -> Unit
            else -> {
                handler.accept(MultipleStreamsFound(name, namespace))
                return null
            }
        }

        val expectedSchema: Map<String, AirbyteType> =
            jsonSchemaProperties.properties().associate { (id: String, schema: JsonNode) ->
                id to airbyteTypeFromJsonSchema(schema)
            }
        val actualDataColumns: Map<String, Field> =
            metadataQuerier.fields(name, namespace).associateBy { it.id }

        fun dataColumnOrNull(id: String): Field? {
            if (MetaField.isMetaFieldID(id)) {
                // Ignore airbyte metadata columns.
                // These aren't actually present in the table.
                return null
            }
            val actualColumn: Field? = actualDataColumns[id]
            if (actualColumn == null) {
                handler.accept(FieldNotFound(name, namespace, id))
                return null
            }
            val expectedAirbyteType: AirbyteType = expectedSchema[id] ?: return null
            val actualAirbyteType: AirbyteType = actualColumn.type.airbyteType
            if (expectedAirbyteType != actualAirbyteType) {
                handler.accept(
                    FieldTypeMismatch(
                        name,
                        namespace,
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
            handler.accept(StreamHasNoFields(name, namespace))
            return null
        }

        fun pkOrNull(pkColumnIDs: List<String>): List<Field>? {
            val pk: List<Field> = pkColumnIDs.mapNotNull(::dataColumnOrNull)
            if (pk.isEmpty() || pk.size < pkColumnIDs.size) {
                handler.accept(InvalidPrimaryKey(name, namespace, pkColumnIDs))
                return null
            }
            return pk
        }

        fun cursorOrNull(cursorColumnID: String): FieldOrMetaField? {
            if (cursorColumnID == CommonMetaField.CDC_LSN.id) {
                return CommonMetaField.CDC_LSN
            }
            return dataColumnOrNull(cursorColumnID)
        }
        val primaryKeyCandidates: List<List<Field>> =
            stream.sourceDefinedPrimaryKey.mapNotNull(::pkOrNull)
        val configuredPrimaryKey: List<Field>? =
            configuredStream.primaryKey?.asSequence()?.mapNotNull(::pkOrNull)?.firstOrNull()
        val configuredCursor: FieldOrMetaField? =
            configuredStream.cursorField?.asSequence()?.mapNotNull(::cursorOrNull)?.firstOrNull()
        val configuredSyncMode: SyncMode =
            when (configuredStream.syncMode) {
                SyncMode.INCREMENTAL ->
                    if (configuredCursor == null) {
                        handler.accept(InvalidIncrementalSyncMode(name, namespace))
                        SyncMode.FULL_REFRESH
                    } else {
                        SyncMode.INCREMENTAL
                    }
                else -> SyncMode.FULL_REFRESH
            }
        return Stream(
            name,
            namespace,
            streamFields,
            primaryKeyCandidates,
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
