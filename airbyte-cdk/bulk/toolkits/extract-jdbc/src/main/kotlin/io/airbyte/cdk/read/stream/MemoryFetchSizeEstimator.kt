/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read.stream

import io.github.oshai.kotlinlogging.KotlinLogging
import kotlin.math.max
import kotlin.math.min

/**
 * [MemoryFetchSizeEstimator] is used to estimate the value of the JDBC fetchSize parameter to fill
 * up a portion of the JVM heap defined by [MEM_CAPACITY_RATIO].
 */
class MemoryFetchSizeEstimator(
    val maxMemoryBytes: Long,
    val maxConcurrency: Int,
) : StreamPartitionsCreatorUtils.FetchSizeEstimator {
    private val log = KotlinLogging.logger {}

    override fun apply(rowByteSizeSample: Sample<Long>): Int {
        val maxRowBytes: Long = rowByteSizeSample.sampledValues.maxOrNull() ?: 0L
        log.info {
            "maximum row size in ${rowByteSizeSample.kind.name} table is $maxRowBytes bytes"
        }
        val targetMemoryUse: Long = (maxMemoryBytes * MEM_CAPACITY_RATIO).toLong()
        if (listOf(maxRowBytes, targetMemoryUse, maxConcurrency.toLong()).any { it <= 0L }) {
            return DEFAULT_FETCH_SIZE
        }
        val targetMemoryUsePerQuery: Long = targetMemoryUse / maxConcurrency
        log.info {
            "targeting a maximum of $targetMemoryUsePerQuery bytes " +
                "for each of up to $maxConcurrency queries"
        }
        val maxRowsFetchedPerQuery: Long = targetMemoryUsePerQuery / maxRowBytes
        return max(
            FETCH_SIZE_LOWER_BOUND,
            min(
                    maxRowsFetchedPerQuery,
                    FETCH_SIZE_UPPER_BOUND.toLong(),
                )
                .toInt(),
        )
    }

    companion object {
        const val FETCH_SIZE_LOWER_BOUND: Int = 10
        const val DEFAULT_FETCH_SIZE: Int = 1_000
        const val FETCH_SIZE_UPPER_BOUND: Int = 10_000_000

        // We're targeting use of 60% of the available memory in order to allow
        // for some headroom for other garbage collection.
        const val MEM_CAPACITY_RATIO: Double = 0.6
    }
}
