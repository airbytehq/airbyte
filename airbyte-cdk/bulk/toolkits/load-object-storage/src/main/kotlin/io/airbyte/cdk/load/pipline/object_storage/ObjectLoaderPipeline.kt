/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.LoadPipeline
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.pipline.object_storage.file.FileChunkStep
import io.airbyte.cdk.load.pipline.object_storage.file.ForwardFileRecordStep
import io.airbyte.cdk.load.pipline.object_storage.file.RouteEventStep
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
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
//@Singleton
//@Requires(bean = ObjectLoader::class)
@Requires(property = "airbyte.destination.core.file-transfer.enabled", value = "false")
class ObjectLoaderPipeline<K : WithStream, T : RemoteObject<*>>(
    partStep: ObjectLoaderPartFormatterStep,
    @Named("recordPartLoaderStep") uploadStep: ObjectLoaderPartLoaderStep<T>,
    @Named("recordUploadCompleterStep") completerStep: ObjectLoaderUploadCompleterStep<K, T>,
) : LoadPipeline(listOf(partStep, uploadStep, completerStep))

@Singleton
@Requires(bean = ObjectLoader::class)
class ObjectLoaderPipelineWithFileSupport<K : WithStream, T : RemoteObject<*>>(
    catalog: DestinationCatalog,
    routeEventStep: RouteEventStep,
    fileChunkStep: FileChunkStep<T>,
    @Named("filePartLoaderStep") fileChunkUploader: ObjectLoaderPartLoaderStep<T>,
    @Named("fileUploadCompleterStep") fileCompleterStep: ObjectLoaderUploadCompleterStep<K, T>,
    forwardFileRecordStep: ForwardFileRecordStep<T>,
    @Named("fileRecordPartFormatterStep") recordPartStep: ObjectLoaderPartFormatterStep,
    @Named("recordPartLoaderStep") recordUploadStep: ObjectLoaderPartLoaderStep<T>,
    @Named("recordUploadCompleterStep") recordCompleterStep: ObjectLoaderUploadCompleterStep<K, T>
) : LoadPipeline(selectPipelineSteps(
    catalog,
    routeEventStep,
    fileChunkStep,
    fileChunkUploader,
    fileCompleterStep,
    forwardFileRecordStep,
    recordPartStep,
    recordUploadStep,
    recordCompleterStep,
)) {
    companion object {
        fun hasFileTransfer(catalog: DestinationCatalog): Boolean =
            catalog.streams.any { it.includeFiles }

        fun <K : WithStream, T : RemoteObject<*>> selectPipelineSteps(
            catalog: DestinationCatalog,
            routeEventStep: RouteEventStep,
            fileChunkStep: FileChunkStep<T>,
            @Named("filePartLoaderStep") fileChunkUploader: ObjectLoaderPartLoaderStep<T>,
            @Named("fileUploadCompleterStep") fileCompleterStep: ObjectLoaderUploadCompleterStep<K, T>,
            forwardFileRecordStep: ForwardFileRecordStep<T>,
            @Named("fileRecordPartFormatterStep") recordPartStep: ObjectLoaderPartFormatterStep,
            @Named("recordPartLoaderStep") recordUploadStep: ObjectLoaderPartLoaderStep<T>,
            @Named("recordUploadCompleterStep") recordCompleterStep: ObjectLoaderUploadCompleterStep<K, T>,
        ): List<LoadPipelineStep> {
            return if (hasFileTransfer(catalog)) {
                listOf(
                    routeEventStep,
                    fileChunkStep,
                    fileChunkUploader,
                    fileCompleterStep,
                    forwardFileRecordStep,
                    recordPartStep,
                    recordUploadStep,
                    recordCompleterStep,
                )
            } else {
                listOf(recordPartStep, recordUploadStep, recordCompleterStep)
            }
        }
    }
}
