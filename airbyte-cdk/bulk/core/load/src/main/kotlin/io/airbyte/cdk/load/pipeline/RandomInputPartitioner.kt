/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.message.DestinationRecordRaw
import kotlin.random.Random

class RandomInputPartitioner : InputPartitioner {
    private val prng = Random(System.currentTimeMillis())

    override fun getPartition(record: DestinationRecordRaw, numParts: Int): Int {
        return prng.nextInt(numParts)
    }
}
