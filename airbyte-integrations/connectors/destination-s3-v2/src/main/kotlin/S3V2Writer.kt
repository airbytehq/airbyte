/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.ObjectStorageFormattingWriterFactory
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.s3.S3Client
import io.airbyte.cdk.load.file.s3.S3Object
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.state.DestinationStateManager
import io.airbyte.cdk.load.state.StreamIncompleteResult
import io.airbyte.cdk.load.state.object_storage.ObjectStorageDestinationState
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicLong

@Singleton
class S3V2Writer(
    private val s3Client: S3Client,
    private val pathFactory: ObjectStoragePathFactory,
    private val writerFactory: ObjectStorageFormattingWriterFactory,
    private val destinationStateManager: DestinationStateManager<ObjectStorageDestinationState>,
) : DestinationWriter {
    private val log = KotlinLogging.logger {}

    sealed interface S3V2Batch : Batch
    data class StagedObject(
        override val state: Batch.State = Batch.State.PERSISTED,
        val s3Object: S3Object,
        val partNumber: Long
    ) : S3V2Batch
    data class FinalizedObject(
        override val state: Batch.State = Batch.State.COMPLETE,
        val s3Object: S3Object,
    ) : S3V2Batch

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return S3V2StreamLoader(stream)
    }

    @SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
    inner class S3V2StreamLoader(override val stream: DestinationStream) : StreamLoader {
        private val partNumber = AtomicLong(0L)

        override suspend fun start() {
            val state = destinationStateManager.getState(stream)
            val maxPartNumber =
                state.generations
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

            val s3Object =
                s3Client.streamingUpload(key) { outputStream ->
                    writerFactory.create(stream, outputStream).use { writer ->
                        records.forEach { writer.accept(it) }
                    }
                }
            log.info { "Finished writing records to $key" }
            return StagedObject(s3Object = s3Object, partNumber = partNumber)
        }

        override suspend fun processBatch(batch: Batch): Batch {
            val stagedObject = batch as StagedObject
            val finalKey =
                pathFactory
                    .getPathToFile(stream, stagedObject.partNumber, isStaging = false)
                    .toString()
            log.info { "Moving staged object from ${stagedObject.s3Object.key} to $finalKey" }
            val newObject = s3Client.move(stagedObject.s3Object, finalKey)

            val state = destinationStateManager.getState(stream)
            state.removeObject(stream.generationId, stagedObject.s3Object.key)
            state.addObject(stream.generationId, newObject.key, stagedObject.partNumber)

            val finalizedObject = FinalizedObject(s3Object = newObject)
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
                        val newObject = s3Client.move(obj.key, newKey)
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
                        s3Client.delete(it.key)
                    }

                log.info { "Updating and persisting state" }
                state.dropGenerationsBefore(stream.minimumGenerationId)
                destinationStateManager.persistState(stream)
            }
        }
    }
}
