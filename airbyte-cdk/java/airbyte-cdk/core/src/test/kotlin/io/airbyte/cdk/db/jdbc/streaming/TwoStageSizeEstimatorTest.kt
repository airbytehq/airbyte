/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
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
    }
}
