/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import io.github.oshai.kotlinlogging.KotlinLogging

/**
 * [FetchSizeEstimator] is used to estimate the value of the JDBC fetchSize parameter to fill up a
 * portion of the JVM heap defined by [MEM_CAPACITY_RATIO].
 */
class DefaultJdbcFetchSizeEstimator(
    val maxMemoryBytes: Long,
    val maxConcurrency: Int,
    val minFetchSize: Int,
    val defaultFetchSize: Int,
    val maxFetchSize: Int,
    val memoryCapacityRatio: Double,
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
        val targetMemoryUsePerQuery: Long = targetMemoryUse / maxConcurrency
        log.info {
            "Targeting a maximum of $targetMemoryUsePerQuery bytes " +
                "for each of up to $maxConcurrency queries."
        }
        val maxRowsFetchedPerQuery: Long = targetMemoryUsePerQuery / maxRowBytes
        return maxRowsFetchedPerQuery
            .coerceAtLeast(minFetchSize.toLong())
            .coerceAtMost(maxFetchSize.toLong())
            .toInt()
    }
}
