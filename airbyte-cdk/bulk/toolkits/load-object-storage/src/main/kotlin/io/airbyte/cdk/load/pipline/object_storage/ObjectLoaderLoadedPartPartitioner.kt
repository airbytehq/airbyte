/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.OutputPartitioner

/**
 * Distribute the loaded parts to the upload completers by key. (Distributing the completes
 * efficiently is not as important as not forcing the uploaders to coordinate with each other, so
 * instead we focus on operational simplicity: all fact-of-loaded part signals for the same key go
 * to the same upload completer.)
 */
class ObjectLoaderLoadedPartPartitioner<K : WithStream, T, U : RemoteObject<*>> :
    OutputPartitioner<K, T, ObjectKey, ObjectLoaderPartLoader.PartResult<U>> {

    override fun getOutputKey(
        inputKey: K,
        output: ObjectLoaderPartLoader.PartResult<U>
    ): ObjectKey {
        return ObjectKey(inputKey.stream, output.objectKey)
    }

    override fun getPart(outputKey: ObjectKey, numParts: Int): Int {
        return Math.floorMod(outputKey.objectKey.hashCode(), numParts)
    }
}
