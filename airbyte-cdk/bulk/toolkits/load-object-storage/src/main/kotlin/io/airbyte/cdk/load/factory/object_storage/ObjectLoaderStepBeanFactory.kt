/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.factory.object_storage

import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.PipelineFlushStrategy
import io.airbyte.cdk.load.pipline.object_storage.ObjectKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderCompletedUploadPartitioner
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderOneShotUploader
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderOneShotUploaderStep
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartFormatter
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartFormatterStep
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartLoader
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartLoaderStep
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadCompleter
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadCompleterStep
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory
import io.airbyte.cdk.load.write.object_storage.FilePartAccumulatorFactory
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.OutputStream
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.sync.Semaphore

@Factory
class ObjectLoaderStepBeanFactory {
    @Named("recordPartFormatterStep")
    @Singleton
    fun <T : OutputStream> recordPartFormatter(
        @Named("numInputPartitions") numInputPartitions: Int,
        partFormatter: ObjectLoaderPartFormatter<T>,
        @Named("dataChannelInputFlows")
        inputFlows: Array<Flow<PipelineEvent<StreamKey, DestinationRecordRaw>>>,
        @Named("objectLoaderPartQueue")
        outputQueue:
            PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>,
        taskFactory: LoadPipelineStepTaskFactory,
        flushStrategy: PipelineFlushStrategy,
    ) =
        ObjectLoaderPartFormatterStep(
            numInputPartitions,
            partFormatter,
            inputFlows,
            outputQueue,
            taskFactory,
            "record-part-formatter-step",
            flushStrategy,
        )

    @Named("recordPartLoaderStep")
    @Singleton
    fun <T : RemoteObject<*>> recordPartLoader(
        loader: ObjectLoader,
        partLoader: ObjectLoaderPartLoader<T>,
        @Named("objectLoaderPartQueue")
        inputQueue:
            PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>,
        @Named("objectLoaderLoadedPartQueue")
        outputQueue:
            PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult<T>>>,
        taskFactory: LoadPipelineStepTaskFactory,
    ) =
        ObjectLoaderPartLoaderStep(
            loader,
            partLoader,
            inputQueue,
            outputQueue,
            taskFactory,
            "record-part-loader-step",
        )

    @Named("filePartLoaderStep")
    @Singleton
    @Requires(condition = IsFileTransferCondition::class)
    fun <T : RemoteObject<*>> filePartLoader(
        loader: ObjectLoader,
        partLoader: ObjectLoaderPartLoader<T>,
        @Named("filePartQueue")
        inputQueue:
            PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>,
        @Named("fileLoadedPartQueue")
        outputQueue:
            PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult<T>>>,
        taskFactory: LoadPipelineStepTaskFactory,
    ) =
        ObjectLoaderPartLoaderStep(
            loader,
            partLoader,
            inputQueue,
            outputQueue,
            taskFactory,
            "file-part-loader-step",
        )

    @Named("recordUploadCompleterStep")
    @Singleton
    fun <K : WithStream, T : RemoteObject<*>> recordUploadCompleter(
        objectLoader: ObjectLoader,
        uploadCompleter: ObjectLoaderUploadCompleter<T>,
        @Named("objectLoaderLoadedPartQueue")
        inputQueue:
            PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult<T>>>,
        @Named("objectLoaderCompletedUploadQueue")
        completedUploadQueue:
            PartitionedQueue<PipelineEvent<K, ObjectLoaderUploadCompleter.UploadResult<T>>>? =
            null,
        completedUploadPartitioner:
            ObjectLoaderCompletedUploadPartitioner<
                ObjectKey, ObjectLoaderPartLoader.PartResult<T>, K, T>? =
            null,
        taskFactory: LoadPipelineStepTaskFactory,
    ) =
        ObjectLoaderUploadCompleterStep<K, T>(
            objectLoader,
            uploadCompleter,
            inputQueue,
            completedUploadQueue,
            completedUploadPartitioner,
            taskFactory,
            "record-upload-completer-step",
        )

    @Named("fileUploadCompleterStep")
    @Singleton
    @Requires(condition = IsFileTransferCondition::class)
    fun <K : WithStream, T : RemoteObject<*>> fileUploadCompleter(
        objectLoader: ObjectLoader,
        uploadCompleter: ObjectLoaderUploadCompleter<T>,
        @Named("fileLoadedPartQueue")
        inputQueue:
            PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult<T>>>,
        @Named("fileCompletedQueue")
        completedUploadQueue:
            PartitionedQueue<PipelineEvent<K, ObjectLoaderUploadCompleter.UploadResult<T>>>? =
            null,
        @Named("fileCompletedOutputPartitioner")
        completedUploadPartitioner:
            ObjectLoaderCompletedUploadPartitioner<
                ObjectKey, ObjectLoaderPartLoader.PartResult<T>, K, T>? =
            null,
        taskFactory: LoadPipelineStepTaskFactory,
    ) =
        ObjectLoaderUploadCompleterStep(
            objectLoader,
            uploadCompleter,
            inputQueue,
            completedUploadQueue,
            completedUploadPartitioner,
            taskFactory,
            "file-upload-completer-step",
        )

    @Named("fileRecordPartFormatterStep")
    @Singleton
    @Requires(condition = IsFileTransferCondition::class)
    fun <T : OutputStream> fileRecordPartFormatterStep(
        @Named("numInputPartitions") numInputPartitions: Int,
        partFormatter: ObjectLoaderPartFormatter<T>,
        @Named("recordQueue")
        inputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
        @Named("objectLoaderPartQueue")
        outputQueue:
            PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>,
        taskFactory: LoadPipelineStepTaskFactory,
        flushStrategy: PipelineFlushStrategy,
    ) =
        ObjectLoaderPartFormatterStep(
            numInputPartitions,
            partFormatter,
            inputQueue.asOrderedFlows(),
            outputQueue,
            taskFactory,
            "file-record-part-formatter-step",
            flushStrategy,
        )

    @Singleton
    fun legacyFilePartAccumulatorFactory(
        pathFactory: ObjectStoragePathFactory,
        @Named("objectLoaderPartQueue")
        outputQueue:
            PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>,
        loadStrategy: ObjectLoader
    ): FilePartAccumulatorFactory {
        return FilePartAccumulatorFactory(pathFactory, outputQueue, loadStrategy)
    }

    @Named("oneShotObjectLoaderStep")
    @Singleton
    fun <O : OutputStream, K : WithStream, T : RemoteObject<*>> oneShotObjectLoaderStep(
        objectLoaderOneShotUploader: ObjectLoaderOneShotUploader<O, T>,
        @Named("numInputPartitions") numInputPartitions: Int,
        @Named("objectLoaderCompletedUploadQueue")
        completedUploadQueue:
            PartitionedQueue<PipelineEvent<K, ObjectLoaderUploadCompleter.UploadResult<T>>>? =
            null,
        completedUploadPartitioner:
            ObjectLoaderCompletedUploadPartitioner<StreamKey, DestinationRecordRaw, K, T>? =
            null,
        taskFactory: LoadPipelineStepTaskFactory,
    ) =
        ObjectLoaderOneShotUploaderStep(
            objectLoaderOneShotUploader,
            completedUploadQueue,
            completedUploadPartitioner,
            taskFactory,
            numInputPartitions,
        )

    @Named("sharedUploadPermits")
    @Singleton
    fun sharedUploadPermits(@Named("dataChannelSocketPaths") dataChannelSocketPaths: List<String>) =
        Semaphore(dataChannelSocketPaths.size)
}
