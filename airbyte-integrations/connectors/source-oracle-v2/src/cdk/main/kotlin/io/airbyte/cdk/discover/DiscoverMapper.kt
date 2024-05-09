/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.discover

import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.CatalogHelpers

/**
 * Each source connector contains an implementation of this interface in a stateless class which
 * encapsulates the peculiarities of the source database as far as the DISCOVER operation is
 * concerned.
 */
interface DiscoverMapper {

    /** Crafts a SQL query for a table which, if possible, doesn't return any rows. */
    fun selectFromTableLimit0(table: TableName, columns: List<String>): String

    /** Maps a [ColumnMetadata] to a [FieldType] in a many-to-one relationship. */
    fun toFieldType(c: ColumnMetadata): FieldType

    /**
     * Can the column be used as part of a primary key in a resumable initial sync?
     *
     * For this to be possible,
     * 1. the column needs to be part of a key as defined by the source relation,
     * 2. and its values must be settable as parameters in a [java.sql.PreparedStatement].
     *
     * This method does not determine (1), of course, because the source relation keys are defined
     * in the source database itself and are retrieved via [MetadataQuerier.primaryKeys]. Instead,
     * this method determines (2) based on the type information of the column, typically the
     * [FieldType] objects. For instance if the [ColumnMetadata] does not map to a
     * [ReversibleFieldType] then the column can't reliably round-trip checkpoint values during a
     * resumable initial sync.
     */
    fun isPossiblePrimaryKeyElement(c: ColumnMetadata): Boolean =
        toFieldType(c) is ReversibleFieldType

    /**
     * Can the column be used as a cursor in a cursor-based incremental sync?
     *
     * This predicate is like [isPossiblePrimaryKeyElement] but tighter: in addition to being
     * able to round-trip the column values, we need to be able to aggregate them using the MAX()
     * SQL function.
     */
    fun isPossibleCursor(c: ColumnMetadata): Boolean {
        val type: FieldType = toFieldType(c)
        return (type is ReversibleFieldType && type.airbyteType != LeafAirbyteType.BOOLEAN)
    }

    /** Maps a [DiscoveredStream] to an [AirbyteStream] when the state is to be of type GLOBAL. */
    fun globalAirbyteStream(stream: DiscoveredStream): AirbyteStream

    /** Maps a [DiscoveredStream] to an [AirbyteStream] when the state is to be of type STREAM. */
    fun nonGlobalAirbyteStream(stream: DiscoveredStream): AirbyteStream

    companion object {

        /**
         * Utility function to pre-populate an [AirbyteStream] instance using a [DiscoveredStream]
         * instance regardless of the type of the state.
         */
        fun basicAirbyteStream(mapper: DiscoverMapper, stream: DiscoveredStream): AirbyteStream {
            val fields: List<Field> =
                stream.columnMetadata.map {
                    val fieldType: FieldType = mapper.toFieldType(it)
                    Field.of(it.label, fieldType.airbyteType.asJsonSchemaType())
                }
            val airbyteStream: AirbyteStream =
                CatalogHelpers.createAirbyteStream(
                    stream.table.name,
                    stream.table.schema ?: stream.table.catalog, // This is a wild guess.
                    fields
                )
            val metadataByName: Map<String, ColumnMetadata> =
                stream.columnMetadata.associateBy { it.name }
            val pkColumnNames: List<List<String>> =
                stream.primaryKeyColumnNames
                    .map { pk: List<String> -> pk.map { metadataByName[it]!! } }
                    .filter { pk: List<ColumnMetadata> ->
                        // Only keep PKs whose values can be round-tripped.
                        pk.all { mapper.isPossiblePrimaryKeyElement(it) }
                    }
                    .map { pk: List<ColumnMetadata> -> pk.map { it.name } }
            airbyteStream.withSourceDefinedPrimaryKey(pkColumnNames)
            val cursorColumnLabels: List<String> =
                // Only keep cursors whose values can be round-tripped and can be aggregated by MAX.
                stream.columnMetadata.filter { mapper.isPossibleCursor(it) }.map { it.label }
            airbyteStream.withDefaultCursorField(cursorColumnLabels)
            return airbyteStream
        }
    }
}
