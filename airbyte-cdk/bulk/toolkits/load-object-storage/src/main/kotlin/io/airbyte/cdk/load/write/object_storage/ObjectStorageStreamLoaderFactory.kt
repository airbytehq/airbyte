/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import com.google.common.annotations.VisibleForTesting
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfigurationProvider
import io.airbyte.cdk.load.file.StreamProcessor
import io.airbyte.cdk.load.file.object_storage.BufferedFormattingWriter
import io.airbyte.cdk.load.file.object_storage.BufferedFormattingWriterFactory
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.state.DestinationStateManager
import io.airbyte.cdk.load.state.StreamIncompleteResult
import io.airbyte.cdk.load.state.object_storage.ObjectStorageDestinationState
import io.airbyte.cdk.load.write.BatchAccumulator
import io.airbyte.cdk.load.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.io.File
import java.io.OutputStream
import java.nio.file.Path
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference
import kotlinx.coroutines.CompletableDeferred
import org.apache.mina.util.ConcurrentHashSet

@Singleton
@Secondary
class ObjectStorageStreamLoaderFactory<T : RemoteObject<*>, U : OutputStream>(
    private val config: DestinationConfiguration,
    private val client: ObjectStorageClient<T>,
    private val pathFactory: ObjectStoragePathFactory,
    private val bufferedWriterFactory: BufferedFormattingWriterFactory<U>,
    private val compressionConfigurationProvider:
        ObjectStorageCompressionConfigurationProvider<U>? =
        null,
    private val destinationStateManager: DestinationStateManager<ObjectStorageDestinationState>,
    private val uploadConfigurationProvider: ObjectStorageUploadConfigurationProvider,
) {
    fun create(stream: DestinationStream): StreamLoader {
        return ObjectStorageStreamLoader(
            stream,
            client,
            compressionConfigurationProvider?.objectStorageCompressionConfiguration?.compressor,
            pathFactory,
            bufferedWriterFactory,
            destinationStateManager,
            recordBatchSizeBytes = config.recordBatchSizeBytes
        )
    }
}

@SuppressFBWarnings(
    value = ["NP_NONNULL_PARAM_VIOLATION", "NP_NULL_ON_SOME_PATH_FROM_RETURN_VALUE"],
    justification = "Kotlin async continuation"
)
class ObjectStorageStreamLoader<T : RemoteObject<*>, U : OutputStream>(
    override val stream: DestinationStream,
    private val client: ObjectStorageClient<T>,
    private val compressor: StreamProcessor<U>?,
    private val pathFactory: ObjectStoragePathFactory,
    private val bufferedWriterFactory: BufferedFormattingWriterFactory<U>,
    private val destinationStateManager: DestinationStateManager<ObjectStorageDestinationState>,
    private val recordBatchSizeBytes: Long,
) : StreamLoader {
    private val log = KotlinLogging.logger {}

    sealed interface ObjectStorageBatch : Batch

    // An indexed bytearray containing an uploadable chunk of a file.
    // Returned by the batch accumulator after processing records.
    class LoadablePart(
        val key: String,
        val fileNumber: Long,
        val bytes: ByteArray?, // can be null on final
        val index: Int,
        val isFinalPart: Boolean,
    ) : ObjectStorageBatch {
        override val groupId = null
        override val state = Batch.State.LOCAL
    }

    // An UploadablePart that has been uploaded to an incomplete object.
    // Returned by processBatch
    data class IncompletePartialUpload(val key: String, val fileNumber: Long) : ObjectStorageBatch {
        override val state: Batch.State = Batch.State.LOCAL
        override val groupId: String = key
    }

    // An UploadablePart that has triggered a completed upload.
    data class LoadedObject<T : RemoteObject<*>>(
        val remoteObject: T,
        val fileNumber: Long,
    ) : ObjectStorageBatch {
        override val state: Batch.State = Batch.State.COMPLETE
        override val groupId = remoteObject.key
    }

    // Used for naming files. Distinct from part index, which is used to track uploads.
    private val fileNumber = AtomicLong(0L)

    override suspend fun start() {
        val state = destinationStateManager.getState(stream)
        val nextPartNumber = state.nextPartNumber
        log.info { "Got next part number from destination state: $nextPartNumber" }
        fileNumber.set(nextPartNumber)
    }

    data class PartialObject<T : OutputStream>(
        val key: String,
        val fileNumber: Long,
        val partIndex: Int,
        val accumulatedSize: Long,
        val writer: BufferedFormattingWriter<T>,
    )

    inner class PartAccumulator : BatchAccumulator {
        private val objectInProgress = AtomicReference<PartialObject<U>>()

        override suspend fun processRecords(
            records: Iterator<DestinationRecord>,
            totalSizeBytes: Long,
            endOfStream: Boolean
        ): Batch {
            // Start a new object if there is not one in progress.
            objectInProgress.compareAndSet(
                null,
                PartialObject(
                    key =
                        pathFactory.getPathToFile(
                            stream,
                            fileNumber.getAndIncrement(),
                            isStaging = pathFactory.supportsStaging
                        ),
                    fileNumber = fileNumber.get(),
                    partIndex = 0,
                    accumulatedSize = 0,
                    writer = bufferedWriterFactory.create(stream),
                )
            )
            val partialObject = objectInProgress.get()

            // Add all the records to the formatting writer.
            log.info {
                "Accumulating ${totalSizeBytes}b records for part ${partialObject.partIndex} of ${partialObject.key}"
            }
            records.forEach { partialObject.writer.accept(it) }
            partialObject.writer.flush()

            // Check if we have reached the target size.
            val newSize = partialObject.accumulatedSize + partialObject.writer.bufferSize
            val nextIndex = partialObject.partIndex + 1 // 1-indexed, so pre-increment
            if (newSize >= recordBatchSizeBytes || endOfStream) {

                // If we have reached target size, clear the object and yield a final part.
                val bytes = partialObject.writer.finish()
                log.info {
                    "Size $newSize/${recordBatchSizeBytes}b reached (endOfStream=$endOfStream), yielding final part $nextIndex (empty=${bytes == null})"
                }
                partialObject.writer.close()
                objectInProgress.set(null)

                return LoadablePart(
                    key = partialObject.key,
                    fileNumber = partialObject.fileNumber,
                    bytes = bytes,
                    index = nextIndex,
                    isFinalPart = true
                )
            } else {
                // If we have not reached target size, advance the object and yield a non-final
                // part.
                objectInProgress.set(
                    partialObject.copy(
                        accumulatedSize = newSize,
                        partIndex = nextIndex,
                    )
                )

                val bytes =
                    if (partialObject.writer.bufferSize > 0) {
                        partialObject.writer.takeBytes()
                    } else {
                        null
                    }

                log.info {
                    "Size $newSize/${recordBatchSizeBytes}b not reached, yielding part ${partialObject.partIndex} (empty=${bytes == null})"
                }

                return LoadablePart(
                    key = partialObject.key,
                    fileNumber = partialObject.fileNumber,
                    bytes = bytes,
                    index = nextIndex,
                    isFinalPart = false
                )
            }
        }
    }

    override suspend fun createBatchAccumulator(): BatchAccumulator {
        return PartAccumulator()
    }

    override suspend fun processFile(file: DestinationFile): Batch {
        if (pathFactory.supportsStaging) {
            throw IllegalStateException("Staging is not supported for files")
        }
        val key =
            Path.of(pathFactory.getFinalDirectory(stream).toString(), file.fileMessage.fileUrl!!)
                .toString()

        val state = destinationStateManager.getState(stream)
        state.addObject(
            generationId = stream.generationId,
            key = key,
            partNumber = 0,
            isStaging = false
        )

        val localFile = createFile(file.fileMessage.fileUrl!!)

        val metadata = ObjectStorageDestinationState.metadataFor(stream)
        val obj =
            client.streamingUpload(key, metadata, streamProcessor = compressor) { outputStream ->
                File(file.fileMessage.fileUrl!!).inputStream().use { it.copyTo(outputStream) }
            }
        localFile.delete()
        return LoadedObject(remoteObject = obj, fileNumber = 0)
    }

    @VisibleForTesting fun createFile(url: String) = File(url)

    inner class LoadInProgress(
        val streamingUpload: CompletableDeferred<StreamingUpload<T>> = CompletableDeferred(),
        val indexesOrCompletion: ConcurrentHashSet<Int> = ConcurrentHashSet()
    )
    private val uploadsInProgress = ConcurrentHashMap<String, LoadInProgress>()
    override suspend fun processBatch(batch: Batch): Batch {
        batch as LoadablePart
        val load = uploadsInProgress.getOrPut(batch.key) { LoadInProgress() }

        log.info {
            "Processing loadable part ${batch.index} of ${batch.key} (empty=${batch.bytes==null})"
        }

        // Start the upload if we haven't already. Note that the `complete`
        // here refers to the completable deferred, not the streaming upload.
        val metadata = ObjectStorageDestinationState.metadataFor(stream)
        load.streamingUpload.complete(client.startStreamingUpload(batch.key, metadata))
        val streamingUpload = load.streamingUpload.await()

        // Upload provided bytes and update indexes.
        if (batch.bytes != null) {
            streamingUpload.uploadPart(batch.bytes, batch.index)
        }
        load.indexesOrCompletion.add(batch.index) // Allow for empty parts
        if (batch.isFinalPart) {
            val finalIndex = batch.index
            load.indexesOrCompletion.add(-finalIndex)
        }

        // TODO: Simplify this once we have workers pulling from queues.
        // If we've loaded a final part AND have all the indexes, we can complete the upload.
        // Eg, {-2, 1, 2} ⇒ final == 2, first == -final, so:
        // (-first == last) AND (last == size - 1) ⇒ done
        // It's okay if we have a race condition here, because completes are idempotent and
        // state updates are atomic.
        val sorted = load.indexesOrCompletion.sorted()
        log.info { "Parts already uploaded: $sorted" }
        if (
            sorted.isNotEmpty() // At least one part has been loaded
            &&
                (sorted.first() < 0) // A final part has been loaded
                &&
                (-sorted.first() == sorted.last()) // The final part is the last part
                &&
                (sorted.last() == sorted.size - 1) // There are no missing parts
        ) {
            val obj = streamingUpload.complete()
            uploadsInProgress.remove(batch.key)

            // Mark that we've completed the upload and persist the state before returning the
            // persisted batch.
            // Otherwise, we might lose track of the upload if the process crashes before
            // persisting.
            // TODO: Just move/del everything in staging on close, respecting the gen id, so we
            // don't need this.
            val state = destinationStateManager.getState(stream)
            state.addObject(
                stream.generationId,
                obj.key,
                batch.fileNumber,
                isStaging = pathFactory.supportsStaging
            )
            destinationStateManager.persistState(stream)

            log.info { "Completed upload of ${obj.key}" }
            return LoadedObject(remoteObject = obj, fileNumber = batch.fileNumber)
        } else {
            log.info { "Upload of ${batch.key} is not yet complete" }
            // Because this is an incomplete batch with a group id, the framework won't return it.
            return IncompletePartialUpload(key = batch.key, fileNumber = batch.fileNumber)
        }
    }

    override suspend fun close(streamFailure: StreamIncompleteResult?) {
        if (streamFailure != null) {
            log.info { "Sync failed, persisting destination state for next run" }
            destinationStateManager.persistState(stream)
        } else {
            val state = destinationStateManager.getState(stream)
            log.info { "Sync succeeded, Removing old files" }
            state.getObjectsToDelete(stream.minimumGenerationId).forEach {
                (generationId, objectAndPart) ->
                log.info {
                    "Deleting old object for generation $generationId: ${objectAndPart.key}"
                }
                client.delete(objectAndPart.key)
                state.removeObject(generationId, objectAndPart.key)
            }

            log.info { "Moving all current data out of staging" }
            state.getStagedObjectsToFinalize(stream.minimumGenerationId).forEach {
                (generationId, objectAndPart) ->
                val newKey =
                    pathFactory.getPathToFile(stream, objectAndPart.partNumber, isStaging = false)
                log.info {
                    "Moving staged object of generation $generationId: ${objectAndPart.key} to $newKey"
                }
                val newObject = client.move(objectAndPart.key, newKey)
                state.removeObject(generationId, objectAndPart.key, isStaging = true)
                state.addObject(generationId, newObject.key, objectAndPart.partNumber)
            }

            log.info { "Persisting state" }
            destinationStateManager.persistState(stream)
        }
    }
}
