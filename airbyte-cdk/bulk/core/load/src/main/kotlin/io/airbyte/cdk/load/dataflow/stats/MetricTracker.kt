/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.stats

import io.airbyte.cdk.load.command.DestinationStream
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

@Singleton
class MetricTracker {

    private val metrics: MutableMap<DestinationStream.Descriptor, MutableMap<String, Double>> =
        ConcurrentHashMap()

    private val lock: Any = Any()

    fun add(stream: DestinationStream.Descriptor, metric: ObservabilityMetrics, value: Double) {
        synchronized(lock) {
            if (!metrics.containsKey(stream)) {
                metrics[stream] = ConcurrentHashMap()
                initMetrics(stream)
            }
            val streamMetrics = metrics[stream]!!
            streamMetrics[metric.metricName] =
                streamMetrics.getOrDefault(metric.metricName, 0.0) + value
        }
    }

    fun get(stream: DestinationStream.Descriptor): Map<String, Double> =
        synchronized(lock) { metrics[stream]?.toMap() ?: emptyMap() }

    fun drain(stream: DestinationStream.Descriptor): Map<String, Double> {
        synchronized(lock) {
            val copy = get(stream)
            metrics[stream]?.clear()
            initMetrics(stream)
            return copy
        }
    }

    private fun initMetrics(stream: DestinationStream.Descriptor) {
        ObservabilityMetrics.entries.forEach {
            // Initialize all metrics to 0.0 for the given stream
            add(stream, it, 0.0)
        }
    }
}

enum class ObservabilityMetrics(val metricName: String) {
    NULLED_VALUE_COUNT("NulledValueCount"),
    TRUNCATED_VALUE_COUNT("TruncatedValueCount")
}
