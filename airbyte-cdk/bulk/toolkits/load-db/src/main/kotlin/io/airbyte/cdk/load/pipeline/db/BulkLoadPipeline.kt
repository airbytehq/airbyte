/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.db

import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.LoadPipeline
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartStep
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPipeline
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadStep
import io.airbyte.cdk.load.write.db.BulkLoaderFactory
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Requires(bean = BulkLoaderFactory::class)
@Replaces(ObjectLoaderPipeline::class)
class BulkLoadPipeline<K : WithStream, T : RemoteObject<*>>(
    partStep: ObjectLoaderPartStep,
    uploadStep: ObjectLoaderUploadStep<K, T>,
    loadIntoTableStep: BulkLoadIntoTableStep<*, *>,
) : LoadPipeline(listOf(partStep, uploadStep, loadIntoTableStep))
