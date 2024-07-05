/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc.streaming

import io.airbyte.commons.json.Jsons
import java.util.*
import java.util.Map
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class BaseSizeEstimatorTest {
    @Test
    fun testGetEstimatedByteSize() {
        Assertions.assertEquals(0L, BaseSizeEstimator.getEstimatedByteSize(null))
        Assertions.assertEquals(21L, BaseSizeEstimator.getEstimatedByteSize("12345"))
        Assertions.assertEquals(
            45L,
            BaseSizeEstimator.getEstimatedByteSize(Jsons.jsonNode(Map.of("key", "value")))
        )
    }

    class TestSizeEstimator(
        bufferByteSize: Long,
        minFetchSize: Int,
        defaultFetchSize: Int,
        maxFetchSize: Int
    ) : BaseSizeEstimator(bufferByteSize, minFetchSize, defaultFetchSize, maxFetchSize) {
        override val fetchSize: Optional<Int> = Optional.empty()

        override fun accept(o: Any) {}

        fun setMeanByteSize(meanByteSize: Double) {
            this.maxRowByteSize = meanByteSize
        }
    }

    @Test
    fun testGetBoundedFetchSize() {
        val bufferByteSize: Long = 120
        val minFetchSize = 10
        val defaultFetchSize = 20
        val maxFetchSize = 40
        val sizeEstimator =
            TestSizeEstimator(bufferByteSize, minFetchSize, defaultFetchSize, maxFetchSize)

        sizeEstimator.setMeanByteSize(-1.0)
        Assertions.assertEquals(defaultFetchSize, sizeEstimator.boundedFetchSize)

        sizeEstimator.setMeanByteSize(0.0)
        Assertions.assertEquals(defaultFetchSize, sizeEstimator.boundedFetchSize)

        // fetch size = 5 < min fetch size
        sizeEstimator.setMeanByteSize(bufferByteSize / 5.0)
        Assertions.assertEquals(minFetchSize, sizeEstimator.boundedFetchSize)

        // fetch size = 10 within [min fetch size, max fetch size]
        sizeEstimator.setMeanByteSize(bufferByteSize / 10.0)
        Assertions.assertEquals(10, sizeEstimator.boundedFetchSize)

        // fetch size = 30 within [min fetch size, max fetch size]
        sizeEstimator.setMeanByteSize(bufferByteSize / 30.0)
        Assertions.assertEquals(30, sizeEstimator.boundedFetchSize)

        // fetch size = 40 within [min fetch size, max fetch size]
        sizeEstimator.setMeanByteSize(bufferByteSize / 40.0)
        Assertions.assertEquals(40, sizeEstimator.boundedFetchSize)

        // fetch size = 60 > max fetch size
        sizeEstimator.setMeanByteSize(bufferByteSize / 60.0)
        Assertions.assertEquals(maxFetchSize, sizeEstimator.boundedFetchSize)
    }
}
