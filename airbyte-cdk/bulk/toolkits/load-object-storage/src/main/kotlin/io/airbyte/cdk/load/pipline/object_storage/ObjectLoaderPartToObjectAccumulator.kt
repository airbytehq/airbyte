/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.file.object_storage.PartBookkeeper
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.WithBatchState
import io.airbyte.cdk.load.pipeline.BatchAccumulator
import io.airbyte.cdk.load.state.object_storage.ObjectStorageDestinationState
import io.airbyte.cdk.load.util.setOnce
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicBoolean

/**
 * In order to allow streaming uploads on the same key to be parallelized, upload state needs to be
 * shared across workers.
 */
@Singleton
@Requires(bean = ObjectLoader::class)
class UploadsInProgress<T : RemoteObject<*>> {
    val byKey: ConcurrentHashMap<String, ObjectLoaderPartToObjectAccumulator<T>.State> =
        ConcurrentHashMap()
}

data class LoadedObject<T : RemoteObject<*>>(
    val remoteObject: T,
    override val state: Batch.State = Batch.State.COMPLETE,
    val alreadyComplete: Boolean
) : WithBatchState

@Singleton
@Requires(bean = ObjectLoader::class)
class ObjectLoaderPartToObjectAccumulator<T : RemoteObject<*>>(
    private val client: ObjectStorageClient<T>,
    private val catalog: DestinationCatalog,
    private val uploads: UploadsInProgress<T>,
    private val strategy: ObjectLoader,
) :
    BatchAccumulator<
        ObjectLoaderPartToObjectAccumulator<T>.State, ObjectKey, Part, LoadedObject<T>> {

    inner class State(
        val streamingUpload: StreamingUpload<T>,
        val bookkeeper: PartBookkeeper,
        val isComplete: AtomicBoolean = AtomicBoolean(false),
    ) : AutoCloseable {
        override fun close() {
            // Do Nothing
        }
    }

    data class ObjectResult(override val state: Batch.State, val objectKey: String) :
        WithBatchState

    override suspend fun start(key: ObjectKey, part: Int): State {
        val stream = catalog.getStream(key.stream)
        return uploads.byKey.getOrPut(key.objectKey) {
            State(
                client.startStreamingUpload(
                    key.objectKey,
                    metadata = ObjectStorageDestinationState.metadataFor(stream)
                ),
                PartBookkeeper(),
            )
        }
    }

    override suspend fun accept(input: Part, state: State): Pair<State?, LoadedObject<T>?> {
        input.bytes?.let { state.streamingUpload.uploadPart(it, input.partIndex) }
        if (input.bytes == null) {
            throw IllegalStateException("Empty non-final part received: this should not happen")
        }
        state.bookkeeper.add(input)
        if (state.bookkeeper.isComplete) {
            return Pair(null, finish(state))
        }
        return Pair(state, null)
    }

    override suspend fun finish(state: State): LoadedObject<T> {
        val obj = state.streamingUpload.complete()
        return LoadedObject(
            obj,
            strategy.batchStateOnUpload,
            alreadyComplete = !state.isComplete.setOnce()
        )
    }
}
