/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.file.object_storage.PartBookkeeper
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.WithBatchState
import io.airbyte.cdk.load.pipeline.BatchAccumulator
import io.airbyte.cdk.load.pipeline.BatchAccumulatorResult
import io.airbyte.cdk.load.pipeline.FinalOutput
import io.airbyte.cdk.load.pipeline.NoOutput
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Requires(bean = ObjectLoader::class)
class ObjectLoaderUploadCompleter :
    BatchAccumulator<
        ObjectLoaderUploadCompleter.State,
        ObjectKey,
        ObjectLoaderPartLoader.PartResult,
        ObjectLoaderUploadCompleter.UploadResult
    > {
    private val log = KotlinLogging.logger {}

    data class State(val objectKey: String, val partBookkeeper: PartBookkeeper) : AutoCloseable {
        override fun close() {
            // Do Nothing
        }
    }

    data class UploadResult(override val state: Batch.State) : WithBatchState

    override suspend fun start(key: ObjectKey, part: Int): State {
        val bookkeeper = PartBookkeeper()
        return State(key.objectKey, bookkeeper)
    }

    override suspend fun accept(
        input: ObjectLoaderPartLoader.PartResult,
        state: State
    ): BatchAccumulatorResult<State, UploadResult> {
        return when (input) {
            is ObjectLoaderPartLoader.LoadedPart -> {
                val part =
                    Part(
                        key = state.objectKey,
                        fileNumber = 0L, // ignored
                        bytes = ByteArray(0), // only null/not-null is significant
                        isFinal = input.isFinal,
                        partIndex = input.partIndex
                    )
                state.partBookkeeper.add(part)
                if (state.partBookkeeper.isComplete) {
                    log.info {
                        "Loaded part ${input.partIndex} (isFinal=${input.isFinal}) completes ${state.objectKey}, finishing (state $state)"
                    }
                    input.upload.await().complete()
                    FinalOutput(UploadResult(Batch.State.COMPLETE))
                } else {
                    log.info {
                        "After loaded part ${input.partIndex} (isFinal=${input.isFinal}), ${state.objectKey} still incomplete, not finishing (state $state)"
                    }
                    NoOutput(state)
                }
            }
            is ObjectLoaderPartLoader.NoPart -> {
                NoOutput(state)
            }
        }
    }

    override suspend fun finish(state: State): FinalOutput<State, UploadResult> {
        /**
         * Should never be called until end-of-stream. There should ever be one completer worker,
         * and the enclosing step should be configured not to flush.
         */
        return FinalOutput(UploadResult(Batch.State.COMPLETE))
    }
}
