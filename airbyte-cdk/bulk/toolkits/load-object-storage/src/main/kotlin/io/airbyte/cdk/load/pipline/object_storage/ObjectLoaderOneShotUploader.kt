/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.file.object_storage.ByteArrayPool
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.BatchAccumulator
import io.airbyte.cdk.load.pipeline.BatchAccumulatorResult
import io.airbyte.cdk.load.pipeline.FinalOutput
import io.airbyte.cdk.load.pipeline.IntermediateOutput
import io.airbyte.cdk.load.pipeline.NoOutput
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.OutputStream
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Deferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.supervisorScope

/**
 * Wraps the PartFormatter, PartLoader, and UploadCompleter in a single BatchAccumulator.
 * - feeds incoming records to the formatter
 * - as the formatter produces parts, feeds them to the part loader (in async futures)
 * - when the final part is generated, or finish is called, awaits all part uploads, feeding the
 * load results to the completer until the completer completes
 * - returns the completer result (which might be sent further downstream if bulk load is enabled)
 *
 * Ie, Accomplishes "Simplify the Object Storage Path" here:
 * https://docs.google.com/document/d/1pLWrtqGqynfnKs8FzMq64g4-04Fot6LvVU6CVUGHBQI/edit?tab=t.0
 */
@Singleton
@Requires(bean = ObjectLoader::class)
class ObjectLoaderOneShotUploader<O : OutputStream, T : RemoteObject<*>>(
    private val partFormatter: ObjectLoaderPartFormatter<O>,
    private val partLoader: ObjectLoaderPartLoader<T>,
    private val uploadCompleter: ObjectLoaderUploadCompleter<T>,
    @Named("uploadParallelismForSocket") uploadParallelism: Int,
) :
    BatchAccumulator<
        ObjectLoaderOneShotUploader.State<O, T>,
        StreamKey,
        DestinationRecordRaw,
        ObjectLoaderUploadCompleter.UploadResult<T>
    > {

    private val log = KotlinLogging.logger {}
    @OptIn(ExperimentalCoroutinesApi::class)
    private val uploadDispatcher = Dispatchers.IO.limitedParallelism(uploadParallelism)

    /**
     * One structured scope that owns *all* part-upload coroutines. Using a SupervisorJob prevents
     * *one* failed upload from killing the rest.
     */
    //    private val uploadScope = CoroutineScope(uploadDispatcher + SupervisorJob())
    private val uploadScope = CoroutineScope(uploadDispatcher)

    data class State<O : OutputStream, T : RemoteObject<*>>(
        val formatterState: ObjectLoaderPartFormatter.State<O>,
        val partLoaderState: ObjectLoaderPartLoader.State<T>,
        val completerState: ObjectLoaderUploadCompleter.State,
        val uploads: MutableList<Deferred<ObjectLoaderPartLoader.PartResult<T>>> = mutableListOf(),
    ) : AutoCloseable {
        override fun close() {
            formatterState.close()
            partLoaderState.close()
            completerState.close()
        }
    }

    override suspend fun start(key: StreamKey, part: Int): State<O, T> {
        val fmt = partFormatter.start(key, part)
        val objKey = ObjectKey(stream = key.stream, objectKey = fmt.partFactory.key)
        return State(
            formatterState = fmt,
            partLoaderState = partLoader.start(objKey, part),
            completerState = uploadCompleter.start(objKey, part),
        )
    }

    override suspend fun accept(
        input: DestinationRecordRaw,
        state: State<O, T>,
    ): BatchAccumulatorResult<State<O, T>, ObjectLoaderUploadCompleter.UploadResult<T>> =
        when (val fmtResult = partFormatter.accept(input, state.formatterState)) {
            is NoOutput -> NoOutput(state.copy(formatterState = fmtResult.nextState))
            is IntermediateOutput -> {
                state.uploads += launchUpload(fmtResult.output, state.partLoaderState)
                NoOutput(state.copy(formatterState = fmtResult.nextState))
            }
            is FinalOutput -> uploadFinalAndFinish(fmtResult.output, state)
        }

    override suspend fun finish(
        state: State<O, T>
    ): FinalOutput<State<O, T>, ObjectLoaderUploadCompleter.UploadResult<T>> =
        uploadFinalAndFinish(partFormatter.finish(state.formatterState).output, state)

    private fun launchUpload(
        part: ObjectLoaderPartFormatter.FormattedPart,
        loaderState: ObjectLoaderPartLoader.State<T>,
    ): Deferred<ObjectLoaderPartLoader.PartResult<T>> =
        uploadScope.async {
            try {
                when (val res = partLoader.accept(part, loaderState)) {
                    is IntermediateOutput -> res.output
                    else -> error("PartLoader should emit IntermediateOutput only")
                }
            } finally {
                part.part.bytes?.let { ByteArrayPool.recycle(it) }
            }
        }

    private suspend fun uploadFinalAndFinish(
        finalPart: ObjectLoaderPartFormatter.FormattedPart,
        state: State<O, T>,
    ): FinalOutput<State<O, T>, ObjectLoaderUploadCompleter.UploadResult<T>> = supervisorScope {
        state.uploads += launchUpload(finalPart, state.partLoaderState)

        log.info { "Waiting on ${state.uploads.size} multipart uploads…" }

        val completerResult =
            async(uploadDispatcher) {
                // Feed each upload to the completer *as soon as it is ready*.
                // adding this just to make a commit to make the publish workflow run again
                state.uploads
                    .map { deferredPart ->
                        async(uploadDispatcher) {
                            val part = deferredPart.await()
                            uploadCompleter.accept(part, state.completerState)
                        }
                    }
                    .awaitAll() // Still non-blocking – we simply suspend
                    .firstOrNull { it is FinalOutput }
                    ?.let { it as FinalOutput<*, *> }
                    ?: error("Completer never produced FinalOutput – logic bug?")
            }

        // Suspend until the completer tells us we’re done,
        // then bubble its payload downstream.
        @Suppress("UNCHECKED_CAST")
        FinalOutput(completerResult.await().output as ObjectLoaderUploadCompleter.UploadResult<T>)
    }
}
