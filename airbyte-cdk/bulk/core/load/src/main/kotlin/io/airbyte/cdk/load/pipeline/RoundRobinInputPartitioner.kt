/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.message.DestinationRecordRaw
import kotlin.random.Random

/**
 * Declare a singleton of this type to have input distributed evenly across the input partitions.
 * (The default is to [ByStreamInputPartitioner].)
 *
 * [rotateEveryNRecords] determines how often to rotate to the next partition. In testing, 10_000
 * seems to be the sweet spot between too much context switching and not enough load balancing.
 */
open class RoundRobinInputPartitioner(private val rotateEveryNRecords: Int = 10_000) :
    InputPartitioner {
    private var nextPartition =
        Random(System.currentTimeMillis()).nextInt(Int.MAX_VALUE / rotateEveryNRecords) *
            rotateEveryNRecords

    override fun getPartition(record: DestinationRecordRaw, numParts: Int): Int {
        val part = nextPartition++ / rotateEveryNRecords
        return Math.floorMod(part, numParts)
    }
}
