/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state.stats

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.state.AdditionalStatsHistogram
import io.airbyte.cdk.load.dataflow.state.Histogram
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

/**
 * A singleton class responsible for managing additional state statistics, specifically histograms
 * of metrics associated with partitions and destination streams. This class provides methods to add
 * metrics values, retrieve combined statistics, and maintain metrics completeness with default
 * values.
 */
@Singleton
class StateAdditionalStatsStore {

    private val store =
        ConcurrentHashMap<
            PartitionKey, ConcurrentHashMap<DestinationStream.Descriptor, AdditionalStatsHistogram>
        >()

    /**
     * Adds a value to the histogram associated with the given partition and stream descriptor for
     * the specified metric.
     *
     * @param partitionKey The key representing the partition for which the histogram is maintained.
     * @param streamDescriptor The descriptor identifying the specific destination stream.
     * @param metric The metric whose value is to be incremented in the histogram.
     * @param value The value to increment for the specified metric.
     */
    fun add(
        partitionKey: PartitionKey,
        streamDescriptor: DestinationStream.Descriptor,
        metric: ObservabilityMetrics,
        value: Double
    ) {
        store.putIfAbsent(partitionKey, ConcurrentHashMap())
        store[partitionKey]?.let { partitionStats ->
            partitionStats.putIfAbsent(streamDescriptor, Histogram())
            partitionStats[streamDescriptor]?.increment(metric.metricName, value)
        }
    }

    /**
     * Drains the accumulated statistics for the specified destination stream across the provided
     * partition keys, returning a combined histogram of all relevant metrics. For any metric values
     * not present, default values are added. This is to ensure that the metrics are always
     * published as part of the state message with a zero value if no value has been recorded since
     * the last state message publish event.
     *
     * @param partitionKeys The list of partition keys to process, each representing a distinct
     * partition.
     * @param stream The descriptor of the destination stream whose statistics are to be drained.
     * @return A `Histogram` containing the combined metrics for the specified destination stream.
     */
    fun drain(
        partitionKeys: List<PartitionKey>,
    ): Map<DestinationStream.Descriptor, AdditionalStatsHistogram> {
        val accumulator =
            mutableMapOf<DestinationStream.Descriptor, AdditionalStatsHistogram>().withDefault {
                populateWithDefaultValues(AdditionalStatsHistogram())
            }

        return partitionKeys
            .mapNotNull { store.remove(it) }
            .fold(accumulator) { acc, perStreamStats ->
                perStreamStats.forEach { (stream, histogram) ->
                    acc.merge(stream, histogram, AdditionalStatsHistogram::merge)
                }
                addDefaultValues(acc)
            }
    }

    /**
     * Adds default values for metrics that are not present in the given histogram. This ensures
     * that all metrics defined in `ObservabilityMetrics` are represented in the histogram with a
     * default value of 0.0 if they are missing.
     *
     * @param histogram The histogram to which default values should be added,
     * ```
     *                  representing metric counts by their names.
     * @return
     * ```
     * The updated histogram with default values for missing metrics.
     */
    private fun addDefaultValues(
        stats: MutableMap<DestinationStream.Descriptor, AdditionalStatsHistogram>
    ): MutableMap<DestinationStream.Descriptor, AdditionalStatsHistogram> {
        stats.forEach { (_, histogram) -> populateWithDefaultValues(histogram) }
        return stats
    }

    private fun populateWithDefaultValues(
        histogram: AdditionalStatsHistogram
    ): AdditionalStatsHistogram {
        ObservabilityMetrics.entries.forEach {
            if (histogram.get(it.metricName) == null) {
                histogram.increment(it.metricName, 0.0)
            }
        }
        return histogram
    }

    /**
     * Enum representing the available observability metrics. Each metric is associated with a
     * specific metric name used for tracking system behavior and performance.
     *
     * @property metricName The name of the metric used in tracking.
     */
    enum class ObservabilityMetrics(val metricName: String) {
        NULLED_VALUE_COUNT("nulledValueCount"),
        TRUNCATED_VALUE_COUNT("truncatedValueCount")
    }
}
