/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.StreamLoader
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import kotlinx.coroutines.CompletableDeferred

sealed interface DestinationResult

data object DestinationSuccess : DestinationResult

data class DestinationFailure(
    val cause: Exception,
    val streamResults: Map<DestinationStream.Descriptor, StreamResult>
) : DestinationResult

@Singleton
@SuppressFBWarnings(
    "NP_NONNULL_PARAM_VIOLATION",
    justification = "exception is guaranteed to be non-null by Kotlin's type system"
)
class SyncManager(
    val catalog: DestinationCatalog,
    @Named("requireCheckpointIdOnRecordAndKeyOnState") requireCheckpointIndexOnState: Boolean
) {
    private val streamManagers: ConcurrentHashMap<DestinationStream.Descriptor, StreamManager> =
        ConcurrentHashMap(
            catalog.streams.associate {
                it.descriptor to StreamManager(it, requireCheckpointIndexOnState)
            }
        )

    private val destinationResult = CompletableDeferred<DestinationResult>()
    private val streamLoaders =
        ConcurrentHashMap<DestinationStream.Descriptor, CompletableDeferred<Result<StreamLoader>>>()
    private val inputConsumed = CompletableDeferred<Boolean>()
    private val checkpointsProcessed = CompletableDeferred<Boolean>()
    private val setupComplete = CompletableDeferred<Unit>()
    private val globalReadCount = ConcurrentHashMap<CheckpointId, Long>()

    /** Get the manager for the given stream. Throws an exception if the stream is not found. */
    fun getStreamManager(stream: DestinationStream.Descriptor): StreamManager {
        return streamManagers[stream] ?: throw IllegalArgumentException("Stream not found: $stream")
    }

    fun registerStartedStreamLoader(
        streamDescriptor: DestinationStream.Descriptor,
        streamLoaderResult: Result<StreamLoader>
    ) {
        streamLoaders
            .getOrPut(streamDescriptor) { CompletableDeferred() }
            .complete(streamLoaderResult)
    }

    suspend fun getOrAwaitStreamLoader(stream: DestinationStream.Descriptor): StreamLoader {
        return streamLoaders.getOrPut(stream) { CompletableDeferred() }.await().getOrThrow()
    }

    suspend fun getStreamLoaderOrNull(stream: DestinationStream.Descriptor): StreamLoader? {
        return streamLoaders[stream]?.await()?.getOrNull()
    }

    /**
     * Suspend until all streams are processed successfully. Returns false if processing failed for
     * any stream.
     */
    suspend fun awaitAllStreamsProcessedSuccessfully(): Boolean {
        return streamManagers.all { (_, manager) ->
            manager.awaitStreamResult() is StreamProcessingSucceeded
        }
    }

    suspend fun markDestinationFailed(causedBy: Exception): DestinationFailure {
        val result =
            DestinationFailure(causedBy, streamManagers.mapValues { it.value.awaitStreamResult() })
        destinationResult.complete(result)
        return result
    }

    suspend fun markDestinationSucceeded() {
        if (streamManagers.values.any { it.isActive() }) {
            throw IllegalStateException(
                "Cannot mark sync as succeeded until all streams are complete"
            )
        }
        destinationResult.complete(DestinationSuccess)
    }

    /**
     * Whether we received stream complete messages for all streams in the catalog from upstream.
     */
    suspend fun allStreamsComplete(): Boolean {
        return streamManagers.all { it.value.receivedStreamComplete() }
    }

    fun isActive(): Boolean {
        return destinationResult.isActive
    }

    suspend fun awaitDestinationResult(): DestinationResult {
        return destinationResult.await()
    }

    suspend fun awaitInputProcessingComplete() {
        inputConsumed.await()
        checkpointsProcessed.await()
    }

    suspend fun markInputConsumed() {
        val incompleteStreams =
            streamManagers
                .filter { (_, manager) -> !manager.endOfStreamRead() }
                .map { (stream, _) -> stream }
        if (incompleteStreams.isNotEmpty()) {
            val prettyStreams = incompleteStreams.map { it.toPrettyString() }
            throw TransientErrorException(
                "Input was fully read, but some streams did not receive a terminal stream status message. If the destination did not encounter other errors, this likely indicates an error in the source or platform. Streams without a status message: $prettyStreams"
            )
        }
        inputConsumed.complete(true)
    }

    suspend fun markCheckpointsProcessed() {
        checkpointsProcessed.complete(true)
    }

    suspend fun markSetupComplete() {
        setupComplete.complete(Unit)
    }

    suspend fun awaitSetupComplete() {
        setupComplete.await()
    }

    fun setGlobalReadCountForCheckpoint(checkpointId: CheckpointId, records: Long) {
        globalReadCount[checkpointId] = records
    }

    fun hasGlobalCount(checkpointId: CheckpointId): Boolean {
        return globalReadCount.containsKey(checkpointId)
    }

    fun areAllStreamsPersistedForGlobalCheckpoint(checkpointId: CheckpointId): Boolean {
        val readCount =
            globalReadCount[checkpointId]
                ?: throw IllegalStateException(
                    "Global read count for checkpoint $checkpointId is not set"
                )
        val persistedCount =
            streamManagers.values.sumOf { it.persistedRecordCountForCheckpoint(checkpointId) }
        return persistedCount == readCount
    }
}
