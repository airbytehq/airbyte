/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.airbyte.cdk.load.pipeline.BatchAccumulator
import io.airbyte.cdk.load.pipeline.BatchAccumulatorResult
import io.airbyte.cdk.load.pipeline.FinalOutput
import io.airbyte.cdk.load.pipeline.IntermediateOutput
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
    val byKey: ConcurrentHashMap<String, ObjectLoaderPartLoader.State> = ConcurrentHashMap()
}

@Singleton
@Requires(bean = ObjectLoader::class)
class ObjectLoaderPartLoader(
    private val client: ObjectStorageClient<*>,
    private val catalog: DestinationCatalog,
    private val uploads: UploadsInProgress,
) :
    BatchAccumulator<
        ObjectLoaderPartLoader.State,
        ObjectKey,
        ObjectLoaderPartFormatter.FormattedPart,
        ObjectLoaderPartLoader.PartResult
    > {
    private val log = KotlinLogging.logger {}

    data class State(
        val objectKey: String,
        val streamingUpload: Deferred<StreamingUpload<*>>,
    ) : AutoCloseable {
        override fun close() {
            // Do Nothing
        }
    }

    sealed interface PartResult {
        val objectKey: String
    }
    data class LoadedPart(
        val upload: Deferred<StreamingUpload<*>>,
        override val objectKey: String,
        val partIndex: Int,
        val isFinal: Boolean
    ) : PartResult
    data class NoPart(override val objectKey: String) : PartResult

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
            )
        }
    }

    override suspend fun accept(
        input: ObjectLoaderPartFormatter.FormattedPart,
        state: State
    ): BatchAccumulatorResult<State, PartResult> {
        log.info { "Uploading part $input" }
        input.part.bytes?.let { state.streamingUpload.await().uploadPart(it, input.part.partIndex) }
            ?: throw IllegalStateException("Empty non-final part received: this should not happen")
        val output =
            LoadedPart(
                state.streamingUpload,
                input.part.key,
                input.part.partIndex,
                input.part.isFinal
            )
        return IntermediateOutput(state, output)
    }

    override suspend fun finish(state: State): FinalOutput<State, PartResult> {
        return FinalOutput(NoPart(state.objectKey))
    }
}
