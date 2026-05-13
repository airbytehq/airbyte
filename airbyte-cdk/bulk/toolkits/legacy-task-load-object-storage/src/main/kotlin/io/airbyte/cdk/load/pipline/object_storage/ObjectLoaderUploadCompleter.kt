/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.file.object_storage.PartBookkeeper
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.BatchState
import io.airbyte.cdk.load.message.WithBatchState
import io.airbyte.cdk.load.pipeline.BatchAccumulator
import io.airbyte.cdk.load.pipeline.BatchAccumulatorResult
import io.airbyte.cdk.load.pipeline.FinalOutput
import io.airbyte.cdk.load.pipeline.NoOutput
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

// TODO: Add unit tests
@Singleton
@Requires(bean = ObjectLoader::class)
class ObjectLoaderUploadCompleter<T : RemoteObject<*>>(val objectLoader: ObjectLoader) :
    BatchAccumulator<
        ObjectLoaderUploadCompleter.State,
        ObjectKey,
        ObjectLoaderPartLoader.PartResult<T>,
        ObjectLoaderUploadCompleter.UploadResult<T>
    > {
    private val log = KotlinLogging.logger {}

    data class State(val objectKey: String, val partBookkeeper: PartBookkeeper) : AutoCloseable {
        override fun close() {
            // Do Nothing
        }
    }

    data class UploadResult<T>(override val state: BatchState, val remoteObject: T?) :
        WithBatchState

    override suspend fun start(key: ObjectKey, part: Int): State {
        val bookkeeper = PartBookkeeper()
        return State(key.objectKey, bookkeeper)
    }

    override suspend fun accept(
        input: ObjectLoaderPartLoader.PartResult<T>,
        state: State
    ): BatchAccumulatorResult<State, UploadResult<T>> {
        return when (input) {
            is ObjectLoaderPartLoader.LoadedPart -> {
                // by setting bytes to null, we tell the bookkeeper
                // not to track this empty part
                val bytes =
                    if (input.empty) {
                        null
                    } else {
                        ByteArray(0)
                    }

                val part =
                    Part(
                        key = state.objectKey,
                        fileNumber = 0L, // ignored
                        bytes = bytes,
                        isFinal = input.isFinal,
                        partIndex = input.partIndex
                    )
                state.partBookkeeper.add(part)
                if (state.partBookkeeper.isComplete) {
                    if (state.partBookkeeper.isEmpty) {
                        // All parts were empty (no data was ever uploaded).
                        // Skip completing the upload to avoid creating a 0-byte
                        // object which would lack valid file headers/footers
                        // (e.g. Parquet magic bytes), causing schema mismatch
                        // errors in downstream readers.
                        //
                        // ObjectLoaderPartLoader.start() has already initiated the
                        // streaming upload (e.g. on S3 this is a createMultipartUpload),
                        // so we must abort() it explicitly to avoid leaking a dangling
                        // multipart upload server-side. abort() is best-effort and
                        // never throws.
                        log.info {
                            "Loaded part ${input.partIndex} (isFinal=${input.isFinal}) completes ${state.objectKey} but all parts were empty, aborting upload (state $state)"
                        }
                        input.upload.await().abort()
                        FinalOutput(UploadResult(objectLoader.stateAfterUpload, null))
                    } else {
                        log.info {
                            "Loaded part ${input.partIndex} (isFinal=${input.isFinal}) completes ${state.objectKey}, finishing (state $state)"
                        }
                        val obj = input.upload.await().complete()
                        FinalOutput(UploadResult(objectLoader.stateAfterUpload, obj))
                    }
                } else {
                    log.debug {
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

    override suspend fun finish(state: State): FinalOutput<State, UploadResult<T>> {
        if (!state.partBookkeeper.isEmpty) {
            throw IllegalStateException(
                "Upload completers had unfinished work at end-of-stream. This should not happen."
            )
        }

        // Everything we received before end-of-stream was a no-op. Return a dummy output.
        return FinalOutput(UploadResult(objectLoader.stateAfterUpload, null))
    }
}
