package io.airbyte.cdk.load.orchestration

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
    companion object {
        // TODO comment explaining this
        const val TMP_TABLE_SUFFIX = "_airbyte_tmp"
    }
}

data class TableName(val namespace: String, val name: String)

/**
 * map from the column name as declared in the schema, to the column name that we'll create in the
 * final (typed) table.
 */
@JvmInline
value class ColumnNameMapping(private val columnNameMapping: Map<String, String>) :
    Map<String, String> by columnNameMapping
