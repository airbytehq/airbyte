/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.OutputPartitioner
import kotlin.random.Random

/**
 * For routing parts to upload workers.
 *
 * The behavior we want is for the upload workers to grab whatever is available which is the default
 * in kotlin for multiple workers reading from a single partition. So just return 1 here.
 */
class ObjectLoaderPartPartitioner<T> : OutputPartitioner<StreamKey, T, ObjectKey, Part> {
    // Start on a random value
    private var nextPartition = Random(System.currentTimeMillis()).nextInt(Int.MAX_VALUE)

    override fun getOutputKey(inputKey: StreamKey, output: Part): ObjectKey {
        return ObjectKey(inputKey.stream, output.key)
    }

    override fun getPart(outputKey: ObjectKey, numParts: Int): Int {
        // Rotate through partitions
        val part = nextPartition++
        return Math.floorMod(part, numParts)
    }
}
