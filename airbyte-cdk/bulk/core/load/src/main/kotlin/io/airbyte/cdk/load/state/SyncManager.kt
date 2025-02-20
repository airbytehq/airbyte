/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.StreamLoader
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import kotlinx.coroutines.CompletableDeferred

sealed interface DestinationResult

data object DestinationSuccess : DestinationResult

data class DestinationFailure(
    val cause: Exception,
    val streamResults: Map<DestinationStream.Descriptor, StreamResult>
) : DestinationResult

/** Manages the state of all streams in the destination. */
interface SyncManager {
    /** Get the manager for the given stream. Throws an exception if the stream is not found. */
    fun getStreamManager(stream: DestinationStream.Descriptor): StreamManager

    fun registerStartedStreamLoader(
        streamDescriptor: DestinationStream.Descriptor,
        streamLoaderResult: Result<StreamLoader>
    )
    suspend fun getOrAwaitStreamLoader(stream: DestinationStream.Descriptor): StreamLoader
    suspend fun getStreamLoaderOrNull(stream: DestinationStream.Descriptor): StreamLoader?

    /**
     * Suspend until all streams are processed successfully. Returns false if processing failed for
     * any stream.
     */
    suspend fun awaitAllStreamsProcessedSuccessfully(): Boolean

    suspend fun markInputConsumed()
    suspend fun markCheckpointsProcessed()
    suspend fun markDestinationFailed(causedBy: Exception): DestinationFailure
    suspend fun markDestinationSucceeded()

    /**
     * Whether we received stream complete messages for all streams in the catalog from upstream.
     */
    suspend fun allStreamsComplete(): Boolean

    fun isActive(): Boolean

    suspend fun awaitInputProcessingComplete()
    suspend fun awaitDestinationResult(): DestinationResult
}

@SuppressFBWarnings(
    "NP_NONNULL_PARAM_VIOLATION",
    justification = "exception is guaranteed to be non-null by Kotlin's type system"
)
class DefaultSyncManager(
    private val streamManagers: ConcurrentHashMap<DestinationStream.Descriptor, StreamManager>
) : SyncManager {
    private val destinationResult = CompletableDeferred<DestinationResult>()
    private val streamLoaders =
        ConcurrentHashMap<DestinationStream.Descriptor, CompletableDeferred<Result<StreamLoader>>>()
    private val inputConsumed = CompletableDeferred<Boolean>()
    private val checkpointsProcessed = CompletableDeferred<Boolean>()

    override fun getStreamManager(stream: DestinationStream.Descriptor): StreamManager {
        return streamManagers[stream] ?: throw IllegalArgumentException("Stream not found: $stream")
    }

    override fun registerStartedStreamLoader(
        streamDescriptor: DestinationStream.Descriptor,
        streamLoaderResult: Result<StreamLoader>
    ) {
        streamLoaders
            .getOrPut(streamDescriptor) { CompletableDeferred() }
            .complete(streamLoaderResult)
    }

    override suspend fun getOrAwaitStreamLoader(
        stream: DestinationStream.Descriptor
    ): StreamLoader {
        return streamLoaders.getOrPut(stream) { CompletableDeferred() }.await().getOrThrow()
    }

    override suspend fun getStreamLoaderOrNull(
        stream: DestinationStream.Descriptor
    ): StreamLoader? {
        return streamLoaders[stream]?.await()?.getOrNull()
    }

    override suspend fun awaitAllStreamsProcessedSuccessfully(): Boolean {
        return streamManagers.all { (_, manager) ->
            manager.awaitStreamResult() is StreamProcessingSucceeded
        }
    }

    override suspend fun markDestinationFailed(causedBy: Exception): DestinationFailure {
        val result =
            DestinationFailure(causedBy, streamManagers.mapValues { it.value.awaitStreamResult() })
        destinationResult.complete(result)
        return result
    }

    override suspend fun markDestinationSucceeded() {
        if (streamManagers.values.any { it.isActive() }) {
            throw IllegalStateException(
                "Cannot mark sync as succeeded until all streams are complete"
            )
        }
        destinationResult.complete(DestinationSuccess)
    }

    override suspend fun allStreamsComplete(): Boolean {
        return streamManagers.all { it.value.isComplete() }
    }

    override fun isActive(): Boolean {
        return destinationResult.isActive
    }

    override suspend fun awaitDestinationResult(): DestinationResult {
        return destinationResult.await()
    }

    override suspend fun awaitInputProcessingComplete() {
        inputConsumed.await()
        checkpointsProcessed.await()
    }

    override suspend fun markInputConsumed() {
        val incompleteStreams =
            streamManagers
                .filter { (_, manager) -> !manager.endOfStreamRead() }
                .map { (stream, _) -> stream }
        if (incompleteStreams.isNotEmpty()) {
            val prettyStreams = incompleteStreams.map { it.toPrettyString() }
            throw TransientErrorException(
                "Input was fully read, but some streams did not receive a terminal stream status message. This likely indicates an error in the source or platform. Streams without a status message: $prettyStreams"
            )
        }
        inputConsumed.complete(true)
    }

    override suspend fun markCheckpointsProcessed() {
        checkpointsProcessed.complete(true)
    }
}

@Factory
class SyncManagerFactory(
    private val catalog: DestinationCatalog,
    private val streamManagerFactory: StreamManagerFactory
) {
    @Singleton
    @Secondary
    fun make(): SyncManager {
        val hashMap = ConcurrentHashMap<DestinationStream.Descriptor, StreamManager>()
        catalog.streams.forEach { hashMap[it.descriptor] = streamManagerFactory.create(it) }
        return DefaultSyncManager(hashMap)
    }
}
