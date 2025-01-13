/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.discover

import io.airbyte.cdk.jdbc.BooleanFieldType
import io.airbyte.cdk.jdbc.CharacterStreamFieldType
import io.airbyte.cdk.jdbc.ClobFieldType
import io.airbyte.cdk.jdbc.JsonStringFieldType
import io.airbyte.cdk.jdbc.NCharacterStreamFieldType
import io.airbyte.cdk.jdbc.NClobFieldType
import io.airbyte.protocol.models.v0.SyncMode

/** [JdbcAirbyteStreamFactory] implements [createGlobal] and [createNonGlobal] for JDBC sourcesx. */
interface JdbcAirbyteStreamFactory : AirbyteStreamFactory, MetaFieldDecorator {

    override fun createGlobal(discoveredStream: DiscoveredStream) =
        AirbyteStreamFactory.createAirbyteStream(discoveredStream).apply {
            if (hasValidPrimaryKey(discoveredStream)) {
                decorateAirbyteStream(this)
                supportedSyncModes = listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                sourceDefinedPrimaryKey = discoveredStream.primaryKeyColumnIDs
                isResumable = true
            } else {
                supportedSyncModes = listOf(SyncMode.FULL_REFRESH)
                sourceDefinedCursor = false
                isResumable = false
            }
        }

    override fun createNonGlobal(discoveredStream: DiscoveredStream) =
        AirbyteStreamFactory.createAirbyteStream(discoveredStream).apply {
            if (hasCursorFields(discoveredStream)) {
                supportedSyncModes = listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
            } else {
                supportedSyncModes = listOf(SyncMode.FULL_REFRESH)
            }
            sourceDefinedCursor = false
            if (hasValidPrimaryKey(discoveredStream)) {
                sourceDefinedPrimaryKey = discoveredStream.primaryKeyColumnIDs
                isResumable = true
            }
        }

    /** Does the [discoveredStream] have a field that could serve as a cursor? */
    fun hasCursorFields(discoveredStream: DiscoveredStream): Boolean =
        !discoveredStream.columns.none(::isPossibleCursor)

    /** Does the [discoveredStream] have a valid primary key declared? */
    fun hasValidPrimaryKey(discoveredStream: DiscoveredStream): Boolean {
        if (discoveredStream.primaryKeyColumnIDs.isEmpty()) {
            return false
        }
        val allColumnsByID: Map<String, Field> = discoveredStream.columns.associateBy { it.id }
        return discoveredStream.primaryKeyColumnIDs.all { idComponents: List<String> ->
            val id: String = idComponents.joinToString(separator = ".")
            val field: Field? = allColumnsByID[id]
            field != null && isPossiblePrimaryKeyElement(field)
        }
    }

    /**
     * Can the field be used as part of a primary key?
     *
     * For this to be possible,
     * 1. the field needs to be part of a key as defined by the source,
     * 2. and its values must be deserializable from the checkpoint persisted in an Airbyte state
     * message.
     *
     * This method does not determine (1), of course, because the source keys are defined in the
     * source database itself and are retrieved via [MetadataQuerier.primaryKey]. Instead, this
     * method determines (2) based on the type information of the field, typically the [FieldType]
     * objects. For instance if the [Field.type] does not map to a [LosslessFieldType] then the
     * field can't reliably round-trip checkpoint values during a resumable initial sync.
     */
    fun isPossiblePrimaryKeyElement(field: Field): Boolean =
        when (field.type) {
            !is LosslessFieldType -> false
            CharacterStreamFieldType,
            NCharacterStreamFieldType,
            ClobFieldType,
            NClobFieldType,
            JsonStringFieldType, -> false
            else -> true
        }

    /**
     * Can the field be used as a cursor in a cursor-based incremental sync?
     *
     * This predicate is like [isPossiblePrimaryKeyElement] but tighter: in addition to being able
     * to round-trip the column values, we need to be able to query the max value from the source at
     * the start of the sync.
     */
    fun isPossibleCursor(field: Field): Boolean =
        isPossiblePrimaryKeyElement(field) && field.type !is BooleanFieldType
}
