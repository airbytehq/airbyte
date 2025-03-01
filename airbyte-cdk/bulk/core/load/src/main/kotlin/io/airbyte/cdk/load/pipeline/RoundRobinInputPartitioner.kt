/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import kotlin.math.abs
import kotlin.random.Random

/**
 * Declare a singleton of this type to have input distributed evenly across the input partitions.
 * (The default is to [ByStreamInputPartitioner].)
 */
open class RoundRobinInputPartitioner(private val rotateEveryNRecords: Int = 10_000) :
    InputPartitioner {
    private var nextPartition =
        Random(System.currentTimeMillis()).nextInt(Int.MAX_VALUE / rotateEveryNRecords) *
            rotateEveryNRecords

    override fun getPartition(record: DestinationRecordAirbyteValue, numParts: Int): Int {
        val part = nextPartition++ / rotateEveryNRecords
        return if (part == Int.MIN_VALUE) { // avoid overflow
            0
        } else {
            abs(part) % numParts
        }
    }
}
