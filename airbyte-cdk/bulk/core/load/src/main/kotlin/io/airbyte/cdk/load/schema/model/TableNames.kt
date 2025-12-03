/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema.model

/** Table names used during different stages of data loading. */
data class TableNames(
    // raw only applies to T+D destinations. Pre-deprecated.
    val rawTableName: TableName? = null,
    val tempTableName: TableName? = null,
    val finalTableName: TableName? = null,
) {
    init {
        check(rawTableName != null || finalTableName != null) {
            "At least one table name should be nonnull"
        }
    }

    fun toPrettyString() =
        "Raw table: ${rawTableName?.toPrettyString()}; " +
            "Temp table: ${tempTableName?.toPrettyString()}; " +
            "Final table: ${finalTableName?.toPrettyString()}"
}
