/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.OutputPartitioner

interface ObjectLoaderCompletedUploadPartitioner<
    K1 : WithStream, T, K2 : WithStream, U : RemoteObject<*>> :
    OutputPartitioner<K1, T, K2, ObjectLoaderUploadCompleter.UploadResult<U>>
