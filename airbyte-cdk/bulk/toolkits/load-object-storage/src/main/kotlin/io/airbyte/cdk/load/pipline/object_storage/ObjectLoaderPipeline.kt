/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.LoadPipeline
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.pipline.object_storage.file.FileChunkStep
import io.airbyte.cdk.load.pipline.object_storage.file.ForwardFileRecordStep
import io.airbyte.cdk.load.pipline.object_storage.file.ProcessFileTaskLegacyStep
import io.airbyte.cdk.load.pipline.object_storage.file.RouteEventStep
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton

/**
 * Three steps for default record flow:
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
 *
 * There are 8 steps for the file and record flow.
 *
 * Composed of 5 new steps (File Pipe) that feed into the same 3 steps as above (Record Pipe).
 *
 * The new steps are as follows:
 * 1. Routes the record message to either through file pipe or straight to the record pipe if it's
 * not related to a file based stream.
 * 2. Read file reference from the incoming record, open the file and read into chunks, emitting
 * them as "Part"s downstream.
 * 3. Uploads file parts
 * 4. Completes multipart file uploads.
 * 5. Passes the related record on to the record pipe (see above)
 */
@Singleton
@Requires(bean = ObjectLoader::class)
class ObjectLoaderPipeline<K : WithStream, T : RemoteObject<*>>(
    routeEventStep: RouteEventStep?,
    fileChunkStep: FileChunkStep<T>?,
    @Named("filePartLoaderStep") fileChunkUploader: ObjectLoaderPartLoaderStep<T>?,
    @Named("fileUploadCompleterStep") fileCompleterStep: ObjectLoaderUploadCompleterStep<K, T>?,
    forwardFileRecordStep: ForwardFileRecordStep<T>?,
    @Named("fileRecordPartFormatterStep") fileRecordFormatStep: ObjectLoaderPartFormatterStep?,
    @Named("recordPartFormatterStep") recordFormatStep: ObjectLoaderPartFormatterStep,
    @Named("recordPartLoaderStep") recordUploadStep: ObjectLoaderPartLoaderStep<T>,
    @Named("recordUploadCompleterStep") recordCompleterStep: ObjectLoaderUploadCompleterStep<K, T>,
    @Value("\${airbyte.destination.core.file-transfer.enabled}") isLegacyFileTransfer: Boolean,
    processFileTaskLegacyStep: ProcessFileTaskLegacyStep,
    @Named("isFileTransfer") isFileTransfer: Boolean,
    @Named("oneShotObjectLoaderStep")
    oneShotObjectLoaderStep: ObjectLoaderOneShotUploaderStep<K, T>,
    @Named("dataChannelMedium") dataChannelMedium: DataChannelMedium,
) :
    LoadPipeline(
        selectPipelineSteps(
            isFileTransfer,
            routeEventStep,
            fileChunkStep,
            fileChunkUploader,
            fileCompleterStep,
            forwardFileRecordStep,
            fileRecordFormatStep,
            recordFormatStep,
            recordUploadStep,
            recordCompleterStep,
            isLegacyFileTransfer,
            processFileTaskLegacyStep,
            oneShotObjectLoaderStep,
            dataChannelMedium
        )
    ) {
    companion object {
        fun <K : WithStream, T : RemoteObject<*>> selectPipelineSteps(
            isFileTransfer: Boolean,
            routeEventStep: RouteEventStep?,
            fileChunkStep: FileChunkStep<T>?,
            fileChunkUploader: ObjectLoaderPartLoaderStep<T>?,
            fileCompleterStep: ObjectLoaderUploadCompleterStep<K, T>?,
            forwardFileRecordStep: ForwardFileRecordStep<T>?,
            fileRecordFormatStep: ObjectLoaderPartFormatterStep?,
            recordPartStep: ObjectLoaderPartFormatterStep,
            recordUploadStep: ObjectLoaderPartLoaderStep<T>,
            recordCompleterStep: ObjectLoaderUploadCompleterStep<K, T>,
            isLegacyFileTransfer: Boolean,
            legacyProcessFileStep: ProcessFileTaskLegacyStep,
            oneShotObjectLoaderStep: ObjectLoaderOneShotUploaderStep<K, T>,
            dataChannelMedium: DataChannelMedium
        ): List<LoadPipelineStep> {
            return if (dataChannelMedium == DataChannelMedium.SOCKET) {
                listOf(oneShotObjectLoaderStep)
            } else if (isFileTransfer) {
                listOf(
                    routeEventStep!!,
                    fileChunkStep!!,
                    fileChunkUploader!!,
                    fileCompleterStep!!,
                    forwardFileRecordStep!!,
                    fileRecordFormatStep!!,
                    recordUploadStep,
                    recordCompleterStep,
                )
            } else {
                listOf(
                    if (isLegacyFileTransfer) {
                        legacyProcessFileStep
                    } else {
                        recordPartStep
                    },
                    recordUploadStep,
                    recordCompleterStep,
                )
            }
        }
    }
}
