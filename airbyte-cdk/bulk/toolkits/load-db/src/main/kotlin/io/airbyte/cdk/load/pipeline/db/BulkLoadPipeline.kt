/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.db

import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.LoadPipeline
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartFormatterStep
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartLoaderStep
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPipeline
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadCompleterStep
import io.airbyte.cdk.load.write.db.BulkLoaderFactory
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Requires(bean = BulkLoaderFactory::class)
@Replaces(ObjectLoaderPipeline::class)
class BulkLoadPipeline<K : WithStream, T : RemoteObject<*>>(
    formatterStep: ObjectLoaderPartFormatterStep,
    loaderStep: ObjectLoaderPartLoaderStep<T>,
    completerStep: ObjectLoaderUploadCompleterStep<K, T>,
    loadIntoTableStep: BulkLoaderLoadIntoTableStep<K, T>,
) : LoadPipeline(listOf(formatterStep, loaderStep, completerStep, loadIntoTableStep))
