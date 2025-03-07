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
import io.airbyte.cdk.load.pipeline.BatchAccumulatorResult
import io.airbyte.cdk.load.pipeline.FinalOutput
import io.airbyte.cdk.load.pipeline.NoOutput
import io.airbyte.cdk.load.state.object_storage.ObjectStorageDestinationState
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Deferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async

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
    private val log = KotlinLogging.logger {}

    data class State(
        val objectKey: String,
        val streamingUpload: Deferred<StreamingUpload<*>>,
        val bookkeeper: PartBookkeeper
    ) : AutoCloseable {
        override fun close() {
            // Do Nothing
        }
    }

    data class ObjectResult(override val state: Batch.State) : WithBatchState

    override suspend fun start(key: ObjectKey, part: Int): State {
        val stream = catalog.getStream(key.stream)
        return uploads.byKey.computeIfAbsent(key.objectKey) {
            State(
                key.objectKey,
                CoroutineScope(Dispatchers.IO).async {
                    client.startStreamingUpload(
                        key.objectKey,
                        metadata = ObjectStorageDestinationState.metadataFor(stream)
                    )
                },
                PartBookkeeper()
            )
        }
    }

    override suspend fun accept(
        input: Part,
        state: State
    ): BatchAccumulatorResult<State, ObjectResult> {
        log.info { "Uploading part $input" }
        input.bytes?.let { state.streamingUpload.await().uploadPart(it, input.partIndex) }
        if (input.bytes == null) {
            throw IllegalStateException("Empty non-final part received: this should not happen")
        }
        state.bookkeeper.add(input)
        return if (state.bookkeeper.isComplete) {
            finish(state)
        } else {
            NoOutput(state)
        }
    }

    override suspend fun finish(state: State): FinalOutput<State, ObjectResult> {
        // Guard against finishing early because one stream closed while another was still working
        if (state.bookkeeper.isComplete) {
            state.streamingUpload.await().complete()
        }

        return FinalOutput(ObjectResult(Batch.State.COMPLETE))
    }
}
