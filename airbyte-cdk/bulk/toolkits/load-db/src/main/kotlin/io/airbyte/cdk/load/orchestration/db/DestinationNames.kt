/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.TableNames.Companion.TMP_TABLE_SUFFIX
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingUtil
import org.apache.commons.codec.digest.DigestUtils

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

    fun toPrettyString() =
        "Raw table: ${rawTableName?.toPrettyString()}; Final table: ${finalTableName?.toPrettyString()}"

    companion object {
        const val NO_SUFFIX = ""
        // TODO comment explaining this
        const val TMP_TABLE_SUFFIX = "_airbyte_tmp"
        const val SOFT_RESET_SUFFIX = "_ab_soft_reset"
    }
}

data class TableName(val namespace: String, val name: String) {
    fun toPrettyString(quote: String = "", suffix: String = "") =
        "$quote$namespace$quote.$quote$name$suffix$quote"

    fun asOldStyleTempTable() = copy(name = name + TMP_TABLE_SUFFIX)
}

fun interface TempTableNameGenerator {
    fun generate(originalName: TableName): TableName
}

/**
 * better handling for temp table names - e.g. postgres has a 64-char table name limit, so we want
 * to avoid running into that. This method generates a table name with (by default) at most 64
 * characters (`4 * affixLength + 2 * affixSeparator.length + hashLength`).
 *
 * T+D destinations simply appended [TMP_TABLE_SUFFIX] to the table name, and should use
 * [TableName.asOldStyleTempTable] instead
 */
class DefaultTempTableNameGenerator(
    private val internalNamespace: String,
    private val affixLength: Int = 8,
    private val affixSeparator: String = "",
    private val hashLength: Int = 32,
) : TempTableNameGenerator {
    override fun generate(originalName: TableName): TableName {
        val shortNamespace =
            originalName.namespace.takeFirstAndLastNChars(affixLength, separator = affixSeparator)
        val shortName =
            originalName.name.takeFirstAndLastNChars(affixLength, separator = affixSeparator)
        val hash =
            DigestUtils.sha256Hex(
                    TypingDedupingUtil.concatenateRawTableName(
                        originalName.namespace,
                        originalName.name + TMP_TABLE_SUFFIX,
                    ),
                )
                .take(hashLength)
        return TableName(
            name = "$shortNamespace$shortName$hash",
            namespace = internalNamespace,
        )
    }

    /**
     * Examples:
     * * `"123456".takeFirstAndLastNChars(1, "_") = "1_6"`
     * * `"123456".takeFirstAndLastNChars(2, "_") = "12_56"`
     * * `"123456".takeFirstAndLastNChars(3, "_") = "123456"`
     * * `"123456".takeFirstAndLastNChars(4, "_") = "123456"`
     */
    private fun String.takeFirstAndLastNChars(n: Int, separator: String): String {
        if (length <= 2 * n) {
            // if the entire string fits within the prefix+suffix substrings,
            // then just return the original string.
            return this
        }
        val prefix = substring(0, n)
        val suffix = substring(length - n, length)
        return "$prefix$separator$suffix"
    }
}

/**
 * map from the column name as declared in the schema, to the column name that we'll create in the
 * final (typed) table.
 */
@JvmInline
value class ColumnNameMapping(private val columnNameMapping: Map<String, String>) :
    Map<String, String> by columnNameMapping

sealed interface TableNameGenerator {
    fun getTableName(streamDescriptor: DestinationStream.Descriptor): TableName
}

fun interface RawTableNameGenerator : TableNameGenerator

fun interface FinalTableNameGenerator : TableNameGenerator

fun interface ColumnNameGenerator {
    /**
     * In some database/warehouses, there's a difference between how a name is _displayed_, and how
     * the underlying engine actually treats it. For example, a column might be displayed as
     * `CamelCaseColumn`, but the engine actually treats it as lowercase `camelcasecolumn`, or
     * truncate it to `CamelCas`. Bigquery is an example of this: `create table foo (foo int, FOO
     * int)` is invalid, because `foo` is duplicated.
     *
     * This is relevant for handling collisions between column names. We need to know what name will
     * be displayed to the user, since that's what we'll use in queries - but we also need to know
     * the "canonical" name to check whether two columns will collide.
     */
    data class ColumnName(val displayName: String, val canonicalName: String)
    fun getColumnName(column: String): ColumnName
}

const val CDC_DELETED_AT_COLUMN = "_ab_cdc_deleted_at"
