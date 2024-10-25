/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.StreamDescriptor
import kotlin.math.max

/**
 * In general, callers should not directly instantiate this class. Use [SqlGenerator.buildStreamId]
 * instead.
 *
 * All names/namespaces are intended to be quoted, but do not explicitly contain quotes. For
 * example, finalName might be "foo bar"; the caller is required to wrap that in quotes before using
 * it in a query.
 *
 * @param finalNamespace the namespace where the final table will be created
 * @param finalName the name of the final table
 * @param rawNamespace the namespace where the raw table will be created (typically "airbyte")
 * @param rawName the name of the raw table (typically namespace_name, but may be different if there
 * are collisions). There is no rawNamespace because we assume that we're writing raw tables to the
 * airbyte namespace.
 */
data class StreamId(
    val finalNamespace: String,
    val finalName: String,
    val rawNamespace: String,
    val rawName: String,
    val originalNamespace: String,
    val originalName: String,
) {
    /**
     * Most databases/warehouses use a `schema.name` syntax to identify tables. This is a
     * convenience method to generate that syntax.
     */
    fun finalTableId(quote: String): String {
        return "$quote$finalNamespace$quote.$quote$finalName$quote"
    }

    fun finalTableId(quote: String, suffix: String): String {
        return "$quote$finalNamespace$quote.$quote$finalName$suffix$quote"
    }

    fun rawTableId(quote: String): String {
        return "$quote$rawNamespace$quote.$quote$rawName$quote"
    }

    fun finalName(quote: String): String {
        return quote + finalName + quote
    }

    fun finalNamespace(quote: String): String {
        return quote + finalNamespace + quote
    }

    fun asPair(): AirbyteStreamNameNamespacePair {
        return AirbyteStreamNameNamespacePair(originalName, originalNamespace)
    }

    fun asStreamDescriptor(): StreamDescriptor {
        return StreamDescriptor().withNamespace(originalNamespace).withName(originalName)
    }

    companion object {
        /**
         * Build the raw table name as namespace + (delimiter) + name. For example, given a stream
         * with namespace "public__ab" and name "abab_users", we will end up with raw table name
         * "public__ab_ab___ab_abab_users".
         *
         * This logic is intended to solve two problems:
         *
         * * The raw table name should be unambiguously parsable into the namespace/name.
         * * It must be impossible for two different streams to generate the same raw table name.
         *
         * The generated delimiter is guaranteed to not be present in the namespace or name, so it
         * accomplishes both of these goals.
         */
        @JvmStatic
        fun concatenateRawTableName(namespace: String, name: String): String {
            val plainConcat = namespace + name
            // Pretend we always have at least one underscore, so that we never generate
            // `_raw_stream_`
            var longestUnderscoreRun = 1
            var i = 0
            while (i < plainConcat.length) {
                // If we've found an underscore, count the number of consecutive underscores
                var underscoreRun = 0
                while (i < plainConcat.length && plainConcat[i] == '_') {
                    underscoreRun++
                    i++
                }
                longestUnderscoreRun =
                    max(longestUnderscoreRun.toDouble(), underscoreRun.toDouble()).toInt()
                i++
            }

            return namespace + "_raw" + "_".repeat(longestUnderscoreRun + 1) + "stream_" + name
        }
    }
}
