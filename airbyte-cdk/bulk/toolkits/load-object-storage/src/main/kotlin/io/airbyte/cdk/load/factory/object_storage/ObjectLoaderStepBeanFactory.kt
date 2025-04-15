package io.airbyte.cdk.load.factory.object_storage

import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartLoaderStep
import io.micronaut.context.annotation.Factory
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderCompletedUploadPartitioner
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartFormatter
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartLoader
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadCompleter
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadCompleterStep
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import jakarta.inject.Named
import jakarta.inject.Singleton

@Factory
class ObjectLoaderStepBeanFactory {
    @Named("recordPartLoaderStep")
    @Singleton
    fun <T : RemoteObject<*>> recordPartLoader(
        loader: ObjectLoader,
        partLoader: ObjectLoaderPartLoader<T>,
        @Named("objectLoaderPartQueue") inputQueue: PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>,
        @Named("objectLoaderLoadedPartQueue") outputQueue: PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult<T>>>,
        taskFactory: LoadPipelineStepTaskFactory,
        ) = ObjectLoaderPartLoaderStep(
            loader,
            partLoader,
            inputQueue,
            outputQueue,
            taskFactory,
        )

    @Named("filePartLoaderStep")
    @Singleton
    fun <T : RemoteObject<*>> filePartLoader(
        loader: ObjectLoader,
        partLoader: ObjectLoaderPartLoader<T>,
        @Named("filePartQueue") inputQueue: PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>,
        @Named("fileLoadedPartQueue") outputQueue: PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult<T>>>,
        taskFactory: LoadPipelineStepTaskFactory,
        ) = ObjectLoaderPartLoaderStep(
            loader,
            partLoader,
            inputQueue,
            outputQueue,
            taskFactory,
        )

    @Named("recordUploadCompleterStep")
    @Singleton
    fun <K : WithStream, T : RemoteObject<*>> recordUploadCompleter(
        objectLoader: ObjectLoader,
        uploadCompleter: ObjectLoaderUploadCompleter<T>,
        @Named("objectLoaderLoadedPartQueue") inputQueue: PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult<T>>>,
        @Named("objectLoaderCompletedUploadQueue") completedUploadQueue: PartitionedQueue<PipelineEvent<K, ObjectLoaderUploadCompleter.UploadResult<T>>>? = null,
        completedUploadPartitioner: ObjectLoaderCompletedUploadPartitioner<K, T>? = null,
        taskFactory: LoadPipelineStepTaskFactory,
    ) = ObjectLoaderUploadCompleterStep(
        objectLoader,
        uploadCompleter,
        inputQueue,
        completedUploadQueue,
        completedUploadPartitioner,
        taskFactory,
    )

    @Named("fileUploadCompleterStep")
    @Singleton
    fun <K : WithStream, T : RemoteObject<*>> fileUploadCompleter(
        objectLoader: ObjectLoader,
        uploadCompleter: ObjectLoaderUploadCompleter<T>,
        @Named("fileLoadedPartQueue") inputQueue: PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult<T>>>,
        @Named("fileCompletedQueue") completedUploadQueue: PartitionedQueue<PipelineEvent<K, ObjectLoaderUploadCompleter.UploadResult<T>>>? = null,
        completedUploadPartitioner: ObjectLoaderCompletedUploadPartitioner<K, T>? = null,
        taskFactory: LoadPipelineStepTaskFactory,
    ) = ObjectLoaderUploadCompleterStep(
        objectLoader,
        uploadCompleter,
        inputQueue,
        completedUploadQueue,
        completedUploadPartitioner,
        taskFactory,
    )
}
