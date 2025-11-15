/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state.stats

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.state.PartitionHistogram
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.state.StateKey
import io.mockk.junit5.MockKExtension
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class CommittedStatsStoreTest {

    private lateinit var store: CommittedStatsStore

    @BeforeEach
    fun setup() {
        store = CommittedStatsStore()
    }

    @Test
    fun `acceptStats should store stats for a stream`() {
        // Given
        val counts = PartitionHistogram()
        counts.increment(Fixtures.partition1, 10.0)
        counts.increment(Fixtures.partition2, 20.0)

        val bytes = PartitionHistogram()
        bytes.increment(Fixtures.partition1, 100.0)
        bytes.increment(Fixtures.partition2, 200.0)

        // When
        store.acceptStats(Fixtures.descriptor, counts, bytes)

        // Then - verify through commit since liveStats is private
        val stateKey = StateKey(1L, listOf(Fixtures.partition1, Fixtures.partition2))
        val result = store.commitStats(Fixtures.descriptor, stateKey)
        assertEquals(30L, result.committedStats.count)
        assertEquals(300L, result.committedStats.bytes)
    }

    @Test
    fun `acceptStats should merge multiple stats for the same stream`() {
        // Given
        val counts1 = PartitionHistogram().apply { increment(Fixtures.partition1, 10.0) }
        val bytes1 = PartitionHistogram().apply { increment(Fixtures.partition1, 100.0) }
        val counts2 = PartitionHistogram().apply { increment(Fixtures.partition1, 5.0) }
        val bytes2 = PartitionHistogram().apply { increment(Fixtures.partition1, 50.0) }

        // When
        store.acceptStats(Fixtures.descriptor, counts1, bytes1)
        store.acceptStats(Fixtures.descriptor, counts2, bytes2)

        // Then
        val stateKey = StateKey(1L, listOf(Fixtures.partition1))
        val result = store.commitStats(Fixtures.descriptor, stateKey)
        assertEquals(15L, result.committedStats.count)
        assertEquals(150L, result.committedStats.bytes)
    }

    @Test
    fun `commitStats should remove live stats and accumulate cumulative stats`() {
        // Given
        val counts = PartitionHistogram()
        counts.increment(Fixtures.partition1, 10.0)
        counts.increment(Fixtures.partition2, 20.0)

        val bytes = PartitionHistogram()
        bytes.increment(Fixtures.partition1, 100.0)
        bytes.increment(Fixtures.partition2, 200.0)
        store.acceptStats(Fixtures.descriptor, counts, bytes)

        // When - commit only Fixtures.partition1
        val stateKey1 = StateKey(1L, listOf(Fixtures.partition1))
        val result1 = store.commitStats(Fixtures.descriptor, stateKey1)

        // Then
        assertEquals(10L, result1.committedStats.count)
        assertEquals(100L, result1.committedStats.bytes)
        assertEquals(10L, result1.cumulativeStats.count)
        assertEquals(100L, result1.cumulativeStats.bytes)

        // When - commit Fixtures.partition2
        val stateKey2 = StateKey(2L, listOf(Fixtures.partition2))
        val result2 = store.commitStats(Fixtures.descriptor, stateKey2)

        // Then
        assertEquals(20L, result2.committedStats.count)
        assertEquals(200L, result2.committedStats.bytes)
        assertEquals(30L, result2.cumulativeStats.count) // Accumulated
        assertEquals(300L, result2.cumulativeStats.bytes) // Accumulated
    }

    @Test
    fun `commitStats should handle multiple partitions in single state key`() {
        // Given
        val counts = PartitionHistogram()
        counts.increment(Fixtures.partition1, 10.0)
        counts.increment(Fixtures.partition2, 20.0)
        counts.increment(Fixtures.partition3, 30.0)

        val bytes = PartitionHistogram()
        bytes.increment(Fixtures.partition1, 100.0)
        bytes.increment(Fixtures.partition2, 200.0)
        bytes.increment(Fixtures.partition3, 300.0)

        store.acceptStats(Fixtures.descriptor, counts, bytes)

        // When - commit multiple partitions at once
        val stateKey = StateKey(1L, listOf(Fixtures.partition1, Fixtures.partition2))
        val result = store.commitStats(Fixtures.descriptor, stateKey)

        // Then
        assertEquals(30L, result.committedStats.count) // 10 + 20
        assertEquals(300L, result.committedStats.bytes) // 100 + 200
        assertEquals(30L, result.cumulativeStats.count)
        assertEquals(300L, result.cumulativeStats.bytes)

        // And partition3 should still be live
        val stateKey3 = StateKey(2L, listOf(Fixtures.partition3))
        val result3 = store.commitStats(Fixtures.descriptor, stateKey3)
        assertEquals(30L, result3.committedStats.count)
        assertEquals(300L, result3.committedStats.bytes)
    }

    @Test
    fun `commitStats should handle empty state key`() {
        // Given
        val counts = PartitionHistogram().apply { increment(Fixtures.partition1, 10.0) }
        val bytes = PartitionHistogram().apply { increment(Fixtures.partition1, 100.0) }
        store.acceptStats(Fixtures.descriptor, counts, bytes)

        // When - commit with empty partition list
        val stateKey = StateKey(1L, emptyList())
        val result = store.commitStats(Fixtures.descriptor, stateKey)

        // Then
        assertEquals(0L, result.committedStats.count)
        assertEquals(0L, result.committedStats.bytes)
        assertEquals(0L, result.cumulativeStats.count)
        assertEquals(0L, result.cumulativeStats.bytes)
    }

    @Test
    fun `commitStats should handle non-existent partition`() {
        // Given
        val counts = PartitionHistogram().apply { increment(Fixtures.partition1, 10.0) }
        val bytes = PartitionHistogram().apply { increment(Fixtures.partition1, 100.0) }
        store.acceptStats(Fixtures.descriptor, counts, bytes)

        // When - try to commit non-existent partition
        val stateKey = StateKey(1L, listOf(PartitionKey("non-existent")))
        val result = store.commitStats(Fixtures.descriptor, stateKey)

        // Then
        assertEquals(0L, result.committedStats.count)
        assertEquals(0L, result.committedStats.bytes)
        assertEquals(0L, result.cumulativeStats.count)
        assertEquals(0L, result.cumulativeStats.bytes)
    }

    @Test
    fun `multiple streams should be tracked independently`() {
        // Given
        val descriptor1 = DestinationStream.Descriptor("namespace1", "stream1")
        val descriptor2 = DestinationStream.Descriptor("namespace2", "stream2")
        val partition = Fixtures.partition1

        val counts1 = PartitionHistogram().apply { increment(partition, 10.0) }
        val bytes1 = PartitionHistogram().apply { increment(partition, 100.0) }
        val counts2 = PartitionHistogram().apply { increment(partition, 20.0) }
        val bytes2 = PartitionHistogram().apply { increment(partition, 200.0) }

        store.acceptStats(descriptor1, counts1, bytes1)
        store.acceptStats(descriptor2, counts2, bytes2)

        // When
        val stateKey = StateKey(1L, listOf(partition))
        val result1 = store.commitStats(descriptor1, stateKey)
        val result2 = store.commitStats(descriptor2, stateKey)

        // Then
        assertEquals(10L, result1.committedStats.count)
        assertEquals(100L, result1.committedStats.bytes)
        assertEquals(20L, result2.committedStats.count)
        assertEquals(200L, result2.committedStats.bytes)
    }

    @Test
    fun `removeLiveStats with single partition should remove and return stats`() {
        // Given
        val partition = Fixtures.partition1
        val counts = PartitionHistogram().apply { increment(partition, 10.0) }
        val bytes = PartitionHistogram().apply { increment(partition, 100.0) }
        store.acceptStats(Fixtures.descriptor, counts, bytes)

        // When
        val stats = store.removeLiveStats(Fixtures.descriptor, partition)

        // Then
        assertNotNull(stats)
        assertEquals(10L, stats?.count)
        assertEquals(100L, stats?.bytes)

        // And partition should be removed
        val secondRemoval = store.removeLiveStats(Fixtures.descriptor, partition)
        assertEquals(0L, secondRemoval?.count)
        assertEquals(0L, secondRemoval?.bytes)
    }

    @Test
    fun `removeLiveStats with StateKey should aggregate multiple partitions`() {
        // Given
        val counts = PartitionHistogram()
        counts.increment(Fixtures.partition1, 10.0)
        counts.increment(Fixtures.partition2, 20.0)

        val bytes = PartitionHistogram()
        bytes.increment(Fixtures.partition1, 100.0)
        bytes.increment(Fixtures.partition2, 200.0)

        store.acceptStats(Fixtures.descriptor, counts, bytes)

        // When
        val stateKey = StateKey(1L, listOf(Fixtures.partition1, Fixtures.partition2))
        val stats = store.removeLiveStats(Fixtures.descriptor, stateKey)

        // Then
        assertEquals(30L, stats.count)
        assertEquals(300L, stats.bytes)
    }

    @Test
    fun `CommitStatsResult merge should combine stats correctly`() {
        // Given
        val result1 =
            CommitStatsResult(
                committedStats = EmissionStats(10L, 100L),
                cumulativeStats = EmissionStats(50L, 500L)
            )
        val result2 =
            CommitStatsResult(
                committedStats = EmissionStats(20L, 200L),
                cumulativeStats = EmissionStats(60L, 600L)
            )

        // When
        val merged = result1.merge(result2)

        // Then
        assertEquals(30L, merged.committedStats.count)
        assertEquals(300L, merged.committedStats.bytes)
        assertEquals(110L, merged.cumulativeStats.count)
        assertEquals(1100L, merged.cumulativeStats.bytes)
    }

    @Test
    fun `PartitionStats merge should combine histograms`() {
        // Given
        val stats1 =
            PartitionStats(
                counts = PartitionHistogram().apply { increment(Fixtures.partition1, 10.0) },
                bytes = PartitionHistogram().apply { increment(Fixtures.partition1, 100.0) }
            )
        val stats2 =
            PartitionStats(
                counts =
                    PartitionHistogram().apply {
                        increment(Fixtures.partition1, 5.0)
                        increment(Fixtures.partition2, 20.0)
                    },
                bytes =
                    PartitionHistogram().apply {
                        increment(Fixtures.partition1, 50.0)
                        increment(Fixtures.partition2, 200.0)
                    }
            )

        // When
        val merged = stats1.merge(stats2)

        // Then
        assertEquals(15L, merged.counts.get(Fixtures.partition1)?.toLong())
        assertEquals(20L, merged.counts.get(Fixtures.partition2)?.toLong())
        assertEquals(150L, merged.bytes.get(Fixtures.partition1)?.toLong())
        assertEquals(200L, merged.bytes.get(Fixtures.partition2)?.toLong())
    }

    @Test
    fun `concurrent operations should be thread-safe`() {
        // Given
        val threads = mutableListOf<Thread>()

        // When - simulate concurrent operations
        for (i in 1..10) {
            threads.add(
                Thread {
                    val partition = PartitionKey("p$i")
                    val counts = PartitionHistogram().apply { increment(partition, i.toDouble()) }
                    val bytes = PartitionHistogram().apply { increment(partition, i * 10.0) }
                    store.acceptStats(Fixtures.descriptor, counts, bytes)
                }
            )
        }

        threads.forEach { it.start() }
        threads.forEach { it.join() }

        // Commit all partitions
        val partitions = (1..10).map { PartitionKey("p$it") }
        val stateKey = StateKey(1L, partitions)
        val result = store.commitStats(Fixtures.descriptor, stateKey)

        // Then
        val expectedCount = (1..10).sum().toLong() // 55
        val expectedBytes = (1..10).sumOf { it * 10L } // 550
        assertEquals(expectedCount, result.committedStats.count)
        assertEquals(expectedBytes, result.committedStats.bytes)
    }

    object Fixtures {
        val descriptor = DestinationStream.Descriptor("namespace", "stream")

        val partition1 = PartitionKey("p1")
        val partition2 = PartitionKey("p21")
        val partition3 = PartitionKey("p31")
    }
}
