/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.LoadPipeline
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Requires(bean = ObjectLoader::class)
class ObjectLoaderPipeline<K : WithStream, T : RemoteObject<*>>(
    partStep: ObjectLoaderPartStep,
    uploadStep: ObjectLoaderUploadStep<K, T>
) : LoadPipeline(listOf(partStep, uploadStep))
