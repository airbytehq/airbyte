/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.file.object_storage.PartBookkeeper
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.WithBatchState
import io.airbyte.cdk.load.pipeline.BatchAccumulator
import io.airbyte.cdk.load.state.object_storage.ObjectStorageDestinationState
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

/**
 * In order to allow streaming uploads on the same key to be parallelized, upload state needs to be
 * shared across workers.
 */
@Singleton
@Requires(bean = ObjectLoader::class)
class UploadsInProgress {
    val byKey: ConcurrentHashMap<String, ObjectLoaderPartToObjectAccumulator.State> =
        ConcurrentHashMap()
}

@Singleton
@Requires(bean = ObjectLoader::class)
class ObjectLoaderPartToObjectAccumulator(
    private val client: ObjectStorageClient<*>,
    private val catalog: DestinationCatalog,
    private val uploads: UploadsInProgress,
) :
    BatchAccumulator<
        ObjectLoaderPartToObjectAccumulator.State,
        ObjectKey,
        Part,
        ObjectLoaderPartToObjectAccumulator.ObjectResult
    > {

    data class State(val streamingUpload: StreamingUpload<*>, val bookkeeper: PartBookkeeper) :
        AutoCloseable {
        override fun close() {
            // Do Nothing
        }
    }

    data class ObjectResult(override val state: Batch.State) : WithBatchState

    override suspend fun start(key: ObjectKey, part: Int): State {
        val stream = catalog.getStream(key.stream)
        return uploads.byKey.getOrPut(key.objectKey) {
            State(
                client.startStreamingUpload(
                    key.objectKey,
                    metadata = ObjectStorageDestinationState.metadataFor(stream)
                ),
                PartBookkeeper()
            )
        }
    }

    override suspend fun accept(input: Part, state: State): Pair<State, ObjectResult?> {
        input.bytes?.let { state.streamingUpload.uploadPart(it, input.partIndex) }
        if (input.bytes == null) {
            throw IllegalStateException("Empty non-final part received: this should not happen")
        }
        state.bookkeeper.add(input)
        if (state.bookkeeper.isComplete) {
            return Pair(state, finish(state))
        }
        return Pair(state, null)
    }

    override suspend fun finish(state: State): ObjectResult {
        if (state.bookkeeper.isComplete) {
            state.streamingUpload.complete()
        } // else assume another part is finishing this
        return ObjectResult(Batch.State.COMPLETE)
    }
}
