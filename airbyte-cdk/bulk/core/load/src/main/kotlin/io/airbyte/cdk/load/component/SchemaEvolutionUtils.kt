/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

// Some potentially-shareable utility classes for TableSchemaEvolutionClient.

data class PrimaryKeySet(val primaryKey: Set<String>) {
    fun diff(expected: PrimaryKeySet): PrimaryKeyDiff {
        return PrimaryKeyDiff(
            columnsToAdd = expected.primaryKey.filter { !this.primaryKey.contains(it) }.toSet(),
            columnsToRemove = this.primaryKey.filter { !expected.primaryKey.contains(it) }.toSet(),
        )
    }
}

data class PrimaryKeyDiff(val columnsToAdd: Set<String>, val columnsToRemove: Set<String>) {
    fun isNoop() = columnsToAdd.isEmpty() && columnsToRemove.isEmpty()
}
