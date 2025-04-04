/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.db

import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderCompletedUploadPartitioner
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadCompleter
import io.airbyte.cdk.load.write.db.BulkLoaderFactory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

@Singleton
@Secondary
@Requires(bean = BulkLoaderFactory::class)
class BulkLoadCompletedUploadPartitioner<T : RemoteObject<*>> :
    ObjectLoaderCompletedUploadPartitioner<StreamKey, T> {
    override fun getOutputKey(
        inputKey: ObjectKey,
        output: ObjectLoaderUploadCompleter.UploadResult<T>
    ): StreamKey {
        return StreamKey(inputKey.stream)
    }

    override fun getPart(outputKey: StreamKey, numParts: Int): Int {
        return Math.floorMod(outputKey.stream.hashCode(), numParts)
    }
}
