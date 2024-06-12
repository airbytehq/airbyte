/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc.streaming

import com.google.common.annotations.VisibleForTesting
import io.airbyte.commons.json.Jsons
import kotlin.math.max
import kotlin.math.min

/** Fetch size (number of rows) = target buffer byte size / max row byte size */
abstract class BaseSizeEstimator
protected constructor( // desired buffer size in memory
    private val targetBufferByteSize: Long,
    private val minFetchSize: Int,
    private val defaultFetchSize: Int,
    private val maxFetchSize: Int
) : FetchSizeEstimator {
    var maxRowByteSize: Double = 0.0
        protected set

    val boundedFetchSize: Int
        /**
         * This method ensures that the fetch size is between `minFetchSize` and `maxFetchSize`,
         * inclusively.
         */
        get() {
            if (maxRowByteSize <= 0.0) {
                return defaultFetchSize
            }
            val rawFetchSize = Math.round(targetBufferByteSize / maxRowByteSize)
            if (rawFetchSize > Int.MAX_VALUE) {
                return maxFetchSize
            }
            return max(
                    minFetchSize.toDouble(),
                    min(maxFetchSize.toDouble(), rawFetchSize.toInt().toDouble())
                )
                .toInt()
        }

    companion object {
        /**
         * What we really want is to know how much memory each `rowData` takes. However, there is no
         * easy way to measure that. So we use the byte size of the serialized row to approximate
         * that.
         */
        @VisibleForTesting
        fun getEstimatedByteSize(rowData: Any?): Long {
            if (rowData == null) {
                return 0L
            }

            // The string length is multiplied by 4 assuming each character is a
            // full UTF-8 character. In reality, a UTF-8 character is encoded as
            // 1 to 4 bytes. So this is an overestimation. This is alright, because
            // the whole method only provides an estimation. Please never convert
            // the string to byte[] to get the exact length. That conversion is known
            // to introduce a lot of memory overhead.
            //
            // We are using 3L as the median byte-size of a serialized char here assuming that most
            // chars fit
            // into the ASCII space (fewer bytes)
            return Jsons.serialize(rowData).length * 3L
        }
    }
}
