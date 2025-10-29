/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

// Some potentially-shareable utility classes for TableSchemaEvolutionClient.

data class PrimaryKeyList(val primaryKey: List<String>) {
    fun diff(other: PrimaryKeyList): PrimaryKeyDiff {
        TODO()
    }
}

data class PrimaryKeyDiff(
    val columnsToAddToPrimaryKey: List<String>,
    val columnsToRemoveFromPrimaryKey: List<String>
) {
    fun isNoop() = columnsToAddToPrimaryKey.isEmpty() && columnsToRemoveFromPrimaryKey.isEmpty()
}
