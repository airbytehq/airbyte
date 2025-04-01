/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.OutputPartitioner

interface ObjectLoaderCompletedUploadPartitioner<K : WithStream, T : RemoteObject<*>> :
    OutputPartitioner<
        ObjectKey,
        ObjectLoaderPartLoader.PartResult<T>,
        K,
        ObjectLoaderUploadCompleter.UploadResult<T>
    >
