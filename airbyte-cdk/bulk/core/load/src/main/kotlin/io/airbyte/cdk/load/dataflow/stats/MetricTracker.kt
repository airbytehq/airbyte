/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.stats

import io.airbyte.cdk.load.command.DestinationStream
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

/**
 * A thread-safe utility class designed to track and manage metrics for different destination
 * streams. Metrics are categorized by stream descriptors and identified by metric names.
 *
 * The class supports adding numeric metric values, retrieving metrics for specific streams, and
 * draining (retrieving and clearing) metrics for a stream. If metric values are missing for
 * predefined metric names, default values of 0.0 are used.
 */
@Singleton
class MetricTracker {

    private val metrics: MutableMap<DestinationStream.Descriptor, MutableMap<String, Double>> =
        ConcurrentHashMap()

    private val lock: Any = Any()

    /**
     * Adds a metric value to the specified stream descriptor and metric. If the metric does not
     * already exist for the given stream, it will be initialized with the given value. Later calls
     * will update the existing value by adding the provided value.
     *
     * @param stream the stream descriptor used to identify the metrics data.
     * @param metric the metric name and related metadata to be added or updated.
     * @param value the numeric value to add to the specified metric for the given stream.
     */
    fun add(stream: DestinationStream.Descriptor, metric: ObservabilityMetrics, value: Double) {
        synchronized(lock) {
            metrics.putIfAbsent(stream, ConcurrentHashMap())
            val streamMetrics = metrics[stream]!!
            streamMetrics[metric.metricName] =
                streamMetrics.getOrDefault(metric.metricName, 0.0) + value
        }
    }

    /**
     * Retrieves the metrics associated with the specified stream descriptor.
     *
     * @param stream the stream descriptor used to identify the metrics to retrieve.
     * @return a map containing the metrics data, where keys represent metric names
     * ```
     *         and values are their corresponding numeric values. If no metrics are
     *         found for the provided stream, an empty map is returned.
     * ```
     */
    fun get(stream: DestinationStream.Descriptor): Map<String, Double> =
        synchronized(lock) { metrics[stream]?.toMap() ?: mutableMapOf() }

    /**
     * Drains and returns the current metrics data for the specified stream descriptor. After
     * retrieval, the metrics for the provided stream are cleared.
     *
     * @param stream the stream descriptor associated with the metrics to be drained.
     * @return a map containing the drained metrics data, where keys are metric names and values are
     * their respective numeric values.
     */
    fun drain(stream: DestinationStream.Descriptor): Map<String, Double> {
        synchronized(lock) {
            // Ensure that all metrics are present even if not explicitly set.
            val copy = addDefaultValues(get(stream))
            metrics[stream]?.clear()
            return copy
        }
    }

    /**
     * Adds default values for any missing metrics in the provided map. If a metric defined in the
     * [ObservabilityMetrics] enum is absent in the given map, it will be initialized with a default
     * value of 0.0.
     *
     * @param metrics the map of metrics to be updated with default values. The keys
     * ```
     *                are metric names and the values are their respective numeric values.
     * @return
     * ```
     * a new mutable map containing the updated metrics with default values for
     * ```
     *         any missing entries.
     * ```
     */
    private fun addDefaultValues(metrics: Map<String, Double>): Map<String, Double> {
        val copy = metrics.toMutableMap()
        ObservabilityMetrics.entries.forEach { copy.putIfAbsent(it.metricName, 0.0) }
        return copy
    }
}

/**
 * Enum representing the available observability metrics. Each metric is associated with a specific
 * metric name used for tracking system behavior and performance.
 *
 * @property metricName The name of the metric used in tracking.
 */
enum class ObservabilityMetrics(val metricName: String) {
    NULLED_VALUE_COUNT("NulledValueCount"),
    TRUNCATED_VALUE_COUNT("TruncatedValueCount")
}
