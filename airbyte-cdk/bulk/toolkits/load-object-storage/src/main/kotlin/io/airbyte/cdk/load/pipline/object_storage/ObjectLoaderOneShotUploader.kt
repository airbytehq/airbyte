/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

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
import kotlinx.coroutines.Deferred
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit

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
    @Named("sharedUploadPermits") private val sharedUploadPermits: Semaphore
) :
    BatchAccumulator<
        ObjectLoaderOneShotUploader.State<O, T>,
        StreamKey,
        DestinationRecordRaw,
        ObjectLoaderUploadCompleter.UploadResult<T>
    > {
    private val log = KotlinLogging.logger {}

    data class State<O : OutputStream, T : RemoteObject<*>>(
        val formatterState: ObjectLoaderPartFormatter.State<O>,
        val partLoaderState: ObjectLoaderPartLoader.State<T>,
        val completerState: ObjectLoaderUploadCompleter.State,
        val partUploads:
            MutableList<
                Deferred<
                    BatchAccumulatorResult<
                        ObjectLoaderPartLoader.State<T>, ObjectLoaderPartLoader.PartResult<T>>
                >
            > =
            mutableListOf(),
        val finalPartUploaded: Boolean = false
    ) : AutoCloseable {
        override fun close() {
            formatterState.close()
            partLoaderState.close()
            completerState.close()
        }
    }

    override suspend fun start(key: StreamKey, part: Int): State<O, T> {
        val formatterState = partFormatter.start(key, part)
        val objectKey = ObjectKey(stream = key.stream, objectKey = formatterState.partFactory.key)
        val partLoaderState = partLoader.start(objectKey, part)
        val completerState = uploadCompleter.start(objectKey, part)
        return State(formatterState, partLoaderState, completerState)
    }

    override suspend fun accept(
        input: DestinationRecordRaw,
        state: State<O, T>
    ): BatchAccumulatorResult<State<O, T>, ObjectLoaderUploadCompleter.UploadResult<T>> =
        coroutineScope {
            // First, pass the input through the wrapped PartFormatter, handling its output instead
            // of forwarding it.
            when (val formatterResult = partFormatter.accept(input, state.formatterState)) {
                // No output: still accumulating parts.
                is NoOutput -> NoOutput(state.copy(formatterState = formatterResult.nextState))

                // Intermediate output: this is a non-final formatted part that needs to be
                // uploaded.
                is IntermediateOutput -> {
                    val formattedPart = formatterResult.output
                    val partUpload = async {
                        sharedUploadPermits.withPermit {
                            partLoader.accept(formattedPart, state.partLoaderState)
                        }
                    }
                    state.partUploads.add(partUpload)
                    // TODO: Async kick off the upload
                    NoOutput(state.copy(formatterState = formatterResult.nextState))
                }

                // Final output: this is the last part for a whole object.
                is FinalOutput -> {
                    uploadFinalPartAndFinish(formatterResult.output, state)
                }
            }
        }

    // Finish only gets called if the last task did not
    override suspend fun finish(
        state: State<O, T>
    ): FinalOutput<State<O, T>, ObjectLoaderUploadCompleter.UploadResult<T>> {
        val finalPart = partFormatter.finish(state.formatterState).output
        return uploadFinalPartAndFinish(finalPart, state)
    }

    private suspend fun uploadFinalPartAndFinish(
        finalPart: ObjectLoaderPartFormatter.FormattedPart,
        state: State<O, T>
    ): FinalOutput<State<O, T>, ObjectLoaderUploadCompleter.UploadResult<T>> = coroutineScope {
        val partUpload = async {
            sharedUploadPermits.withPermit { partLoader.accept(finalPart, state.partLoaderState) }
        }
        state.partUploads.add(partUpload)

        var finalCompleterResult: ObjectLoaderUploadCompleter.UploadResult<T>? = null
        log.info { "Awaiting part upload completion." }
        val uploadResults = state.partUploads.awaitAll()
        uploadResults.forEach { partUploadResult ->
            val completerResult =
                when (partUploadResult) {
                    is IntermediateOutput ->
                        uploadCompleter.accept(partUploadResult.output, state.completerState)
                    is FinalOutput,
                    is NoOutput ->
                        throw IllegalStateException(
                            "Part loader returns only IntermediateOutput=>Uploaded part"
                        )
                }
            when (completerResult) {
                is FinalOutput -> {
                    if (finalCompleterResult != null) {
                        throw IllegalStateException(
                            "Upload completer returned multiple final outputs, this should not happen"
                        )
                    }
                    finalCompleterResult = completerResult.output
                }
                is NoOutput -> {}
                is IntermediateOutput ->
                    throw IllegalStateException(
                        "Upload completer should return only NoOutput=>incomplete or FinalOutput=>complete"
                    )
            }
        }

        finalCompleterResult?.let { FinalOutput(it) }
            ?: throw IllegalStateException(
                "Upload completer did not return a final output, this should not happen"
            )
    }
}
