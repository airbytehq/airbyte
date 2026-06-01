/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import io.github.oshai.kotlinlogging.KotlinLogging

/**
 * [FetchSizeEstimator] is used to estimate the value of the JDBC fetchSize parameter to fill up a
 * portion of the JVM heap defined by [memoryCapacityRatio], up to a hard
 * [maxMemoryBytesPerQuery] cap.
 */
class DefaultJdbcFetchSizeEstimator(
    val maxMemoryBytes: Long,
    val maxConcurrency: Int,
    val minFetchSize: Int,
    val defaultFetchSize: Int,
    val maxFetchSize: Int,
    val memoryCapacityRatio: Double,
    val maxMemoryBytesPerQuery: Long,
) : JdbcSharedState.JdbcFetchSizeEstimator {
    private val log = KotlinLogging.logger {}

    override fun apply(rowByteSizeSample: Sample<Long>): Int {
        val maxRowBytes: Long = rowByteSizeSample.sampledValues.maxOrNull() ?: 0L
        log.info {
            "Maximum row size in ${rowByteSizeSample.kind.name} table is $maxRowBytes bytes."
        }
        val targetMemoryUse: Long = (maxMemoryBytes * memoryCapacityRatio).toLong()
        if (listOf(maxRowBytes, targetMemoryUse, maxConcurrency.toLong()).any { it <= 0L }) {
            return defaultFetchSize
        }
        // Divide the total budget across the configured concurrency, then clamp to the
        // per-query cap. The cap guards against two failure modes:
        //   1) `maxConcurrency` underestimates the number of partition readers actually
        //      running in parallel (so the per-query share over-estimates real headroom),
        //   2) the row-size sample misses the wide-row tail of the table, so the true
        //      bytes-per-row at runtime is much larger than `maxRowBytes` here.
        val perQueryFromRatio: Long = targetMemoryUse / maxConcurrency
        val targetMemoryUsePerQuery: Long =
            perQueryFromRatio.coerceAtMost(maxMemoryBytesPerQuery.coerceAtLeast(1L))
        log.info {
            "Targeting a maximum of $targetMemoryUsePerQuery bytes for each of up to " +
                "$maxConcurrency configured concurrent queries " +
                "(ratio-derived=$perQueryFromRatio, per-query cap=$maxMemoryBytesPerQuery)."
        }
        val maxRowsFetchedPerQuery: Long = targetMemoryUsePerQuery / maxRowBytes
        return maxRowsFetchedPerQuery
            .coerceAtLeast(minFetchSize.toLong())
            .coerceAtMost(maxFetchSize.toLong())
            .toInt()
    }
}
