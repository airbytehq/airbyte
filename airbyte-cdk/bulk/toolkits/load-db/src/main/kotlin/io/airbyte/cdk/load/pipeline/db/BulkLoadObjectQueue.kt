/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.db

import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipline.object_storage.LoadedObject
import io.airbyte.cdk.load.write.db.BulkLoaderFactory
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlinx.coroutines.channels.Channel

@Factory
@Requires(bean = BulkLoaderFactory::class)
class BulkLoadObjectQueueFactory<K : WithStream, T : RemoteObject<*>>(
    val bulkLoad: BulkLoaderFactory<K, T>
) {
    @Singleton
    @Named("objectLoaderOutputQueue")
    @Secondary
    fun bulkLoadObjectQueue(): PartitionedQueue<PipelineEvent<K, LoadedObject<T>>> =
        PartitionedQueue(
            (0 until bulkLoad.maxNumConcurrentLoads)
                .map { ChannelMessageQueue<PipelineEvent<K, LoadedObject<T>>>(Channel(1)) }
                .toTypedArray()
        )
}
