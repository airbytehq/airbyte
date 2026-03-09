/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc.streaming

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class TwoStageSizeEstimatorTest {
    @Test
    fun testDelegationSwitch() {
        val sizeEstimator = TwoStageSizeEstimator.instance
        for (i in 0 until FetchSizeConstants.INITIAL_SAMPLE_SIZE) {
            sizeEstimator.accept("1")
            Assertions.assertTrue(sizeEstimator.delegate is InitialSizeEstimator)
        }
        // delegation is changed after initial sampling
        for (i in 0..2) {
            sizeEstimator.accept("1")
            Assertions.assertTrue(sizeEstimator.delegate is SamplingSizeEstimator)
        }
    }

    @Test
    fun testGetTargetBufferByteSize() {
        Assertions.assertEquals(
            FetchSizeConstants.MIN_BUFFER_BYTE_SIZE,
            TwoStageSizeEstimator.getTargetBufferByteSize(null)
        )
        Assertions.assertEquals(
            FetchSizeConstants.MIN_BUFFER_BYTE_SIZE,
            TwoStageSizeEstimator.getTargetBufferByteSize(Long.MAX_VALUE)
        )
        Assertions.assertEquals(
            FetchSizeConstants.MIN_BUFFER_BYTE_SIZE,
            TwoStageSizeEstimator.getTargetBufferByteSize(
                FetchSizeConstants.MIN_BUFFER_BYTE_SIZE - 10L
            )
        )
        // With 10% ratio and 8Gi heap, buffer should be capped at MAX_BUFFER_BYTE_SIZE
        val eightGiHeap = 8L * 1024L * 1024L * 1024L
        Assertions.assertEquals(
            FetchSizeConstants.MAX_BUFFER_BYTE_SIZE,
            TwoStageSizeEstimator.getTargetBufferByteSize(eightGiHeap)
        )
        // With a smaller heap where 10% is between min and max, should return 10% of heap
        val threeGiHeap = 3L * 1024L * 1024L * 1024L
        val expected = Math.round(threeGiHeap * FetchSizeConstants.TARGET_BUFFER_SIZE_RATIO)
        Assertions.assertEquals(
            expected,
            TwoStageSizeEstimator.getTargetBufferByteSize(threeGiHeap)
        )
    }
}
