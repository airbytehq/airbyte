/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

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
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.state.DestinationStateManager
import io.airbyte.cdk.load.state.StreamIncompleteResult
import io.airbyte.cdk.load.state.object_storage.ObjectStorageDestinationState
import io.airbyte.cdk.load.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.io.OutputStream
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
    data class StagedObject<T>(
        override val state: Batch.State = Batch.State.PERSISTED,
        val remoteObject: T,
        val partNumber: Long
    ) : ObjectStorageBatch
    data class FinalizedObject<T>(
        override val state: Batch.State = Batch.State.COMPLETE,
        val remoteObject: T,
    ) : ObjectStorageBatch

    private val partNumber = AtomicLong(0L)

    override suspend fun start() {
        val state = destinationStateManager.getState(stream)
        val maxPartNumber =
            state.generations
                .map {
                    println(it)
                    it
                }
                .filter { it.generationId >= stream.minimumGenerationId }
                .mapNotNull { it.objects.maxOfOrNull { obj -> obj.partNumber } }
                .maxOrNull()
        log.info { "Got max part number from destination state: $maxPartNumber" }
        maxPartNumber?.let { partNumber.set(it + 1L) }
    }

    override suspend fun processRecords(
        records: Iterator<DestinationRecord>,
        totalSizeBytes: Long
    ): Batch {
        val partNumber = partNumber.getAndIncrement()
        val key = pathFactory.getPathToFile(stream, partNumber, isStaging = true).toString()

        log.info { "Writing records to $key" }
        val state = destinationStateManager.getState(stream)
        state.addObject(stream.generationId, key, partNumber)

        val obj =
            client.streamingUpload(key, streamProcessor = compressor) { outputStream ->
                writerFactory.create(stream, outputStream).use { writer ->
                    records.forEach { writer.accept(it) }
                }
            }
        log.info { "Finished writing records to $key" }
        return StagedObject(remoteObject = obj, partNumber = partNumber)
    }

    @Suppress("UNCHECKED_CAST")
    override suspend fun processBatch(batch: Batch): Batch {
        val stagedObject = batch as StagedObject<T>
        val finalKey =
            pathFactory.getPathToFile(stream, stagedObject.partNumber, isStaging = false).toString()
        log.info { "Moving staged object from ${stagedObject.remoteObject.key} to $finalKey" }
        val newObject = client.move(stagedObject.remoteObject, finalKey)

        val state = destinationStateManager.getState(stream)
        state.removeObject(stream.generationId, stagedObject.remoteObject.key)
        state.addObject(stream.generationId, newObject.key, stagedObject.partNumber)

        val finalizedObject = FinalizedObject(remoteObject = newObject)
        return finalizedObject
    }

    override suspend fun close(streamFailure: StreamIncompleteResult?) {
        if (streamFailure != null) {
            log.info { "Sync failed, persisting destination state for next run" }
            destinationStateManager.persistState(stream)
        } else {
            log.info { "Sync succeeded, Moving any stragglers out of staging" }
            val state = destinationStateManager.getState(stream)
            val stagingToKeep =
                state.generations.filter {
                    it.isStaging && it.generationId >= stream.minimumGenerationId
                }
            stagingToKeep.toList().forEach {
                it.objects.forEach { obj ->
                    val newKey =
                        pathFactory
                            .getPathToFile(stream, obj.partNumber, isStaging = false)
                            .toString()
                    log.info { "Moving staged object from ${obj.key} to $newKey" }
                    val newObject = client.move(obj.key, newKey)
                    state.removeObject(it.generationId, obj.key, isStaging = true)
                    state.addObject(it.generationId, newObject.key, obj.partNumber)
                }
            }

            log.info { "Removing old files" }
            val (toKeep, toDrop) =
                state.generations.partition { it.generationId >= stream.minimumGenerationId }
            val keepKeys = toKeep.flatMap { it.objects.map { obj -> obj.key } }.toSet()
            toDrop
                .flatMap { it.objects.filter { obj -> obj.key !in keepKeys } }
                .forEach {
                    log.info { "Deleting object ${it.key}" }
                    client.delete(it.key)
                }

            log.info { "Updating and persisting state" }
            state.dropGenerationsBefore(stream.minimumGenerationId)
            destinationStateManager.persistState(stream)
        }
    }
}
