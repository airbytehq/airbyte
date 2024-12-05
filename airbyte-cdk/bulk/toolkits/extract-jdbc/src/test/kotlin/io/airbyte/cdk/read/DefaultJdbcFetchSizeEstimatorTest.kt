/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.read.Sample.Kind
import io.airbyte.cdk.read.TestFixtures.sharedState
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class DefaultJdbcFetchSizeEstimatorTest {

    @Test
    fun testSingleSmall() {
        val sample = Sample(listOf(10L, 20L, 30L), Kind.SMALL, valueWeight = 0L)
        val sharedState = sharedState(maxMemoryBytesForTesting = 700_000, maxConcurrency = 1)
        val estimator = sharedState.jdbcFetchSizeEstimator()
        Assertions.assertEquals(14_000, estimator.apply(sample))
    }

    @Test
    fun testTwoSmall() {
        val sample = Sample(listOf(10L, 20L, 30L), Kind.SMALL, valueWeight = 0L)
        val sharedState = sharedState(maxMemoryBytesForTesting = 700_000, maxConcurrency = 2)
        val estimator = sharedState.jdbcFetchSizeEstimator()
        Assertions.assertEquals(7_000, estimator.apply(sample))
    }

    @Test
    fun testEmpty() {
        val sample = Sample(listOf<Long>(), Kind.EMPTY, 0L)
        val sharedState = sharedState(maxMemoryBytesForTesting = 700_000, maxConcurrency = 2)
        val estimator = sharedState.jdbcFetchSizeEstimator()
        Assertions.assertEquals(sharedState.constants.defaultFetchSize, estimator.apply(sample))
    }
}
