/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.table

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.TableSuffixes.TMP_TABLE_SUFFIX
import jakarta.inject.Singleton
import org.apache.commons.codec.digest.DigestUtils

// Commented out so CI won't be big mad
// @Deprecated("Deprecated in favor of TableSchemaMapper")
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
 *
 * Not deprecated, but the interface it implements is deprecated.
 */
@Singleton
open class DefaultTempTableNameGenerator(
    private val internalNamespace: String? = null,
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
            namespace = internalNamespace ?: originalName.namespace,
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

sealed interface TableNameGenerator {
    fun getTableName(streamDescriptor: DestinationStream.Descriptor): TableName
}

fun interface RawTableNameGenerator : TableNameGenerator

// Commented out so CI won't be big mad
// @Deprecated("Deprecated in favor of TableSchemaMapper")
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
