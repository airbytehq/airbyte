/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.config

import kotlin.time.Duration
import kotlin.time.Duration.Companion.minutes

/**
 * Configures the publishing of aggregates downstream for uploading to the destination.
 *
 * By extension this controls memory usage in the destination for storing customer data. Note: the
 * defaults presume we are storing the aggregates in memory, but if we are storing them on disk, we
 * can handle a larger quantity of larger aggregates.
 *
 * Per aggregate configuration:
 * @property maxEstBytesPerAgg configures the size of each aggregate based on our estimated byte
 * counts. Once an aggregate reaches this size, we publish it.
 * @property maxRecordsPerAgg configures the max number of records in an aggregate. Once an
 * aggregate has accumulated this many records, we publish it.
 * @property stalenessDeadlinePerAgg is how long we will wait to flush an aggregate after it stops
 * receiving data.
 *
 * Across all aggregate configuration:
 * @property maxEstBytesAllAggregates if the total accumulated estimated bytes for all open
 * aggregates is greater than this value, we will publish the largest aggregate.
 * @property maxBufferedAggregates configures the number of published aggregates we buffer before
 * backpressuring preventing further aggregate publishes.
 *
 * Memory considerations: The max memory consumption is maxEstBytesAllAggregates, but one should
 * make sure this is a multiple of maxEstBytesPerAgg.
 */
data class AggregatePublishingConfig(
    // per aggregate triggers
    val maxRecordsPerAgg: Long = 100_000L,
    val maxEstBytesPerAgg: Long = 50_000_000L,
    val stalenessDeadlinePerAgg: Duration = 5.minutes,
    // total aggregate triggers
    val maxEstBytesAllAggregates: Long = 250_000_000L,
    // backpressure after we fill the buffer
    val maxBufferedAggregates: Int = 5,
) {
    init {
        require(maxRecordsPerAgg > 0) { "maxRecordsPerAgg must be greater than 0" }
        require(maxEstBytesPerAgg > 0) { "maxEstBytesPerAgg must be greater than 0" }
        require(stalenessDeadlinePerAgg > Duration.ZERO) {
            "stalenessDeadlinePerAgg must be greater than 0"
        }
        require(maxEstBytesAllAggregates >= maxEstBytesPerAgg) {
            "maxEstBytesAllAggregates must be at least maxEstBytesPerAgg"
        }
        require(maxBufferedAggregates > 0) { "maxBufferedAggregates must be greater than 0" }
    }
}
