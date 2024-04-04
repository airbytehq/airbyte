/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.source.relationaldb

import io.airbyte.commons.util.AutoCloseableIterator
import io.airbyte.protocol.models.CommonField
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import java.time.Instant
import java.util.function.Consumer
import java.util.function.Function
import java.util.function.Predicate
import java.util.stream.Collectors
import java.util.stream.Stream

class InitialSnapshotUtil<T> {

    // Focus on stream instead of connection.
    fun getSelectedDbFields(
        airbyteStream: ConfiguredAirbyteStream,
        table: TableInfo<CommonField<T>>,
        emittedAt: Instant
    ): List<String?> {
        val iteratorList: MutableList<AutoCloseableIterator<AirbyteMessage>> = ArrayList()
        val stream = airbyteStream.stream
        val streamName = stream.name
        val namespace = stream.namespace
        val primaryKeys =
            stream.sourceDefinedPrimaryKey
                .stream()
                .flatMap { pk: List<String?> ->
                    Stream.of(
                        pk[0],
                    )
                }
                .toList()
        val fullyQualifiedTableName =
            DbSourceDiscoverUtil.getFullyQualifiedTableName(namespace, streamName)

        // Grab the selected fields to sync
        val selectedDatabaseFields: MutableList<String?> =
            table.fields
                .stream()
                .map<String>(
                    Function<CommonField<T>, String> { obj: CommonField<T> -> obj.getName() }
                )
                .filter(
                    Predicate<String> { o: String? ->
                        CatalogHelpers.getTopLevelFieldNames(
                                airbyteStream,
                            )
                            .contains(o)
                    },
                )
                .collect(Collectors.toList())

        // This is to handle the case if the user de-selects the PK column
        // Necessary to query the data via pk but won't be added to the final record
        primaryKeys.forEach(
            Consumer<String?> { pk: String? ->
                if (!selectedDatabaseFields.contains(pk)) {
                    selectedDatabaseFields.add(0, pk)
                }
            },
        )

        return selectedDatabaseFields.toList()
    }
}
