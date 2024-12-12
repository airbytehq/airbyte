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
import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.file.object_storage.PartFactory
import io.airbyte.cdk.load.file.object_storage.PartMetadataAssembler
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
    class LoadablePart(val part: Part) : ObjectStorageBatch {
        override val groupId = null
        override val state = Batch.State.LOCAL
    }

    // An UploadablePart that has been uploaded to an incomplete object.
    // Returned by processBatch
    data class IncompletePartialUpload(val key: String) : ObjectStorageBatch {
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

    data class ObjectInProgress<T : OutputStream>(
        val partFactory: PartFactory,
        val writer: BufferedFormattingWriter<T>,
    )

    inner class PartAccumulator : BatchAccumulator {
        private val currentObject = AtomicReference<ObjectInProgress<U>>()

        override suspend fun processRecords(
            records: Iterator<DestinationRecord>,
            totalSizeBytes: Long,
            endOfStream: Boolean
        ): Batch {
            // Start a new object if there is not one in progress.
            currentObject.compareAndSet(
                null,
                ObjectInProgress(
                    partFactory =
                        PartFactory(
                            key =
                                pathFactory.getPathToFile(
                                    stream,
                                    fileNumber.getAndIncrement(),
                                    isStaging = pathFactory.supportsStaging
                                ),
                            fileNumber = fileNumber.get()
                        ),
                    writer = bufferedWriterFactory.create(stream),
                )
            )
            val partialUpload = currentObject.get()

            // Add all the records to the formatting writer.
            log.info {
                "Accumulating ${totalSizeBytes}b records for ${partialUpload.partFactory.key}"
            }
            records.forEach { partialUpload.writer.accept(it) }
            partialUpload.writer.flush()

            // Check if we have reached the target size.
            val newSize = partialUpload.partFactory.totalSize + partialUpload.writer.bufferSize
            if (newSize >= recordBatchSizeBytes || endOfStream) {

                // If we have reached target size, clear the object and yield a final part.
                val bytes = partialUpload.writer.finish()
                partialUpload.writer.close()
                val part = partialUpload.partFactory.nextPart(bytes, isFinal = true)

                log.info {
                    "Size $newSize/${recordBatchSizeBytes}b reached (endOfStream=$endOfStream), yielding final part ${part.partIndex} (empty=${part.isEmpty})"
                }

                currentObject.set(null)
                return LoadablePart(part)
            } else {
                // If we have not reached target size, just yield the next part.
                val bytes = partialUpload.writer.takeBytes()
                val part = partialUpload.partFactory.nextPart(bytes)
                log.info {
                    "Size $newSize/${recordBatchSizeBytes}b not reached, yielding part ${part.partIndex} (empty=${part.isEmpty})"
                }

                return LoadablePart(part)
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
        val fileUrl = file.fileMessage.fileUrl ?: ""
        if (!File(fileUrl).exists()) {
            log.error { "File does not exist: $fileUrl" }
            throw IllegalStateException("File does not exist: $fileUrl")
        }
        val key =
            Path.of(pathFactory.getFinalDirectory(stream), "${file.fileMessage.fileRelativePath}")
                .toString()

        val state = destinationStateManager.getState(stream)
        state.addObject(
            generationId = stream.generationId,
            key = key,
            partNumber = 0,
            isStaging = false
        )

        val metadata = ObjectStorageDestinationState.metadataFor(stream)
        val obj =
            client.streamingUpload(key, metadata, streamProcessor = compressor) { outputStream ->
                File(fileUrl).inputStream().use { it.copyTo(outputStream) }
            }
        val localFile = createFile(fileUrl)
        localFile.delete()
        return LoadedObject(remoteObject = obj, fileNumber = 0)
    }

    @VisibleForTesting fun createFile(url: String) = File(url)

    data class UploadInProgress<T : RemoteObject<*>>(
        val streamingUpload: CompletableDeferred<StreamingUpload<T>> = CompletableDeferred(),
        val partMetadataAssembler: PartMetadataAssembler = PartMetadataAssembler()
    )

    private val uploadsInProgress = ConcurrentHashMap<String, UploadInProgress<T>>()
    override suspend fun processBatch(batch: Batch): Batch {
        batch as LoadablePart
        val upload = uploadsInProgress[batch.part.key] ?: UploadInProgress()
        if (upload.partMetadataAssembler.isEmpty) {
            // Start the upload if we haven't already. Note that the `complete`
            // here refers to the completable deferred, not the streaming upload.
            val metadata = ObjectStorageDestinationState.metadataFor(stream)
            upload.streamingUpload.complete(client.startStreamingUpload(batch.part.key, metadata))
        }
        val streamingUpload = upload.streamingUpload.await()

        upload.partMetadataAssembler.add(batch.part)

        log.info {
            "Processing loadable part ${batch.part.partIndex} of ${batch.part.key} (empty=${batch.part.isEmpty})"
        }

        // Upload provided bytes and update indexes.
        if (batch.part.bytes != null) {
            streamingUpload.uploadPart(batch.part.bytes, batch.part.partIndex)
        }
        if (upload.partMetadataAssembler.isComplete) {
            val obj = streamingUpload.complete()
            uploadsInProgress.remove(batch.part.key)

            val state = destinationStateManager.getState(stream)
            state.addObject(
                stream.generationId,
                obj.key,
                batch.part.fileNumber,
                isStaging = pathFactory.supportsStaging
            )
            destinationStateManager.persistState(stream)

            // Mark that we've completed the upload and persist the state before returning the
            // persisted batch.
            // Otherwise, we might lose track of the upload if the process crashes before
            // persisting.
            // TODO: Just move/del everything in staging on close, respecting the gen id, so we
            // don't need this.
            log.info { "Completed upload of ${obj.key}" }
            return LoadedObject(remoteObject = obj, fileNumber = batch.part.fileNumber)
        } else {
            return IncompletePartialUpload(batch.part.key)
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
