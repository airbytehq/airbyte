/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.EmptyInputState
import io.airbyte.cdk.command.GlobalInputState
import io.airbyte.cdk.command.InputState
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.StreamInputState
import io.airbyte.cdk.command.StreamStateValue
import io.airbyte.cdk.consumers.CatalogValidationFailureHandler
import io.airbyte.cdk.consumers.ColumnNotFound
import io.airbyte.cdk.consumers.ColumnTypeMismatch
import io.airbyte.cdk.consumers.InvalidCursor
import io.airbyte.cdk.consumers.InvalidPrimaryKey
import io.airbyte.cdk.consumers.MultipleTablesFound
import io.airbyte.cdk.consumers.ResetStream
import io.airbyte.cdk.consumers.TableHasNoDataColumns
import io.airbyte.cdk.consumers.TableNotFound
import io.airbyte.cdk.discover.AirbyteType
import io.airbyte.cdk.discover.ColumnMetadata
import io.airbyte.cdk.discover.LeafAirbyteType
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.discover.ValueType
import io.airbyte.commons.exceptions.ConfigErrorException
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
    val metadataQuerierFactory: MetadataQuerier.Factory,
    val handler: CatalogValidationFailureHandler
) {

    /** Generates a [StateManager] instance based on the provided inputs. */
    fun create(
        config: SourceConfiguration,
        configuredCatalog: ConfiguredAirbyteCatalog,
        inputState: InputState,
    ): StateManager {
        val allStreamKeys: List<StreamKey> =
            metadataQuerierFactory.session(config).use { mq ->
                val tableNames: List<TableName> = mq.tableNames()
                configuredCatalog.streams.mapNotNull { toStreamKey(mq, it, tableNames) }
            }
        return if (config.global) {
            when (inputState) {
                is StreamInputState ->
                    throw ConfigErrorException("input state unexpectedly of type STREAM")
                is GlobalInputState -> forGlobal(config, allStreamKeys, inputState)
                is EmptyInputState -> forGlobal(config, allStreamKeys)
            }
        } else {
            when (inputState) {
                is GlobalInputState ->
                    throw ConfigErrorException("input state unexpectedly of type GLOBAL")
                is StreamInputState -> forStream(config, allStreamKeys, inputState)
                is EmptyInputState -> forStream(config, allStreamKeys)
            }
        }
    }

    private fun forGlobal(
        config: SourceConfiguration,
        streamKeys: List<StreamKey>,
        inputState: GlobalInputState? = null
    ) =
        StateManager(
            initialGlobal =
                run {
                    val globalStreamKeys: List<StreamKey> =
                        streamKeys.filter { it.configuredSyncMode == SyncMode.INCREMENTAL }
                    if (inputState == null) {
                        CdcNotStarted(GlobalKey(globalStreamKeys))
                    } else {
                        CdcStarting(GlobalKey(globalStreamKeys), inputState.global)
                    }
                },
            initialStreams =
                streamKeys.map { streamKey: StreamKey ->
                    when (streamKey.configuredSyncMode) {
                        SyncMode.INCREMENTAL ->
                            buildStreamReadState(
                                config,
                                ReadKind.CDC,
                                streamKey,
                                inputState?.globalStreams?.get(streamKey.namePair)
                            )
                        SyncMode.FULL_REFRESH ->
                            buildStreamReadState(
                                config,
                                ReadKind.FULL_REFRESH,
                                streamKey,
                                inputState?.nonGlobalStreams?.get(streamKey.namePair)
                            )
                    }
                },
        )

    private fun forStream(
        config: SourceConfiguration,
        streamKeys: List<StreamKey>,
        inputState: StreamInputState? = null
    ) =
        StateManager(
            initialGlobal = null,
            initialStreams =
                streamKeys.map { streamKey: StreamKey ->
                    val readKind: ReadKind =
                        when (streamKey.configuredSyncMode) {
                            SyncMode.INCREMENTAL -> ReadKind.CURSOR
                            SyncMode.FULL_REFRESH -> ReadKind.FULL_REFRESH
                        }
                    val stateValue: StreamStateValue? = inputState?.streams?.get(streamKey.namePair)
                    buildStreamReadState(config, readKind, streamKey, stateValue)
                }
        )

    private fun toStreamKey(
        metadataQuerier: MetadataQuerier,
        configuredStream: ConfiguredAirbyteStream,
        tableNames: List<TableName>,
    ): StreamKey? {
        val stream: AirbyteStream = configuredStream.stream
        val jsonSchemaProperties: JsonNode = stream.jsonSchema["properties"]
        val name: String = stream.name!!
        val namespace: String? = stream.namespace
        val matchingTables: List<TableName> =
            tableNames
                .filter { it.name == name }
                .filter { it.catalog == namespace || it.schema == namespace || namespace == null }
        val table: TableName =
            when (matchingTables.size) {
                0 -> {
                    handler.accept(TableNotFound(name, namespace))
                    return null
                }
                1 -> matchingTables.first()
                else -> {
                    handler.accept(MultipleTablesFound(name, namespace, matchingTables))
                    return null
                }
            }
        val expectedColumnLabels: Set<String> =
            jsonSchemaProperties.fieldNames().asSequence().toSet()
        val columnMetadata: List<ColumnMetadata> = metadataQuerier.columnMetadata(table)
        val allDataColumns: Map<String, DataColumn> =
            columnMetadata
                .mapNotNull {
                    jsonSchemaProperties[it.name]?.let { jsonSchema: JsonNode ->
                        it.label to DataColumn(it, FieldSchema(jsonSchema).asColumnType())
                    }
                }
                .toMap()
        fun dataColumnOrNull(columnLabel: String): DataColumn? {
            if (columnLabel.startsWith("_ab_")) {
                // Ignore airbyte metadata columns.
                // These aren't actually present in the table.
                return null
            }
            val column: DataColumn? = allDataColumns[columnLabel]
            if (column == null) {
                handler.accept(ColumnNotFound(name, namespace, columnLabel))
                return null
            }
            val discoveredValueType: ValueType<*> =
                metadataQuerierFactory.discoverMapper.columnValueType(column.metadata)
            val discoveredAirbyteType: AirbyteType = discoveredValueType.airbyteType
            if (column.airbyteType != discoveredAirbyteType) {
                handler.accept(
                    ColumnTypeMismatch(
                        name,
                        namespace,
                        columnLabel,
                        column.airbyteType,
                        discoveredAirbyteType
                    )
                )
                return null
            }
            return column
        }

        for (columnLabel in expectedColumnLabels.toList().sorted()) {
            dataColumnOrNull(columnLabel)
        }
        val streamDataColumns: List<DataColumn> =
            allDataColumns.filterKeys { expectedColumnLabels.contains(it) }.values.toList()
        if (streamDataColumns.isEmpty()) {
            handler.accept(TableHasNoDataColumns(name, namespace))
            return null
        }
        fun pkOrNull(pkColumnLabels: List<String>): List<DataColumn>? =
            pkColumnLabels
                .mapNotNull {
                    allDataColumns[it].apply {
                        if (this == null) handler.accept(ColumnNotFound(name, namespace, it))
                    }
                }
                .takeUnless { it.isEmpty() || it.size < pkColumnLabels.size }
        fun cursorOrNull(cursorColumnLabel: String): Column? {
            if (cursorColumnLabel == "_ab_cdc_lsn") {
                return AirbyteColumn("_ab_cdc_lsn", LeafAirbyteType.STRING)
            }
            return dataColumnOrNull(cursorColumnLabel)
        }
        val primaryKeyCandidates: List<List<DataColumn>> =
            stream.sourceDefinedPrimaryKey.mapNotNull(::pkOrNull)
        val cursorCandidates: List<Column> = stream.defaultCursorField.mapNotNull(::cursorOrNull)
        val configuredSyncMode: SyncMode = configuredStream.syncMode ?: SyncMode.FULL_REFRESH
        val configuredPrimaryKey: List<DataColumn>? =
            configuredStream.primaryKey?.asSequence()?.mapNotNull(::pkOrNull)?.firstOrNull()
        val configuredCursor: Column? =
            configuredStream.cursorField?.asSequence()?.mapNotNull(::cursorOrNull)?.firstOrNull()
        return StreamKey(
            configuredStream,
            table,
            streamDataColumns,
            primaryKeyCandidates,
            cursorCandidates,
            configuredSyncMode,
            configuredPrimaryKey,
            configuredCursor,
        )
    }

    private fun buildStreamReadState(
        config: SourceConfiguration,
        readKind: ReadKind,
        key: StreamKey,
        stateValue: StreamStateValue?
    ): StreamState {
        val pk: Map<DataColumn, JsonNode>? = run {
            if (stateValue == null) {
                return@run null
            }
            if (stateValue.primaryKey.isEmpty()) {
                return@run mapOf()
            }
            val pkKeys: Set<String> = stateValue.primaryKey.keys
            val keys: List<DataColumn>? =
                key.primaryKeyCandidates.find { pk: List<DataColumn> ->
                    pk.map { it.id }.toSet() == stateValue.primaryKey.keys
                }
            if (keys == null) {
                handler.accept(InvalidPrimaryKey(key.name, key.namespace, pkKeys.toList()))
                return@run null
            }
            keys.associateWith { stateValue.primaryKey[it.id]!! }
        }
        val cursor: Pair<Column, JsonNode>? = run {
            if (stateValue == null) {
                return@run null
            }
            if (readKind != ReadKind.CURSOR) {
                return@run null
            }
            val cursorKeys: Set<String> = stateValue.cursors.keys
            if (cursorKeys.size > 1) {
                handler.accept(InvalidCursor(key.name, key.namespace, cursorKeys.toString()))
                return@run null
            }
            val cursorLabel: String = cursorKeys.firstOrNull() ?: return@run null
            val cursorColumn: Column? = key.cursorCandidates.find { it.id == cursorKeys.first() }
            if (cursorColumn == null) {
                handler.accept(InvalidCursor(key.name, key.namespace, cursorLabel))
                return@run null
            }
            cursorColumn to stateValue.cursors[cursorLabel]!!
        }
        return when (readKind) {
            ReadKind.CDC ->
                if (pk == null) {
                    if (stateValue != null) {
                        handler.accept(ResetStream(key.name, key.namespace))
                    }
                    CdcInitialSyncNotStarted(key)
                } else if (pk.isNotEmpty()) {
                    CdcResumableInitialSyncOngoing(
                        key,
                        config.initialLimit,
                        pk.keys.toList(),
                        pk.values.toList()
                    )
                } else {
                    CdcInitialSyncCompleted(key)
                }
            ReadKind.CURSOR ->
                if (cursor == null) {
                    if (stateValue != null) {
                        handler.accept(ResetStream(key.name, key.namespace))
                    }
                    CursorBasedNotStarted(key)
                } else if (pk == null && stateValue != null) {
                    handler.accept(ResetStream(key.name, key.namespace))
                    CursorBasedNotStarted(key)
                } else if (!pk.isNullOrEmpty()) {
                    CursorBasedResumableInitialSyncOngoing(
                        key,
                        config.initialLimit,
                        pk.keys.toList(),
                        pk.values.toList(),
                        cursor.first as DataColumn,
                        cursor.second
                    )
                } else {
                    CursorBasedIncrementalStarting(key, cursor.first as DataColumn, cursor.second)
                }
            ReadKind.FULL_REFRESH ->
                if (pk.isNullOrEmpty()) {
                    if (stateValue != null) {
                        handler.accept(ResetStream(key.name, key.namespace))
                    }
                    FullRefreshNotStarted(key)
                } else {
                    FullRefreshResumableOngoing(
                        key,
                        config.initialLimit,
                        pk.keys.toList(),
                        pk.values.toList()
                    )
                }
        }
    }

    private enum class ReadKind {
        CURSOR,
        CDC,
        FULL_REFRESH
    }
}
