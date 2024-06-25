/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc.streaming

import java.util.*

/**
 * This class estimates the max row byte size by measuring the first consecutive `initialSampleSize`
 * rows.
 */
class InitialSizeEstimator(
    bufferByteSize: Long,
    private val sampleSize: Int,
    minFetchSize: Int,
    defaultFetchSize: Int,
    maxFetchSize: Int
) :
    BaseSizeEstimator(bufferByteSize, minFetchSize, defaultFetchSize, maxFetchSize),
    FetchSizeEstimator {
    private var counter = 0

    override fun accept(row: Any) {
        val byteSize: Long = getEstimatedByteSize(row)
        if (maxRowByteSize < byteSize) {
            maxRowByteSize = byteSize.toDouble()
        }
        counter++
    }

    override val fetchSize: Optional<Int>
        get() {
            if (counter < sampleSize) {
                return Optional.empty()
            }
            return Optional.of(boundedFetchSize)
        }
}
