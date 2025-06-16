/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.dlq

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfig
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfigProvider
import io.airbyte.cdk.load.command.dlq.S3ObjectStorageConfig
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.ResourceReservingPartitionedQueue
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.LoadPipeline
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.pipeline.PipelineFlushStrategy
import io.airbyte.cdk.load.pipeline.dlq.DlqLoaderPipelineStep
import io.airbyte.cdk.load.pipline.object_storage.ObjectKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartFormatter
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartFormatterStep
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartLoaderStep
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadCompleterStep
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.OutputStream

/** Factory to build a DeadLetterQueueLoadPipeline. */
class DlqPipelineFactory(
    private val dlqInputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
    private val dlqPipelineSteps: List<LoadPipelineStep>,
    private val pipelineStepTaskFactory: LoadPipelineStepTaskFactory,
    private val objectLoader: ObjectLoader,
) {
    fun <S : AutoCloseable> createPipeline(dlqLoader: DlqLoader<S>): LoadPipeline =
        object :
            LoadPipeline(
                listOf(
                    DlqLoaderPipelineStep(
                        numWorkers = objectLoader.numPartWorkers,
                        outputQueue = dlqInputQueue,
                        taskFactory = pipelineStepTaskFactory,
                        dlqLoader = dlqLoader,
                        deadLetterQueueEnabled = dlqPipelineSteps.isNotEmpty(),
                    ),
                    *dlqPipelineSteps.toTypedArray(),
                )
            ) {}
}

/** A Micronaut Factory to help initialize the component required for a DeadLetterQueuePipeline */
@Factory
class DlqPipelineFactoryFactory {
    /** The end goal of this file. */
    @Singleton
    fun dlqPipelineFactory(
        @Named("dlqInputQueue")
        dlqInputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
        @Named("dlqPipelineSteps") dlqPipelineSteps: List<LoadPipelineStep>,
        pipelineStepTaskFactory: LoadPipelineStepTaskFactory,
        objectLoader: ObjectLoader,
    ) = DlqPipelineFactory(dlqInputQueue, dlqPipelineSteps, pipelineStepTaskFactory, objectLoader)

    /**
     * This queue is the input queue of a "traditional" ObjectStorageLoadPipeline
     *
     * Effectively, a DLQ LoadPipeline is a custom pipeline step that may pass down records meant
     * for the DLQ. The DLQ LoadPipeline upload to ObjectStorage leverages the usual object storage
     * pipeline steps with the exception of the input.
     *
     * This Queue is the shim between the DlqLoaderStep and the ObjectStorage input.
     */
    @Named("dlqInputQueue")
    @Singleton
    fun dlqInputQueue(
        @Named("globalMemoryManager") globalMemoryManager: ReservationManager
    ): PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>> =
        ResourceReservingPartitionedQueue(
            reservationManager = globalMemoryManager,
            ratioOfTotalMemoryToReserve = 0.2,
            numConsumers = 1,
            numProducers = 1,
            expectedResourceUsagePerUnit = 100000,
        )

    /**
     * This is the start of the "traditional" object storage pipeline. However, in order for the
     * updated pipeline to work, this recreates the ObjectLoaderPartFormatterStep but with the
     * dlqInputQueue as in input instead of the actual input of the destination which is used by the
     * DlqLoader in this case.
     */
    @Named("dlqRecordFormatterStep")
    @Singleton
    fun <T : OutputStream> partFormatterStep(
        @Named("numInputPartitions") numInputPartitions: Int,
        partFormatter: ObjectLoaderPartFormatter<T>,
        @Named("dlqInputQueue")
        inputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
        @Named("objectLoaderPartQueue")
        outputQueue:
            PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>,
        taskFactory: LoadPipelineStepTaskFactory,
        flushStrategy: PipelineFlushStrategy,
    ): ObjectLoaderPartFormatterStep =
        ObjectLoaderPartFormatterStep(
            numWorkers = numInputPartitions,
            partFormatter = partFormatter,
            inputFlows = inputQueue.asOrderedFlows(),
            outputQueue = outputQueue,
            taskFactory = taskFactory,
            stepId = "record-part-formatter-step",
            flushStrategy = flushStrategy,
        )

    /**
     * References the traditional ObjectStorage pipeline steps.
     *
     * We rely on an ObjectStorageConfig to exist and not be `DisabledObjectStorageConfig` to decide
     * whether we should return the ObjectLoader pipeline steps as DLQ Steps.
     */
    @Singleton
    @Requires(bean = ObjectStorageConfig::class, beanProperty = "type", notEquals = "None")
    @Named("dlqPipelineSteps")
    fun <K : WithStream, T : RemoteObject<*>> dlqPipelineSteps(
        @Named("dlqRecordFormatterStep") formatterStep: ObjectLoaderPartFormatterStep,
        @Named("recordPartLoaderStep") loaderStep: ObjectLoaderPartLoaderStep<T>,
        @Named("recordUploadCompleterStep") completerStep: ObjectLoaderUploadCompleterStep<K, T>,
    ): List<LoadPipelineStep> =
        listOf(
            formatterStep,
            loaderStep,
            completerStep,
        )

    @Singleton
    @Requires(bean = ObjectStorageConfig::class, beanProperty = "type", value = "None")
    @Named("dlqPipelineSteps")
    fun dlqPipelineSteps(): List<LoadPipelineStep> {
        return emptyList()
    }

    /** Add a Singleton to extract the `ObjectStorageConfig` from the `DestinationConfiguration`. */
    @Singleton
    fun objectStorageConfig(destinationConfig: DestinationConfiguration): ObjectStorageConfig =
        (destinationConfig as? ObjectStorageConfigProvider)?.objectStorageConfig
            ?: throw IllegalArgumentException(
                "Unable to extract an ObjectStorageConfig from the DestinationConfiguration. Does it implement ObjectStorageConfigProvider"
            )

    /** Singleton to extract the different object storage related config providers for S3 */
    @Singleton
    fun s3ObjectStorageConfig(
        destinationConfig: DestinationConfiguration
    ): S3ObjectStorageConfig<*> =
        (destinationConfig as? ObjectStorageConfigProvider)?.objectStorageConfig
            as? S3ObjectStorageConfig<*>
            ?: throw IllegalArgumentException(
                "Unable to extract an S3ObjectStorageConfig from the DestinationConfiguration. Does it implement ObjectStorageConfigProvider"
            )
}
