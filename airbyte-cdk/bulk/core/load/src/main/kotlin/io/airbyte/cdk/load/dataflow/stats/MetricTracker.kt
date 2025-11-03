/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.stats

import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

@Singleton
class MetricTracker {

    private val metrics: MutableMap<String, Double> = ConcurrentHashMap()

    private val lock: Any = Any()

    init {
        initMetrics()
    }

    fun add(metric: ObservabilityMetrics, value: Double) {
        synchronized(lock) {
            metrics[metric.metricName] = metrics.getOrDefault(metric.metricName, 0.0) + value
        }
    }

    fun get(): Map<String, Double> = synchronized(lock) { metrics.toMap() }

    fun drain(): Map<String, Double> {
        synchronized(lock) {
            val copy = get()
            metrics.clear()
            initMetrics()
            println("Drained metrics: $copy")
            return copy
        }
    }

    private fun initMetrics() {
        ObservabilityMetrics.entries.forEach {
            // Initialize all metrics to 0.0
            add(it, 0.0)
        }
    }
}

enum class ObservabilityMetrics(val metricName: String) {
    NULLED_VALUE_COUNT("NulledValueCount"),
    TRUNCATED_VALUE_COUNT("TruncatedValueCount")
}
