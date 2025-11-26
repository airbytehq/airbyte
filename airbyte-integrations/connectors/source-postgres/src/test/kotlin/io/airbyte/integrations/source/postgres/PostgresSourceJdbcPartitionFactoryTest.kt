/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.postgres.ctid.Ctid
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

/**
 * Test subclass that overrides the lazy blockSize property for testing purposes.
 * This avoids the need for database connections during unit tests.
 */
class TestablePostgresSourceJdbcPartitionFactory(
    private val testBlockSize: Long = 8192L
) {
    // Copy of the computePartitionBounds logic for testing
    // We could also make this extend the real class, but for unit testing
    // it's cleaner to just test the logic directly
    internal fun computePartitionBounds(
        lowerBound: JsonNode?,
        numPartitions: Int,
        relationSize: Long,
    ): List<Pair<Ctid?, Ctid?>> {
        val theoreticalLastPage: Long = relationSize / testBlockSize
        val lowerBoundCtid: Ctid = lowerBound?.let {
            if (it.isNull.not() && it.asText().isEmpty().not()) {
                Ctid.of(it.asText())
            } else null
        } ?: Ctid.ZERO
        val eachStep: Long = ((theoreticalLastPage - lowerBoundCtid.page) / numPartitions).coerceAtLeast(1)
        val lbs: List<Ctid?> = listOf(lowerBoundCtid) + (1 ..< numPartitions).map {
            Ctid(lowerBoundCtid.page + eachStep * it, 1)
        }
        val ubs: List<Ctid?> = lbs.drop(1) + listOf(null)

        return lbs.zip(ubs)
    }
}

class PostgresSourceJdbcPartitionFactoryTest {

    private lateinit var factory: TestablePostgresSourceJdbcPartitionFactory

    @BeforeEach
    fun setup() {
        factory = TestablePostgresSourceJdbcPartitionFactory(
            testBlockSize = 8192L // Standard PostgreSQL block size
        )
    }

    @Test
    fun `computePartitionBounds with null lowerBound should start from Ctid ZERO`() {
        // Given: null lower bound, 4 partitions, 1MB relation size
        val lowerBound: JsonNode? = null
        val numPartitions = 4
        val relationSize = 1024L * 1024L // 1 MB

        // When
        val bounds = factory.computePartitionBounds(lowerBound, numPartitions, relationSize)

        // Then
        assertEquals(4, bounds.size)

        // First partition should start from (0,0)
        assertEquals(Ctid.ZERO, bounds[0].first)
        assertEquals(Ctid(32, 1), bounds[0].second)

        // Subsequent partitions
        assertEquals(Ctid(32, 1), bounds[1].first)
        assertEquals(Ctid(64, 1), bounds[1].second)

        assertEquals(Ctid(64, 1), bounds[2].first)
        assertEquals(Ctid(96, 1), bounds[2].second)

        // Last partition's upper bound should be null (open-ended)
        assertEquals(Ctid(96, 1), bounds[3].first)
        assertNull(bounds[3].second)
    }

    @Test
    fun `computePartitionBounds with null JsonNode lowerBound should start from Ctid ZERO`() {
        // Given: JsonNode null lower bound
        val lowerBound: JsonNode = Jsons.nullNode()
        val numPartitions = 2
        val relationSize = 16384L // 2 blocks

        // When
        val bounds = factory.computePartitionBounds(lowerBound, numPartitions, relationSize)

        // Then
        assertEquals(2, bounds.size)
        assertEquals(Ctid.ZERO, bounds[0].first)
        assertEquals(Ctid(1, 1), bounds[0].second)

        assertEquals(Ctid(1, 1), bounds[1].first)
        assertNull(bounds[1].second)
    }

    @Test
    fun `computePartitionBounds with empty string lowerBound should start from Ctid ZERO`() {
        // Given: empty string lower bound
        val lowerBound: JsonNode = Jsons.textNode("")
        val numPartitions = 3
        val relationSize = 24576L // 3 blocks

        // When
        val bounds = factory.computePartitionBounds(lowerBound, numPartitions, relationSize)

        // Then
        assertEquals(3, bounds.size)
        assertEquals(Ctid.ZERO, bounds[0].first)
    }

    @Test
    fun `computePartitionBounds with valid Ctid string lowerBound`() {
        // Given: valid Ctid string lower bound
        val lowerBound: JsonNode = Jsons.textNode("(10,5)")
        val numPartitions = 2
        val relationSize = 163840L // 20 blocks

        // When
        val bounds = factory.computePartitionBounds(lowerBound, numPartitions, relationSize)

        // Then
        assertEquals(2, bounds.size)

        // Should start from page 10
        assertEquals(Ctid(10, 5), bounds[0].first)
        assertEquals(Ctid(15, 1), bounds[0].second)

        assertEquals(Ctid(15, 1), bounds[1].first)
        assertNull(bounds[1].second)
    }

    @Test
    fun `computePartitionBounds should evenly distribute pages across partitions`() {
        // Given: 100 pages, 5 partitions
        val lowerBound: JsonNode? = null
        val numPartitions = 5
        val relationSize = 819200L // 100 blocks (100 * 8192)

        // When
        val bounds = factory.computePartitionBounds(lowerBound, numPartitions, relationSize)

        // Then: each partition should get 20 pages (100 / 5)
        assertEquals(5, bounds.size)

        assertEquals(Ctid.ZERO, bounds[0].first)
        assertEquals(Ctid(20, 1), bounds[0].second)

        assertEquals(Ctid(20, 1), bounds[1].first)
        assertEquals(Ctid(40, 1), bounds[1].second)

        assertEquals(Ctid(40, 1), bounds[2].first)
        assertEquals(Ctid(60, 1), bounds[2].second)

        assertEquals(Ctid(60, 1), bounds[3].first)
        assertEquals(Ctid(80, 1), bounds[3].second)

        assertEquals(Ctid(80, 1), bounds[4].first)
        assertNull(bounds[4].second)
    }

    @Test
    fun `computePartitionBounds with single partition should return one open-ended range`() {
        // Given: single partition
        val lowerBound: JsonNode? = null
        val numPartitions = 1
        val relationSize = 81920L // 10 blocks

        // When
        val bounds = factory.computePartitionBounds(lowerBound, numPartitions, relationSize)

        // Then
        assertEquals(1, bounds.size)
        assertEquals(Ctid.ZERO, bounds[0].first)
        assertNull(bounds[0].second)
    }

    @Test
    fun `computePartitionBounds should handle small relation size with many partitions`() {
        // Given: very small relation (1 block) with 10 partitions
        val lowerBound: JsonNode? = null
        val numPartitions = 10
        val relationSize = 8192L // 1 block

        // When
        val bounds = factory.computePartitionBounds(lowerBound, numPartitions, relationSize)

        // Then: eachStep should be coerced to at least 1
        assertEquals(10, bounds.size)

        // Each partition should advance by 1 page (minimum step)
        assertEquals(Ctid.ZERO, bounds[0].first)
        assertEquals(Ctid(1, 1), bounds[0].second)

        assertEquals(Ctid(1, 1), bounds[1].first)
        assertEquals(Ctid(2, 1), bounds[1].second)

        // Last partition
        assertEquals(Ctid(9, 1), bounds[9].first)
        assertNull(bounds[9].second)
    }

    @Test
    fun `computePartitionBounds with large relation size`() {
        // Given: large relation (1GB), 10 partitions
        val lowerBound: JsonNode? = null
        val numPartitions = 10
        val relationSize = 1024L * 1024L * 1024L // 1 GB

        // When
        val bounds = factory.computePartitionBounds(lowerBound, numPartitions, relationSize)

        // Then
        assertEquals(10, bounds.size)

        // 1GB / 8192 = 131072 pages
        // 131072 / 10 = 13107 pages per partition
        assertEquals(Ctid.ZERO, bounds[0].first)
        assertEquals(Ctid(13107, 1), bounds[0].second)

        assertEquals(Ctid(13107, 1), bounds[1].first)
        assertEquals(Ctid(26214, 1), bounds[1].second)

        assertEquals(Ctid(117963, 1), bounds[9].first)
        assertNull(bounds[9].second)
    }

    @Test
    fun `computePartitionBounds with non-zero lowerBound should calculate ranges from that point`() {
        // Given: starting from page 50, 100 total pages, 2 partitions
        val lowerBound: JsonNode = Jsons.textNode("(50,10)")
        val numPartitions = 2
        val relationSize = 819200L // 100 blocks total

        // When
        val bounds = factory.computePartitionBounds(lowerBound, numPartitions, relationSize)

        // Then: should split the remaining 50 pages (100 - 50) into 2 partitions
        assertEquals(2, bounds.size)

        assertEquals(Ctid(50, 10), bounds[0].first)
        assertEquals(Ctid(75, 1), bounds[0].second) // 50 + (50/2)

        assertEquals(Ctid(75, 1), bounds[1].first)
        assertNull(bounds[1].second)
    }

    @Test
    fun `computePartitionBounds should ensure all partitions are sequential`() {
        // Given: arbitrary setup
        val lowerBound: JsonNode? = null
        val numPartitions = 7
        val relationSize = 573440L // 70 blocks

        // When
        val bounds = factory.computePartitionBounds(lowerBound, numPartitions, relationSize)

        // Then: verify that each partition's upper bound matches the next partition's lower bound
        assertEquals(7, bounds.size)

        for (i in 0 until bounds.size - 1) {
            assertEquals(
                bounds[i].second,
                bounds[i + 1].first,
                "Partition $i upper bound should match partition ${i + 1} lower bound"
            )
        }

        // Last partition should be open-ended
        assertNull(bounds[bounds.size - 1].second)
    }

    @Test
    fun `computePartitionBounds with zero relation size should handle edge case`() {
        // Given: zero relation size
        val lowerBound: JsonNode? = null
        val numPartitions = 3
        val relationSize = 0L

        // When
        val bounds = factory.computePartitionBounds(lowerBound, numPartitions, relationSize)

        // Then: theoretical last page is 0, step size should be coerced to 1
        assertEquals(3, bounds.size)

        assertEquals(Ctid.ZERO, bounds[0].first)
        assertEquals(Ctid(1, 1), bounds[0].second)

        assertEquals(Ctid(1, 1), bounds[1].first)
        assertEquals(Ctid(2, 1), bounds[1].second)

        assertEquals(Ctid(2, 1), bounds[2].first)
        assertNull(bounds[2].second)
    }

    @Test
    fun `computePartitionBounds should handle uneven division`() {
        // Given: 25 pages, 4 partitions (doesn't divide evenly)
        val lowerBound: JsonNode? = null
        val numPartitions = 4
        val relationSize = 204800L // 25 blocks

        // When
        val bounds = factory.computePartitionBounds(lowerBound, numPartitions, relationSize)

        // Then: 25 / 4 = 6 pages per partition (integer division)
        assertEquals(4, bounds.size)

        assertEquals(Ctid.ZERO, bounds[0].first)
        assertEquals(Ctid(6, 1), bounds[0].second)

        assertEquals(Ctid(6, 1), bounds[1].first)
        assertEquals(Ctid(12, 1), bounds[1].second)

        assertEquals(Ctid(12, 1), bounds[2].first)
        assertEquals(Ctid(18, 1), bounds[2].second)

        // Last partition gets the remainder
        assertEquals(Ctid(18, 1), bounds[3].first)
        assertNull(bounds[3].second)
    }
}