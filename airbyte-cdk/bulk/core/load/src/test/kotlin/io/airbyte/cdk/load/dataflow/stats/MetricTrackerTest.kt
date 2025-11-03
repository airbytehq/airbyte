/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.stats

import io.airbyte.cdk.load.command.DestinationStream
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class MetricTrackerTest {

    @Test
    fun testAddingMetricValue() {
        val stream = DestinationStream.Descriptor(namespace = "namespace", name = "name")
        val metric = ObservabilityMetrics.NULLED_VALUE_COUNT
        val metricTracker = MetricTracker()

        metricTracker.add(stream, metric, 1.0)
        assertEquals(1.0, metricTracker.get(stream)[metric.metricName])

        metricTracker.add(stream, metric, 2.0)
        assertEquals(3.0, metricTracker.get(stream)[metric.metricName])

        metricTracker.add(stream, ObservabilityMetrics.TRUNCATED_VALUE_COUNT, 5.0)
        assertEquals(3.0, metricTracker.get(stream)[metric.metricName])
        assertEquals(
            5.0,
            metricTracker.get(stream)[ObservabilityMetrics.TRUNCATED_VALUE_COUNT.metricName]
        )
    }

    @Test
    fun testDrainMetricValues() {
        val stream = DestinationStream.Descriptor(namespace = "namespace", name = "name")
        val metric = ObservabilityMetrics.NULLED_VALUE_COUNT
        val metricTracker = MetricTracker()

        metricTracker.add(stream, metric, 1.0)
        metricTracker.add(stream, metric, 2.0)
        metricTracker.add(stream, ObservabilityMetrics.TRUNCATED_VALUE_COUNT, 5.0)

        val metrics = metricTracker.drain(stream)
        assertEquals(2, metrics.size)
        assertEquals(3.0, metrics[metric.metricName])
        assertEquals(5.0, metrics[ObservabilityMetrics.TRUNCATED_VALUE_COUNT.metricName])

        // Validate that the underlying map has been cleared and re-initialized
        assertEquals(2, metricTracker.get(stream).size)
        assertEquals(0.0, metricTracker.get(stream)[metric.metricName])
        assertEquals(
            0.0,
            metricTracker.get(stream)[ObservabilityMetrics.TRUNCATED_VALUE_COUNT.metricName]
        )
    }
}
