/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc.streaming

import java.util.*

/**
 * This class adjusts the max row byte size by measuring one row out of every `sampleFrequency`
 * rows.
 */
class SamplingSizeEstimator(
    bufferByteSize: Long,
    private val sampleFrequency: Int,
    initialRowByteSize: Double,
    minFetchSize: Int,
    defaultFetchSize: Int,
    maxFetchSize: Int
) :
    BaseSizeEstimator(bufferByteSize, minFetchSize, defaultFetchSize, maxFetchSize),
    FetchSizeEstimator {
    private var counter = 0
    private var hasNewEstimation = false

    init {
        this.maxRowByteSize = initialRowByteSize
    }

    override fun accept(row: Any) {
        counter++
        if (counter < sampleFrequency) {
            return
        }

        counter = 0
        val rowByteSize: Long = getEstimatedByteSize(row)
        if (this.maxRowByteSize < rowByteSize) {
            this.maxRowByteSize = rowByteSize.toDouble()
            hasNewEstimation = true
        }
    }

    override val fetchSize: Optional<Int>
        get() {
            if (!hasNewEstimation) {
                return Optional.empty()
            }

            hasNewEstimation = false
            return Optional.of(boundedFetchSize)
        }
}
