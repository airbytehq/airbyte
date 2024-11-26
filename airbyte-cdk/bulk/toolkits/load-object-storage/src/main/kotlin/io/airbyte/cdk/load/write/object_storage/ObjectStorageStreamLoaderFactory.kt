/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import com.google.common.annotations.VisibleForTesting
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfigurationProvider
import io.airbyte.cdk.load.file.NoopProcessor
import io.airbyte.cdk.load.file.StreamProcessor
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.ObjectStorageFormattingWriterFactory
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.state.DestinationStateManager
import io.airbyte.cdk.load.state.StreamIncompleteResult
import io.airbyte.cdk.load.state.object_storage.ObjectStorageDestinationState
import io.airbyte.cdk.load.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.io.File
import java.io.OutputStream
import java.nio.file.Path
import java.util.concurrent.atomic.AtomicLong

@Singleton
@Secondary
class ObjectStorageStreamLoaderFactory<T : RemoteObject<*>>(
    private val client: ObjectStorageClient<T>,
    private val compressionConfig: ObjectStorageCompressionConfigurationProvider<*>? = null,
    private val pathFactory: ObjectStoragePathFactory,
    private val writerFactory: ObjectStorageFormattingWriterFactory,
    private val destinationStateManager: DestinationStateManager<ObjectStorageDestinationState>,
) {
    fun create(stream: DestinationStream): StreamLoader {
        return ObjectStorageStreamLoader(
            stream,
            client,
            compressionConfig?.objectStorageCompressionConfiguration?.compressor ?: NoopProcessor,
            pathFactory,
            writerFactory,
            destinationStateManager
        )
    }
}

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class ObjectStorageStreamLoader<T : RemoteObject<*>, U : OutputStream>(
    override val stream: DestinationStream,
    private val client: ObjectStorageClient<T>,
    private val compressor: StreamProcessor<U>,
    private val pathFactory: ObjectStoragePathFactory,
    private val writerFactory: ObjectStorageFormattingWriterFactory,
    private val destinationStateManager: DestinationStateManager<ObjectStorageDestinationState>,
) : StreamLoader {
    private val log = KotlinLogging.logger {}

    sealed interface ObjectStorageBatch : Batch
    data class RemoteObject<T>(
        override val state: Batch.State = Batch.State.COMPLETE,
        val remoteObject: T,
        val partNumber: Long
    ) : ObjectStorageBatch

    private val partNumber = AtomicLong(0L)

    override suspend fun start() {
        val state = destinationStateManager.getState(stream)
        val nextPartNumber = state.nextPartNumber
        log.info { "Got next part number from destination state: $nextPartNumber" }
        partNumber.set(nextPartNumber)
    }

    override suspend fun processRecords(
        records: Iterator<DestinationRecord>,
        totalSizeBytes: Long
    ): Batch {
        val partNumber = partNumber.getAndIncrement()
        val key =
            pathFactory.getPathToFile(stream, partNumber, isStaging = pathFactory.supportsStaging)

        log.info { "Writing records to $key" }
        val state = destinationStateManager.getState(stream)
        state.addObject(
            stream.generationId,
            key,
            partNumber,
            isStaging = pathFactory.supportsStaging
        )

        val metadata = ObjectStorageDestinationState.metadataFor(stream)
        val obj =
            client.streamingUpload(key, metadata, streamProcessor = compressor) { outputStream ->
                writerFactory.create(stream, outputStream).use { writer ->
                    records.forEach {
                        // TODO: S3V2: Remove before release
                        println("Writing record: $it")
                        writer.accept(it)
                    }
                }
            }
        log.info { "Finished writing records to $key, persisting state" }
        destinationStateManager.persistState(stream)
        return RemoteObject(remoteObject = obj, partNumber = partNumber)
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
        return RemoteObject(remoteObject = obj, partNumber = 0)
    }

    @VisibleForTesting fun createFile(url: String) = File(url)

    override suspend fun processBatch(batch: Batch): Batch {
        throw NotImplementedError(
            "All post-processing occurs in the close method; this should not be called"
        )
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
