/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import com.google.common.annotations.VisibleForTesting
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfigurationProvider
import io.airbyte.cdk.load.file.StreamProcessor
import io.airbyte.cdk.load.file.object_storage.BufferedFormattingWriterFactory
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.MultiProducerChannel
import io.airbyte.cdk.load.message.object_storage.*
import io.airbyte.cdk.load.state.DestinationStateManager
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.state.object_storage.ObjectStorageDestinationState
import io.airbyte.cdk.load.write.BatchAccumulator
import io.airbyte.cdk.load.write.FileBatchAccumulator
import io.airbyte.cdk.load.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.io.File
import java.io.OutputStream

@Singleton
@Secondary
class ObjectStorageStreamLoaderFactory<T : RemoteObject<*>, U : OutputStream>(
    private val client: ObjectStorageClient<T>,
    private val pathFactory: ObjectStoragePathFactory,
    private val bufferedWriterFactory: BufferedFormattingWriterFactory<U>,
    private val compressionConfigurationProvider:
        ObjectStorageCompressionConfigurationProvider<U>? =
        null,
    private val uploadConfigurationProvider: ObjectStorageUploadConfigurationProvider,
    private val destinationStateManager: DestinationStateManager<ObjectStorageDestinationState>,
    @Value("\${airbyte.destination.record-batch-size-override}")
    private val recordBatchSizeOverride: Long? = null
) {
    fun create(stream: DestinationStream): StreamLoader {
        return ObjectStorageStreamLoader(
            stream,
            client,
            compressionConfigurationProvider?.objectStorageCompressionConfiguration?.compressor,
            pathFactory,
            bufferedWriterFactory,
            destinationStateManager,
            uploadConfigurationProvider.objectStorageUploadConfiguration.uploadPartSizeBytes,
            recordBatchSizeOverride
                ?: uploadConfigurationProvider.objectStorageUploadConfiguration.fileSizeBytes
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
    private val partSizeBytes: Long,
    private val fileSizeBytes: Long,
) : StreamLoader {
    private val log = KotlinLogging.logger {}

    private val objectAccumulator = PartToObjectAccumulator(stream, client)

    override suspend fun createBatchAccumulator(): BatchAccumulator {
        val state = destinationStateManager.getState(stream)
        return RecordToPartAccumulator(
            pathFactory,
            bufferedWriterFactory,
            partSizeBytes = partSizeBytes,
            fileSizeBytes = fileSizeBytes,
            stream,
            state.getPartIdCounter(pathFactory.getFinalDirectory(stream)),
        ) { name ->
            state.ensureUnique(name)
        }
    }

    override suspend fun createFileBatchAccumulator(
        outputQueue: MultiProducerChannel<BatchEnvelope<*>>,
    ): FileBatchAccumulator = FilePartAccumulator(pathFactory, stream, outputQueue)

    @VisibleForTesting fun createFile(url: String) = File(url)

    override suspend fun processBatch(batch: Batch): Batch = objectAccumulator.processBatch(batch)

    override suspend fun close(streamFailure: StreamProcessingFailed?) {
        if (streamFailure != null) {
            log.info { "Sync failed, persisting destination state for next run" }
        } else if (stream.shouldBeTruncatedAtEndOfSync()) {
            log.info { "Truncate sync succeeded, Removing old files" }
            val state = destinationStateManager.getState(stream)

            state.getObjectsToDelete().forEach { (generationId, objectAndPart) ->
                log.info {
                    "Deleting old object for generation $generationId: ${objectAndPart.key}"
                }
                client.delete(objectAndPart.key)
            }

            log.info { "Persisting state" }
        }
        destinationStateManager.persistState(stream)
    }
}
