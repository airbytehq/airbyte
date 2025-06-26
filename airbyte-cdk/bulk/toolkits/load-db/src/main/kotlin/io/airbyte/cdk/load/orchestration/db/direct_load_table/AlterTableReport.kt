/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.direct_load_table

data class AlterTableReport<Type>(
    val columnsToAdd: List<ColumnAdd<Type>>,
    val columnsToRemove: List<String>,
    val columnsToChangeType: List<ColumnChange<Type>>,
    val columnsToRetain: List<String>,
) {
    /**
     * A no-op for an AlterTableReport is when the existing table matches the expected schema
     *
     * @return whether the schema matches
     */
    val isNoOp =
        columnsToAdd.isEmpty() && columnsToRemove.isEmpty() && columnsToChangeType.isEmpty()
}

data class ColumnAdd<Type>(
    val name: String,
    val type: Type,
)

data class ColumnChange<Type>(
    val name: String,
    val originalType: Type,
    val newType: Type,
)
