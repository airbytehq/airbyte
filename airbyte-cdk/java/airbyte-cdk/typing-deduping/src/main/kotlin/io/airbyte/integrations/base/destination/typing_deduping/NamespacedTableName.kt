/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

// yet another namespace, name combo class
class NamespacedTableName(namespace: String, tableName: String) {
    val namespace: String
    val tableName: String

    init {
        this.namespace = namespace
        this.tableName = tableName
    }
}
