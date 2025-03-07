/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.OutputPartitioner
import kotlin.math.abs
import kotlin.random.Random

/**
 * For routing parts to upload workers.
 *
 * The key is the object key (filename). This means that the framework will keep separate state per
 * upload-in-progress.
 *
 * The partition is round-robin, for maximum concurrency.
 */
class ObjectLoaderPartPartitioner :
    OutputPartitioner<StreamKey, DestinationRecordAirbyteValue, ObjectKey, Part> {
    // Start on a random value
    private var nextPartition = Random(System.currentTimeMillis()).nextInt(Int.MAX_VALUE)

    override fun getOutputKey(inputKey: StreamKey, output: Part): ObjectKey {
        return ObjectKey(inputKey.stream, output.key)
    }

    override fun getPart(outputKey: ObjectKey, numParts: Int): Int {
        // Rotate through partitions
        val part = nextPartition++
        return if (part == Int.MIN_VALUE) { // avoid overflow
            0
        } else {
            abs(part) % numParts
        }
    }
}
