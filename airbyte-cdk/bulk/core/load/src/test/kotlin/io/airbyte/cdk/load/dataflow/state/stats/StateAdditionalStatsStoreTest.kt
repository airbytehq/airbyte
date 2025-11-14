/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state.stats

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class StateAdditionalStatsStoreTest {

    @Test
    fun testAddingMetricValue() {
        val partitionKey1 = PartitionKey("partition-1")
        val partitionKey2 = PartitionKey("partition-2")
        val stream = DestinationStream.Descriptor(namespace = "namespace", name = "name")
        val metric = StateAdditionalStatsStore.ObservabilityMetrics.NULLED_VALUE_COUNT
        val store = StateAdditionalStatsStore()

        store.add(
            partitionKey = partitionKey1,
            streamDescriptor = stream,
            metric = metric,
            value = 1.0
        )
        store.add(
            partitionKey = partitionKey2,
            streamDescriptor = stream,
            metric = metric,
            value = 1.0
        )
        store.add(
            partitionKey = partitionKey1,
            streamDescriptor = stream,
            metric = StateAdditionalStatsStore.ObservabilityMetrics.TRUNCATED_VALUE_COUNT,
            value = 5.0
        )

        val stats = store.drain(listOf(partitionKey1, partitionKey2))
        assertEquals(2, stats.getValue(stream).toMap().size)
        assertEquals(2.0, stats.getValue(stream).get(metric.metricName))
        assertEquals(
            5.0,
            stats
                .getValue(stream)
                .get(
                    StateAdditionalStatsStore.ObservabilityMetrics.TRUNCATED_VALUE_COUNT.metricName
                )
        )
    }

    @Test
    fun testDrainAllPartialDefaultValues() {
        val partitionKey = PartitionKey("partition-1")
        val stream = DestinationStream.Descriptor(namespace = "namespace", name = "name")
        val metric = StateAdditionalStatsStore.ObservabilityMetrics.NULLED_VALUE_COUNT
        val store = StateAdditionalStatsStore()

        store.add(
            partitionKey = partitionKey,
            streamDescriptor = stream,
            metric = metric,
            value = 1.0
        )

        val stats = store.drain(listOf(partitionKey))
        assertEquals(2, stats.getValue(stream).toMap().size)
        assertEquals(1.0, stats.getValue(stream).get(metric.metricName))
        assertEquals(
            0.0,
            stats
                .getValue(stream)
                .get(
                    StateAdditionalStatsStore.ObservabilityMetrics.TRUNCATED_VALUE_COUNT.metricName
                )
        )
    }

    @Test
    fun testDrainAllDefaultValues() {
        val partitionKeys = listOf(PartitionKey("partition-1"), PartitionKey("partition-2"))
        val stream = DestinationStream.Descriptor(namespace = "namespace", name = "name")
        val store = StateAdditionalStatsStore()

        val stats = store.drain(partitionKeys)

        StateAdditionalStatsStore.ObservabilityMetrics.entries.forEach { metric ->
            assertEquals(0.0, stats.getValue(stream).get(metric.metricName))
        }
    }
}
