/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc.streaming

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class SamplingSizeEstimatorTest {
    @Test
    fun testIt() {
        val bufferByteSize: Long = 120
        val sampleFrequency = 3
        val initialByteSize: Long = 10
        val minFetchSize = 1
        val defaultFetchSize = 20
        val maxFetchSize = 120
        val sizeEstimator =
            SamplingSizeEstimator(
                bufferByteSize,
                sampleFrequency,
                initialByteSize.toDouble(),
                minFetchSize,
                defaultFetchSize,
                maxFetchSize
            )

        var maxByteSize = initialByteSize.toDouble()

        // size: 3 * 3 = 12, not sampled
        sizeEstimator.accept("1")
        Assertions.assertFalse(sizeEstimator.fetchSize.isPresent)
        Assertions.assertEquals(maxByteSize, sizeEstimator.maxRowByteSize)

        // size: 4 * 3 = 16, not sampled
        sizeEstimator.accept("11")
        Assertions.assertFalse(sizeEstimator.fetchSize.isPresent)
        Assertions.assertEquals(maxByteSize, sizeEstimator.maxRowByteSize)

        // size: 5 * 3 = 15, sampled, fetch size is ready
        sizeEstimator.accept("111")
        val fetchSize1 = sizeEstimator.fetchSize
        maxByteSize = 15.0
        assertDoubleEquals(15.0, sizeEstimator.maxRowByteSize)
        assertDoubleEquals(bufferByteSize / maxByteSize, fetchSize1.get().toDouble())

        // size: 6 * 3 = 24, not sampled
        sizeEstimator.accept("1111")
        Assertions.assertFalse(sizeEstimator.fetchSize.isPresent)
        assertDoubleEquals(maxByteSize, sizeEstimator.maxRowByteSize)

        // size: 7 * 3 = 28, not sampled
        sizeEstimator.accept("11111")
        Assertions.assertFalse(sizeEstimator.fetchSize.isPresent)
        assertDoubleEquals(maxByteSize, sizeEstimator.maxRowByteSize)

        // size: 8 * 3 = 24, sampled, fetch size is ready
        sizeEstimator.accept("111111")
        val fetchSize2 = sizeEstimator.fetchSize
        Assertions.assertTrue(fetchSize2.isPresent)
        maxByteSize = 24.0
        assertDoubleEquals(maxByteSize, sizeEstimator.maxRowByteSize)
        assertDoubleEquals(bufferByteSize / maxByteSize, fetchSize2.get().toDouble())
    }

    companion object {
        private fun assertDoubleEquals(expected: Double, actual: Double) {
            Assertions.assertEquals(Math.round(expected), Math.round(actual))
        }
    }
}
