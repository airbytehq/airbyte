/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.probably_core_stuff

data class TableNames(
    // this is pretty dumb, but in theory we could have:
    // * old-style implementation: raw+final tables both exist
    // * only the raw table exists (i.e. T+D disabled)
    // * only the final table exists (i.e. new-style direct-load tables)
    val oldStyleRawTableName: TableName?,
    val finalTableName: TableName?,
) {
    companion object {
        // TODO comment explaining this
        const val TMP_TABLE_SUFFIX = "_airbyte_tmp"
    }
}

data class TableName(val namespace: String, val name: String)
