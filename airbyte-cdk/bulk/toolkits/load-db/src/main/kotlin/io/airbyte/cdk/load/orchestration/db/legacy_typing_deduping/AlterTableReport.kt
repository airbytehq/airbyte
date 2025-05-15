/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping

data class AlterTableReport(
    val columnsToAdd: Set<String>,
    val columnsToRemove: Set<String>,
    val columnsToChangeType: Set<String>,
) {
    /**
     * A no-op for an AlterTableReport is when the existing table matches the expected schema
     *
     * @return whether the schema matches
     */
    val isNoOp =
        columnsToAdd.isEmpty() && columnsToRemove.isEmpty() && columnsToChangeType.isEmpty()
}
