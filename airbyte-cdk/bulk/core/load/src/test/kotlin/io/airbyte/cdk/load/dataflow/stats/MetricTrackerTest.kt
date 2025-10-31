/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.stats

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class MetricTrackerTest {

    @Test
    fun testAddingMetricValue() {
        val metricName = "testMetric"
        val metricTracker = MetricTracker()

        assertEquals(0, metricTracker.get().size)

        metricTracker.add(metricName, 1.0)
        assertEquals(1, metricTracker.get().size)
        assertEquals(1.0, metricTracker.get()[metricName])

        metricTracker.add(metricName, 2.0)
        assertEquals(1, metricTracker.get().size)
        assertEquals(3.0, metricTracker.get()[metricName])

        metricTracker.add("$metricName}2", 5.0)
        assertEquals(2, metricTracker.get().size)
        assertEquals(3.0, metricTracker.get()[metricName])
        assertEquals(5.0, metricTracker.get()["$metricName}2"])
    }
}
