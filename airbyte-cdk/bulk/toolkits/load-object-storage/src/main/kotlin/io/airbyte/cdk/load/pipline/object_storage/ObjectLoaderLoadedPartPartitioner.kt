/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.OutputPartitioner

/**
 * The technically correct partitioning is round-robin, but since we use
 * [io.airbyte.cdk.load.message.SinglePartitionQueueWithMultiPartitionBroadcast], the partition is
 * immaterial, so it's simpler just to return 0 here.
 */
class ObjectLoaderLoadedPartPartitioner<K : WithStream, T> :
    OutputPartitioner<K, T, ObjectKey, ObjectLoaderPartLoader.PartResult> {
    override fun getOutputKey(inputKey: K, output: ObjectLoaderPartLoader.PartResult): ObjectKey {
        return ObjectKey(inputKey.stream, output.objectKey)
    }

    override fun getPart(outputKey: ObjectKey, numParts: Int): Int {
        return 0
    }
}
