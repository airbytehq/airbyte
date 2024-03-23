/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import java.util.*

class StreamConfig(id: StreamId?,
                   syncMode: SyncMode,
                   destinationSyncMode: DestinationSyncMode,
                   primaryKey: List<ColumnId?>,
                   cursor: Optional<ColumnId?>,
                   columns: LinkedHashMap<ColumnId?, AirbyteType>) {
    val id: StreamId?
    val syncMode: SyncMode
    val destinationSyncMode: DestinationSyncMode
    val primaryKey: List<ColumnId?>
    val cursor: Optional<ColumnId?>
    val columns: LinkedHashMap<ColumnId?, AirbyteType>

    init {
        this.transactions = transactions
        this.items = items
        this.properties = properties
        this.name = name
        this.originalName = originalName
        this.canonicalName = canonicalName
        this.finalNamespace = finalNamespace
        this.finalName = finalName
        this.rawNamespace = rawNamespace
        this.rawName = rawName
        this.originalNamespace = originalNamespace
        this.originalName = originalName
        this.id = id
        this.syncMode = syncMode
        this.destinationSyncMode = destinationSyncMode
        this.primaryKey = primaryKey
        this.cursor = cursor
        this.columns = columns
    }
}
