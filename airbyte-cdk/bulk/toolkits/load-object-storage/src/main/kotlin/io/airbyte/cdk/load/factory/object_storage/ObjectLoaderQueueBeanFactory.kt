/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.factory.object_storage

import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.ResourceReservingPartitionedQueue
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.StrictPartitionedQueue
import io.airbyte.cdk.load.pipline.object_storage.ObjectKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartFormatter
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartLoader
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadCompleter
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.condition.Condition
import io.micronaut.context.condition.ConditionContext
import io.micronaut.inject.qualifiers.Qualifiers
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlin.math.max
import kotlinx.coroutines.channels.Channel

@Factory
class ObjectLoaderQueueBeanFactory(
    val loader: ObjectLoader,
) {
    val log = KotlinLogging.logger {}

    companion object {
        const val OBJECT_LOADER_MAX_ENQUEUED_COMPLETIONS = 10_000
    }

    /**
     * If we naively accept the part size and concurrency settings, we might end up with a connector
     * that passes CI but can't run in a resource-limited production environment, because there
     * isn't enough memory even for the workers to hold parts in flight.
     *
     * Therefore, we will always clamp the part size to fit the available memory. This might still
     * lead to runtime failures (ie, if it drops below a storage-client-specified minimum), but it
     * is much less likely.
     */
    @Singleton
    @Named("objectLoaderClampedPartSizeBytes")
    @Requires(bean = ObjectLoader::class)
    fun objectLoaderClampedPartSizeBytes(
        @Named("objectLoaderPartQueue") queue: ResourceReservingPartitionedQueue<*>,
        @Named("dataChannelMedium") dataChannelMedium: DataChannelMedium,
    ): Long {
        if (dataChannelMedium == DataChannelMedium.SOCKET) {
            return max(queue.clampedMessageSize, loader.partSizeBytes)
        }
        return queue.clampedMessageSize
    }

    /**
     * Queue between step 1 (format parts) and step 2 (load them): it will hold the actual part
     * bytes and needs to be sized based on the available reserved memory.
     */
    @Singleton
    @Named("objectLoaderPartQueue")
    @Requires(bean = ObjectLoader::class)
    fun recordObjectLoaderPartQueue(
        @Named("globalMemoryManager") globalMemoryManager: ReservationManager
    ): ResourceReservingPartitionedQueue<
        PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>> {
        return ResourceReservingPartitionedQueue(
            globalMemoryManager,
            loader.maxMemoryRatioReservedForParts,
            loader.numUploadWorkers,
            loader.numPartWorkers,
            loader.partSizeBytes
        )
    }

    /**
     * Queue between part 2 (upload parts) and part 3 (finish the upload). It will hold the fact of
     * upload completion only, so in theory it can be [Channel.UNLIMITED], but to be safe we'll
     * limit it to 10,000 queued completions.
     */
    @Singleton
    @Named("objectLoaderLoadedPartQueue")
    @Requires(bean = ObjectLoader::class)
    fun <T : RemoteObject<*>> objectLoaderLoadedPartQueue():
        PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult<T>>> {
        return StrictPartitionedQueue(
            (0 until loader.numUploadCompleters)
                .map {
                    ChannelMessageQueue(
                        Channel<PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult<T>>>(
                            OBJECT_LOADER_MAX_ENQUEUED_COMPLETIONS / loader.numUploadWorkers
                        )
                    )
                }
                .toTypedArray()
        )
    }

    /** A queue for records uploading. */
    @Singleton
    @Named("recordQueue")
    fun recordQueue(
        @Named("numInputPartitions") numInputPartitions: Int,
    ): PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>> {
        return StrictPartitionedQueue(
            Array(numInputPartitions) { ChannelMessageQueue(Channel(Channel.UNLIMITED)) }
        )
    }

    /** A queue for records with file references for file uploading. */
    @Singleton
    @Named("fileQueue")
    @Requires(condition = IsFileTransferCondition::class)
    fun fileQueue(
        @Named("numInputPartitions") numInputPartitions: Int,
    ): PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>> {
        return StrictPartitionedQueue(
            Array(numInputPartitions) { ChannelMessageQueue(Channel(Channel.UNLIMITED)) }
        )
    }

    /**
     * Queue between file part chunking and loading of file parts. It will hold the actual part
     * bytes and needs to be sized based on the available reserved memory.
     */
    @Singleton
    @Named("filePartQueue")
    @Requires(condition = IsFileTransferCondition::class)
    fun fileObjectLoaderPartQueue(
        @Named("globalMemoryManager") globalMemoryManager: ReservationManager
    ): ResourceReservingPartitionedQueue<
        PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>> {
        return ResourceReservingPartitionedQueue(
            globalMemoryManager,
            loader.maxMemoryRatioReservedForParts,
            loader.numUploadWorkers,
            loader.numPartWorkers,
            loader.partSizeBytes
        )
    }

    /**
     * Queue between upload file parts and the upload completer. It will hold the fact of upload
     * completion only, so in theory it can be [Channel.UNLIMITED], but to be safe we'll limit it to
     * 10,000 queued completions.
     */
    @Singleton
    @Named("fileLoadedPartQueue")
    @Requires(condition = IsFileTransferCondition::class)
    fun <T : RemoteObject<*>> fileLoadedPartQueue():
        PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult<T>>> {
        return StrictPartitionedQueue(
            (0 until loader.numUploadCompleters)
                .map {
                    ChannelMessageQueue(
                        Channel<PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult<T>>>(
                            OBJECT_LOADER_MAX_ENQUEUED_COMPLETIONS / loader.numUploadWorkers
                        )
                    )
                }
                .toTypedArray()
        )
    }

    /** Completed file uploads. */
    @Singleton
    @Named("fileCompletedQueue")
    @Requires(condition = IsFileTransferCondition::class)
    fun <T> completedUploadQueue() =
        StrictPartitionedQueue(
            (0 until loader.numUploadCompleters)
                .map {
                    ChannelMessageQueue<
                        PipelineEvent<StreamKey, ObjectLoaderUploadCompleter.UploadResult<T>>>(
                        Channel(OBJECT_LOADER_MAX_ENQUEUED_COMPLETIONS)
                    )
                }
                .toTypedArray()
        )
}

/**
 * Custom Micronaut [Condition] that is used to conditionally create file transfer related beans.
 */
class IsFileTransferCondition : Condition {
    override fun matches(context: ConditionContext<*>): Boolean {
        return context.beanContext.getBean(Boolean::class.java, Qualifiers.byName("isFileTransfer"))
    }
}
