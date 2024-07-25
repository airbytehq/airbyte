/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc.streaming

import com.google.common.annotations.VisibleForTesting
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import kotlin.math.max

private val LOGGER = KotlinLogging.logger {}
/**
 * This estimator first uses the [InitialSizeEstimator] to calculate an initial fetch size by
 * sampling the first N rows consecutively, and then switches to [SamplingSizeEstimator] to
 * periodically adjust the fetch size by sampling every M rows.
 */
class TwoStageSizeEstimator private constructor() : FetchSizeEstimator {
    private val initialSampleSize = FetchSizeConstants.INITIAL_SAMPLE_SIZE

    @get:VisibleForTesting
    var delegate: BaseSizeEstimator
        private set
    private var counter = 0

    init {
        this.delegate =
            InitialSizeEstimator(
                FetchSizeConstants.MIN_BUFFER_BYTE_SIZE,
                initialSampleSize,
                FetchSizeConstants.MIN_FETCH_SIZE,
                FetchSizeConstants.DEFAULT_FETCH_SIZE,
                FetchSizeConstants.MAX_FETCH_SIZE
            )
    }

    override val fetchSize: Optional<Int>
        get() = delegate.fetchSize

    override fun accept(rowData: Any) {
        if (counter <= initialSampleSize + 1) {
            counter++
            // switch to SamplingSizeEstimator after the initial N rows
            if (delegate is InitialSizeEstimator && counter > initialSampleSize) {
                delegate =
                    SamplingSizeEstimator(
                        getTargetBufferByteSize(Runtime.getRuntime().maxMemory()),
                        FetchSizeConstants.SAMPLE_FREQUENCY,
                        delegate.maxRowByteSize,
                        FetchSizeConstants.MIN_FETCH_SIZE,
                        FetchSizeConstants.DEFAULT_FETCH_SIZE,
                        FetchSizeConstants.MAX_FETCH_SIZE
                    )
            }
        }

        delegate.accept(rowData)
    }

    companion object {

        val instance: TwoStageSizeEstimator
            get() = TwoStageSizeEstimator()

        @VisibleForTesting
        fun getTargetBufferByteSize(maxMemory: Long?): Long {
            if (maxMemory == null || maxMemory == Long.MAX_VALUE) {
                LOGGER.info {
                    "No max memory limit found, use min JDBC buffer size: ${FetchSizeConstants.MIN_BUFFER_BYTE_SIZE}"
                }
                return FetchSizeConstants.MIN_BUFFER_BYTE_SIZE
            }
            val targetBufferByteSize =
                Math.round(maxMemory * FetchSizeConstants.TARGET_BUFFER_SIZE_RATIO)
            val finalBufferByteSize =
                max(
                        FetchSizeConstants.MIN_BUFFER_BYTE_SIZE.toDouble(),
                        targetBufferByteSize.toDouble()
                    )
                    .toLong()
            LOGGER.info { "Max memory limit: $maxMemory, JDBC buffer size: $finalBufferByteSize" }
            return finalBufferByteSize
        }
    }
}
