/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage.file

import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderCompletedUploadPartitioner
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadCompleter
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
@Named("fileCompletedOutputPartitioner")
class FileCompletedOutputPartitioner<T : RemoteObject<*>> :
    ObjectLoaderCompletedUploadPartitioner<StreamKey, T> {
    override fun getOutputKey(
        inputKey: ObjectKey,
        output: ObjectLoaderUploadCompleter.UploadResult<T>
    ): StreamKey {
        return StreamKey(inputKey.stream)
    }

    override fun getPart(outputKey: StreamKey, inputPart: Int, numParts: Int): Int {
        return 0
    }
}
