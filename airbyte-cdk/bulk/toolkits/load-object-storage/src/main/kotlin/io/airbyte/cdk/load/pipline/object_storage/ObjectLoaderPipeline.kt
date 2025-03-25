/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.pipeline.LoadPipeline
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

/**
 * Three steps:
 *
 * 1. format records into loadable parts (byte arrays destined for specific object keys)
 * 2. stage the parts in object storage
 * 3. finish the uploads as all parts become available
 *
 * Between steps 1<->2 and 2<->3 are single-partition queues:
 *
 * - formatted parts are put on the first queue as they are completed. its size is scaled to the
 * available memory and part size
 * - the upload workers take parts as they become available and upload them, then put fact-of-upload
 * on the second queue
 * - a single completer worker reads the second queue and completes the uploads
 * - state is acked only when the completer finishes each upload
 */
@Singleton
@Requires(bean = ObjectLoader::class)
class ObjectLoaderPipeline(
    partStep: ObjectLoaderPartFormatterStep,
    uploadStep: ObjectLoaderPartLoaderStep,
    completerStep: ObjectLoaderUploadCompleterStep,
) : LoadPipeline(listOf(partStep, uploadStep, completerStep))
