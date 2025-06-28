/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.db

import io.airbyte.cdk.load.factory.object_storage.ObjectLoaderQueueBeanFactory
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.StrictPartitionedQueue
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadCompleter
import io.airbyte.cdk.load.write.db.BulkLoaderFactory
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlinx.coroutines.channels.Channel

@Factory
class BulkLoadCompletedUploadQueue<K : WithStream, T : RemoteObject<*>> {
    @Singleton
    @Secondary
    @Requires(bean = BulkLoaderFactory::class)
    @Named("objectLoaderCompletedUploadQueue")
    fun bulkLoadCompletedUploadQueue(
        bulkLoader: BulkLoaderFactory<K, T>
    ): PartitionedQueue<PipelineEvent<K, ObjectLoaderUploadCompleter.UploadResult<T>>> =
        StrictPartitionedQueue(
            (0 until bulkLoader.maxNumConcurrentLoads)
                .map {
                    ChannelMessageQueue<
                        PipelineEvent<K, ObjectLoaderUploadCompleter.UploadResult<T>>>(
                        Channel(ObjectLoaderQueueBeanFactory.OBJECT_LOADER_MAX_ENQUEUED_COMPLETIONS)
                    )
                }
                .toTypedArray()
        )
}
