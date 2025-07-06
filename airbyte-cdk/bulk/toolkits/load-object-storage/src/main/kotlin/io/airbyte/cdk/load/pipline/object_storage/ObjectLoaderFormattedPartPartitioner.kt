/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.OutputPartitioner
import kotlin.random.Random

/**
 * Distribute the parts randomly across loaders. (Testing shows this is the most efficient pattern.)
 */
class ObjectLoaderFormattedPartPartitioner<K : WithStream, T> :
    OutputPartitioner<K, T, ObjectKey, ObjectLoaderPartFormatter.FormattedPart> {
    private val prng = Random(System.currentTimeMillis())

    override fun getOutputKey(
        inputKey: K,
        output: ObjectLoaderPartFormatter.FormattedPart
    ): ObjectKey {
        return ObjectKey(inputKey.stream, output.part.key)
    }

    override fun getPart(outputKey: ObjectKey, inputPart: Int, numParts: Int): Int {
        return prng.nextInt(numParts)
    }
}
