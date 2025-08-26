/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.bulk_loader

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.file.gcs.GcsBlob
import io.airbyte.cdk.load.file.object_storage.ByteArrayPool
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.BatchAccumulator
import io.airbyte.cdk.load.pipeline.BatchAccumulatorResult
import io.airbyte.cdk.load.pipeline.FinalOutput
import io.airbyte.cdk.load.pipeline.IntermediateOutput
import io.airbyte.cdk.load.pipeline.NoOutput
import io.airbyte.cdk.load.pipeline.db.BulkLoaderTableLoader
import io.airbyte.cdk.load.pipline.object_storage.ObjectKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartFormatter
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartLoader
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadCompleter
import io.airbyte.cdk.load.write.db.BulkLoader
import io.airbyte.cdk.load.write.db.BulkLoaderFactory
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
import kotlinx.coroutines.coroutineScope

@Singleton
@Requires(bean = BulkLoaderFactory::class)
@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION")
class BigQueryBulkOneShotUploader<O : OutputStream>(
    private val partFormatter: ObjectLoaderPartFormatter<O>,
    private val partLoader: ObjectLoaderPartLoader<GcsBlob>,
    private val uploadCompleter: ObjectLoaderUploadCompleter<GcsBlob>,
    private val bulkLoaderFactory: BulkLoaderFactory<StreamKey, GcsBlob>,
    @Named("uploadParallelismForSocket") private val uploadParallelism: Int,
) :
    BatchAccumulator<
        BigQueryBulkOneShotUploader.State<O>,
        StreamKey,
        DestinationRecordRaw,
        BulkLoaderTableLoader.LoadResult
    > {

    private val log = KotlinLogging.logger {}

    @OptIn(ExperimentalCoroutinesApi::class)
    private val uploadDispatcher = Dispatchers.IO.limitedParallelism(uploadParallelism)

    data class State<O : OutputStream>(
        val streamKey: StreamKey,
        val formatterState: ObjectLoaderPartFormatter.State<O>,
        val partLoaderState: ObjectLoaderPartLoader.State<GcsBlob>,
        val completerState: ObjectLoaderUploadCompleter.State,
        val bulkLoader: BulkLoader<GcsBlob>,
        val uploads: MutableList<Deferred<ObjectLoaderPartLoader.PartResult<GcsBlob>>> =
            mutableListOf(),
        val bigqueryLoads: MutableList<Deferred<Unit>> = mutableListOf(),
    ) : AutoCloseable {
        override fun close() {
            formatterState.close()
            partLoaderState.close()
            completerState.close()
            bulkLoader.close()
        }
    }

    override suspend fun start(key: StreamKey, part: Int): State<O> {
        log.info {
            "Starting BigQuery bulk one-shot upload for stream ${key.stream} partition $part"
        }

        val fmt = partFormatter.startLockFree(key)
        val objKey = ObjectKey(stream = key.stream, objectKey = fmt.partFactory.key)

        return State(
            streamKey = key,
            formatterState = fmt,
            partLoaderState = partLoader.start(objKey, part),
            completerState = uploadCompleter.start(objKey, part),
            bulkLoader = bulkLoaderFactory.create(key, part),
        )
    }

    override suspend fun accept(
        input: DestinationRecordRaw,
        state: State<O>,
    ): BatchAccumulatorResult<State<O>, BulkLoaderTableLoader.LoadResult> {
        return when (val fmtResult = partFormatter.accept(input, state.formatterState)) {
            is NoOutput -> NoOutput(state.copy(formatterState = fmtResult.nextState))
            is IntermediateOutput -> {
                // Launch async upload for intermediate part
                state.uploads += launchUpload(fmtResult.output, state.partLoaderState)
                NoOutput(state.copy(formatterState = fmtResult.nextState))
            }
            is FinalOutput ->
                uploadFinalAndExecuteBigQueryLoad(fmtResult.output, state, isFinish = false)
        }
    }

    override suspend fun finish(
        state: State<O>
    ): FinalOutput<State<O>, BulkLoaderTableLoader.LoadResult> =
        uploadFinalAndExecuteBigQueryLoad(
            partFormatter.finish(state.formatterState).output,
            state,
            isFinish = true
        )

    private fun launchUpload(
        part: ObjectLoaderPartFormatter.FormattedPart,
        loaderState: ObjectLoaderPartLoader.State<GcsBlob>,
    ): Deferred<ObjectLoaderPartLoader.PartResult<GcsBlob>> =
        CoroutineScope(uploadDispatcher).async {
            try {
                when (val res = partLoader.acceptWithExperimentalCoroutinesApi(part, loaderState)) {
                    is IntermediateOutput -> res.output
                    else -> error("PartLoader should emit IntermediateOutput only")
                }
            } finally {
                // Recycle byte arrays to optimize memory usage in socket mode
                part.part.bytes?.let { ByteArrayPool.recycle(it) }
            }
        }

    private fun launchBigQueryLoad(
        blob: GcsBlob,
        bulkLoader: BulkLoader<GcsBlob>,
        streamKey: StreamKey
    ): Deferred<Unit> =
        CoroutineScope(uploadDispatcher).async {
            try {
                bulkLoader.load(blob)
                log.info { "BigQuery load completed successfully for ${streamKey.stream}" }
            } catch (e: Exception) {
                log.error(e) { "BigQuery load failed for ${streamKey.stream}: ${e.message}" }
                throw e // Re-throw to be caught by awaitAll in finish()
            }
        }

    private suspend fun uploadFinalAndExecuteBigQueryLoad(
        finalPart: ObjectLoaderPartFormatter.FormattedPart,
        state: State<O>,
        isFinish: Boolean
    ): FinalOutput<State<O>, BulkLoaderTableLoader.LoadResult> = coroutineScope {
        // Upload the final part
        state.uploads += launchUpload(finalPart, state.partLoaderState)

        log.info { "Awaiting ${state.uploads.size} part uploads for ${state.streamKey.stream}…" }

        // Wait for all uploads to complete and process through upload completer
        var completedGcsBlob: GcsBlob? = null
        state.uploads.awaitAll().forEach { part ->
            when (val res = uploadCompleter.accept(part, state.completerState)) {
                is NoOutput -> Unit // Continue processing parts
                is FinalOutput -> {
                    completedGcsBlob = res.output.remoteObject
                    log.info {
                        "GCS upload completed for ${state.streamKey.stream}: ${completedGcsBlob?.key}"
                    }
                    return@forEach
                }
                else -> error("Unexpected output from upload completer: $res")
            }
        }

        val finalBlob = completedGcsBlob
        if (finalBlob != null) {
            if (isFinish) {
                // When finish() is called, launch final load and wait for all loads to complete
                log.info {
                    "Launching final BigQuery load for ${state.streamKey.stream} from GCS: ${finalBlob.key}"
                }
                state.bigqueryLoads +=
                    launchBigQueryLoad(finalBlob, state.bulkLoader, state.streamKey)

                log.info {
                    "Awaiting ${state.bigqueryLoads.size} BigQuery loads to complete for ${state.streamKey.stream}…"
                }
                try {
                    state.bigqueryLoads.awaitAll()
                    log.info {
                        "All BigQuery loads completed successfully for ${state.streamKey.stream}"
                    }
                } catch (e: Exception) {
                    log.error(e) {
                        "One or more BigQuery loads failed for ${state.streamKey.stream}: ${e.message}"
                    }
                    throw e // Propagate any load errors when finish() is called
                }

                FinalOutput(BulkLoaderTableLoader.LoadResult)
            } else {
                // For intermediate final parts, launch async
                log.info {
                    "Launching async BigQuery load for ${state.streamKey.stream} from GCS: ${finalBlob.key}"
                }

                state.bigqueryLoads +=
                    launchBigQueryLoad(finalBlob, state.bulkLoader, state.streamKey)

                log.info {
                    "BigQuery load initiated for ${state.streamKey.stream} - pipeline continuing " +
                        "(${state.bigqueryLoads.size} loads running)"
                }

                FinalOutput(BulkLoaderTableLoader.LoadResult)
            }
        } else {
            error("Upload completer never produced a completed GCS blob – logic bug in socket mode")
        }
    }
}
