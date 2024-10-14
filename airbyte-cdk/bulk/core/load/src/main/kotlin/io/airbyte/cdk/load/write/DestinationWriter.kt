/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.SyncFailure
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import kotlinx.coroutines.CompletableDeferred

/**
 * Implementor interface. Every Destination must extend this and at least provide an implementation
 * of [createStreamLoader].
 */
interface DestinationWriter<B> {
    // Called once before anything else
    suspend fun setup() {}

    // Return a StreamLoader for the given stream
    fun createStreamLoader(stream: DestinationStream): StreamLoader<B>

    // Called once at the end of the job, unconditionally.
    // NOTE: we don't pass Success here, because it depends on this completing successfully.
    suspend fun teardown(syncFailure: SyncFailure? = null) {}
}

@Singleton
@Secondary
class DefaultDestinationWriter : DestinationWriter<Unit> {
    init {
        throw NotImplementedError(
            "DestinationWrite not implemented. Please create a custom @Singleton implementation."
        )
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader<Unit> {
        throw NotImplementedError()
    }
}

@Singleton
class DestinationWriterInternal<B>(
    private val destinationWriter: DestinationWriter<B>
) {
    private val streamLoaders = ConcurrentHashMap<DestinationStream, CompletableDeferred<StreamLoader<B>>>()

    suspend fun getOrCreateStreamLoader(stream: DestinationStream): StreamLoader<B> {
        return streamLoaders.getOrPut(stream) {
            CompletableDeferred<StreamLoader<B>>().also { deferred ->
                deferred.complete(destinationWriter.createStreamLoader(stream))
            }
        }.await()
    }

    suspend fun awaitStreamLoader(stream: DestinationStream): StreamLoader<B> {
        return streamLoaders.getOrPut(stream) {
            CompletableDeferred()
        }.await()
    }
}
