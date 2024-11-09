/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.StreamLoader
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import kotlinx.coroutines.CompletableDeferred

sealed interface SyncResult

data object SyncSuccess : SyncResult

data class SyncFailure(
    val syncFailure: Exception,
    val streamResults: Map<DestinationStream.Descriptor, StreamResult>
) : SyncResult

/** Manages the state of all streams in the destination. */
interface SyncManager {
    /** Get the manager for the given stream. Throws an exception if the stream is not found. */
    fun getStreamManager(stream: DestinationStream.Descriptor): StreamManager

    fun registerStartedStreamLoader(streamLoader: StreamLoader)
    suspend fun getOrAwaitStreamLoader(stream: DestinationStream.Descriptor): StreamLoader
    suspend fun getStreamLoaderOrNull(stream: DestinationStream.Descriptor): StreamLoader?

    /** Suspend until all streams are complete. Returns false if any stream was failed/killed. */
    suspend fun awaitAllStreamsCompletedSuccessfully(): Boolean

    suspend fun markInputConsumed()
    suspend fun markCheckpointsProcessed()
    suspend fun markFailed(causedBy: Exception): SyncFailure
    suspend fun markSucceeded()

    fun isActive(): Boolean

    suspend fun awaitInputProcessingComplete(): Unit
    suspend fun awaitSyncResult(): SyncResult
}

@SuppressFBWarnings(
    "NP_NONNULL_PARAM_VIOLATION",
    justification = "exception is guaranteed to be non-null by Kotlin's type system"
)
class DefaultSyncManager(
    private val streamManagers: ConcurrentHashMap<DestinationStream.Descriptor, StreamManager>
) : SyncManager {
    private val syncResult = CompletableDeferred<SyncResult>()
    private val streamLoaders =
        ConcurrentHashMap<DestinationStream.Descriptor, CompletableDeferred<StreamLoader>>()
    private val inputConsumed = CompletableDeferred<Boolean>()
    private val checkpointsProcessed = CompletableDeferred<Boolean>()

    override fun getStreamManager(stream: DestinationStream.Descriptor): StreamManager {
        return streamManagers[stream] ?: throw IllegalArgumentException("Stream not found: $stream")
    }

    override fun registerStartedStreamLoader(streamLoader: StreamLoader) {
        streamLoaders
            .getOrPut(streamLoader.stream.descriptor) { CompletableDeferred() }
            .complete(streamLoader)
    }

    override suspend fun getOrAwaitStreamLoader(
        stream: DestinationStream.Descriptor
    ): StreamLoader {
        return streamLoaders.getOrPut(stream) { CompletableDeferred() }.await()
    }

    override suspend fun getStreamLoaderOrNull(
        stream: DestinationStream.Descriptor
    ): StreamLoader? {
        val completable = streamLoaders[stream]
        return completable?.let { if (it.isCompleted) it.await() else null }
    }

    override suspend fun awaitAllStreamsCompletedSuccessfully(): Boolean {
        return streamManagers.all { (_, manager) -> manager.awaitStreamResult() is StreamSucceeded }
    }

    override suspend fun markFailed(causedBy: Exception): SyncFailure {
        val result =
            SyncFailure(causedBy, streamManagers.mapValues { it.value.awaitStreamResult() })
        syncResult.complete(result)
        return result
    }

    override suspend fun markSucceeded() {
        if (streamManagers.values.any { it.isActive() }) {
            throw IllegalStateException(
                "Cannot mark sync as succeeded until all streams are complete"
            )
        }
        syncResult.complete(SyncSuccess)
    }

    override fun isActive(): Boolean {
        return syncResult.isActive
    }

    override suspend fun awaitSyncResult(): SyncResult {
        return syncResult.await()
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
            throw IllegalStateException(
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
