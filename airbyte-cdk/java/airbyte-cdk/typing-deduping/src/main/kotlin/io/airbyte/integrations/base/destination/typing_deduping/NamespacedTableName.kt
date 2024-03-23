/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

// yet another namespace, name combo class
class NamespacedTableName(namespace: String, tableName: String) {
    val namespace: String
    val tableName: String

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
        this.streams = streams
        this.columnsToAdd = columnsToAdd
        this.columnsToRemove = columnsToRemove
        this.columnsToChangeType = columnsToChangeType
        this.isDestinationV2Format = isDestinationV2Format
        this.namespace = namespace
        this.tableName = tableName
    }
}
