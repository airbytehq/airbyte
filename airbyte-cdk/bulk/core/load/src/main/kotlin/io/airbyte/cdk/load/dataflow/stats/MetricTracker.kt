/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.stats

import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

@Singleton
class MetricTracker {

    private val metrics: MutableMap<String, Double> = ConcurrentHashMap()

    fun add(name: String, value: Double) {
        metrics[name] = metrics.getOrDefault(name, 0.0) + value
    }

    fun get(): Map<String, Double> = metrics.toMap()
}
