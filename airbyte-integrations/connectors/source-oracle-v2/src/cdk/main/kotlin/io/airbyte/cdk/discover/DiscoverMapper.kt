/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.discover

import io.airbyte.cdk.read.stream.SelectQuery
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

    /** Maps a [ColumnMetadata] to a [SelectQuery.ValueType] in a many-to-one relationship. */
    fun columnValueType(c: ColumnMetadata): ValueType<*>

    /** Can the column be used as part of a primary key ? */
    fun isPossiblePrimaryKeyElement(c: ColumnMetadata): Boolean =
        columnValueType(c) is ReversibleValueType<*, *>

    /** Can the column be used as a cursor? */
    fun isPossibleCursor(c: ColumnMetadata): Boolean {
        val type: ValueType<*> = columnValueType(c)
        return (type is ReversibleValueType<*, *> && type.airbyteType != LeafAirbyteType.BOOLEAN)
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
                    val valueType: ValueType<*> = mapper.columnValueType(it)
                    Field.of(it.label, valueType.airbyteType.asJsonSchemaType())
                }
            val airbyteStream: AirbyteStream =
                CatalogHelpers.createAirbyteStream(
                    stream.table.name,
                    null, // Don't know how to map namespace yet, fill in later
                    fields
                )
            val metadataByName: Map<String, ColumnMetadata> =
                stream.columnMetadata.associateBy { it.name }
            val pkColumnNames: List<List<String>> =
                stream.primaryKeyColumnNames
                    .map { pk: List<String> -> pk.map { metadataByName[it]!! } }
                    .filter { pk: List<ColumnMetadata> ->
                        pk.all { mapper.isPossiblePrimaryKeyElement(it) }
                    }
                    .map { pk: List<ColumnMetadata> -> pk.map { it.name } }
            airbyteStream.withSourceDefinedPrimaryKey(pkColumnNames)
            val cursorColumnLabels: List<String> =
                stream.columnMetadata.filter { mapper.isPossibleCursor(it) }.map { it.label }
            airbyteStream.withDefaultCursorField(cursorColumnLabels)
            return airbyteStream
        }
    }
}
