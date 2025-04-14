/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration

import io.airbyte.cdk.load.command.DestinationStream

data class TableNames(
    // this is pretty dumb, but in theory we could have:
    // * old-style implementation: raw+final tables both exist
    // * only the raw table exists (i.e. T+D disabled)
    // * only the final table exists (i.e. new-style direct-load tables)
    val rawTableName: TableName?,
    val finalTableName: TableName?,
) {
    init {
        check(rawTableName != null || finalTableName != null) {
            "At least one table name should be nonnull"
        }
    }

    fun conflictsWith(other: TableNames) =
        this.rawTableName.conflictsWith(other.rawTableName) ||
            this.finalTableName.conflictsWith(other.finalTableName)

    companion object {
        // TODO comment explaining this
        const val TMP_TABLE_SUFFIX = "_airbyte_tmp"
    }
}

data class TableName(val namespace: String, val name: String)

fun TableName?.conflictsWith(other: TableName?): Boolean {
    if (this == null || other == null) {
        return false
    }
    return this.namespace == other.namespace && this.name == other.name
}

/**
 * map from the column name as declared in the schema, to the column name that we'll create in the
 * final (typed) table.
 */
@JvmInline
value class ColumnNameMapping(private val columnNameMapping: Map<String, String>) :
    Map<String, String> by columnNameMapping

fun interface TableNameGenerator {
    fun getTableName(streamDescriptor: DestinationStream.Descriptor): TableName
}

fun interface ColumnNameGenerator {
    /**
     * In some database/warehouses, there's a difference between how a name is _displayed_, and how
     * the underlying engine actually treats it. For example, a column might be displayed as
     * `CamelCaseColumn`, but the engine actually treats it as lowercase `camelcasecolumn`, or
     * truncate it to `CamelCas`.
     *
     * This is relevant for handling collisions between column names. We need to know what name will
     * be displayed to the user, since that's what we'll use in queries - but we also need to know
     * the "canonical" name to check whether two columns will collide.
     *
     * (edgao: I actually can't think of an example offhand. This logic predates me, and possibly
     * doesn't need to exist.)
     */
    data class ColumnName(val displayName: String, val canonicalName: String)
    fun getColumnName(column: String): ColumnName
}
