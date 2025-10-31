/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.stats

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class MetricTrackerTest {

    @Test
    fun testAddingMetricValue() {
        val metric = MetricRegistry.NULLED_VALUE_COUNT
        val metricTracker = MetricTracker()

        assertEquals(MetricRegistry.entries.size, metricTracker.get().size)
        metricTracker.get().forEach { assertEquals(0.0, it.value) }

        metricTracker.add(metric, 1.0)
        assertEquals(1.0, metricTracker.get()[metric.metricName])

        metricTracker.add(metric, 2.0)
        assertEquals(3.0, metricTracker.get()[metric.metricName])

        metricTracker.add(MetricRegistry.TRUNCATED_VALUE_COUNT, 5.0)
        assertEquals(3.0, metricTracker.get()[metric.metricName])
        assertEquals(5.0, metricTracker.get()[MetricRegistry.TRUNCATED_VALUE_COUNT.metricName])
    }
}
