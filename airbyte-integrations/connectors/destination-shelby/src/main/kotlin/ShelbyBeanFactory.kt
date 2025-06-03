package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.object_storage.JsonFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.file.object_storage.BufferedFormattingWriterFactory
import io.airbyte.cdk.load.file.object_storage.DefaultObjectStorageFormattingWriterFactory
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.ResourceReservingPartitionedQueue
import io.airbyte.cdk.load.message.StrictPartitionedQueue
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.LoadPipeline
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.pipline.object_storage.ObjectKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartFormatter
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartFormatterStep
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartLoaderStep
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadCompleterStep
import io.airbyte.cdk.load.state.DestinationStateManager
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.object_storage.ObjectStorageDestinationState
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory
import io.airbyte.cdk.load.write.LoadStrategy
import io.airbyte.cdk.load.write.WriteOperation
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.OutputStream
import kotlin.math.tan

@Factory
class ShelbyBeanFactory {
    @Singleton
    fun check() = ShelbyChecker()

    @Singleton
    fun discover() = ShelbyDiscoverer()

    @Singleton
    fun getConfig(config: DestinationConfiguration) = config as ShelbyConfiguration

    @Singleton
    fun objectLoader(): ObjectLoader = object : ObjectLoader {
        override val numPartWorkers = 1
    }

    @Named("deadLetterQueueQueue")
    @Singleton
    fun deadLetterQueueQueue(
        @Named("globalMemoryManager") globalMemoryManager: ReservationManager
    ): PartitionedQueue<PipelineEvent<ObjectKey, DestinationRecordRaw>> =
        ResourceReservingPartitionedQueue(
            globalMemoryManager,
            0.2,
            1,
            1,
            100000,
        )

    @Singleton
    fun objectStorageFormattingWriterFactory(): DefaultObjectStorageFormattingWriterFactory =
        DefaultObjectStorageFormattingWriterFactory(
            object : ObjectStorageFormatConfigurationProvider {
                override val objectStorageFormatConfiguration = JsonFormatConfiguration()
            }
        )

//    @Primary
//    @Singleton
//    fun <T : OutputStream> test(partFormatter: ObjectLoaderPartFormatter<T>): DestinationCatalog =
//        DestinationCatalog()

    @Primary
    @Singleton
    fun <K : WithStream, T : RemoteObject<*>> loadPipeline(
        @Named("deadLetterQueueQueue") deadLetterQueueQueue: PartitionedQueue<PipelineEvent<ObjectKey, DestinationRecordRaw>>,
        @Named("recordPartFormatterStep") formatterStep: ObjectLoaderPartFormatterStep,
        @Named("recordPartLoaderStep") loaderStep: ObjectLoaderPartLoaderStep<T>,
        @Named("recordUploadCompleterStep") completerStep: ObjectLoaderUploadCompleterStep<K, T>,
        taskFactory: LoadPipelineStepTaskFactory,
    ): LoadPipeline =
        object : LoadPipeline(listOf(
            HttpPipelineStep(
                numWorkers = 1,
                outputQueue = deadLetterQueueQueue,
                taskFactory = taskFactory,
            ),
            formatterStep,
            loaderStep,
            completerStep,
        )) {}
}
