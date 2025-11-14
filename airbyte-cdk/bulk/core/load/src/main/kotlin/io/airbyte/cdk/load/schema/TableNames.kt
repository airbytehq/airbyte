/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema

data class TableNames(
    val rawTableName: TableName?,
    val tempTableName: TableName?,
    val finalTableName: TableName?,
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
