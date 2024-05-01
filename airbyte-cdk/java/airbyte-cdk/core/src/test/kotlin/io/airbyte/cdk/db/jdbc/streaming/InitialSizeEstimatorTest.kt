/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc.streaming

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class InitialSizeEstimatorTest {
    @Test
    fun testIt() {
        val bufferByteSize: Long = 120
        val initialSampleSize = 5
        val minFetchSize = 1
        val defaultFetchSize = 20
        val maxFetchSize = 120
        val sizeEstimator =
            InitialSizeEstimator(
                bufferByteSize,
                initialSampleSize,
                minFetchSize,
                defaultFetchSize,
                maxFetchSize
            )

        // size: 3 * 4 = 12
        sizeEstimator.accept("1")
        Assertions.assertFalse(sizeEstimator.fetchSize.isPresent)
        // size: 4 * 4 = 16
        sizeEstimator.accept("11")
        Assertions.assertFalse(sizeEstimator.fetchSize.isPresent)
        // size: 5 * 4 = 20
        sizeEstimator.accept("111")
        Assertions.assertFalse(sizeEstimator.fetchSize.isPresent)
        // size: 6 * 4 = 24
        sizeEstimator.accept("1111")
        Assertions.assertFalse(sizeEstimator.fetchSize.isPresent)
        // size: 7 * 4 = 28, fetch size is available
        sizeEstimator.accept("11111")
        val fetchSize = sizeEstimator.fetchSize
        Assertions.assertTrue(fetchSize.isPresent)
        val expectedMaxByteSize = 21L
        Assertions.assertEquals(expectedMaxByteSize, Math.round(sizeEstimator.maxRowByteSize))
        Assertions.assertEquals(
            (bufferByteSize / expectedMaxByteSize) + 1,
            fetchSize.get().toLong()
        ) // + 1 needed for int remainder rounding
    }
}
