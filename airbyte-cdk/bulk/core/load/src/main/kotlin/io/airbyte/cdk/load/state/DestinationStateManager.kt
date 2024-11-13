/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

interface DestinationState

interface DestinationStateManager<T : DestinationState> {
    suspend fun getState(stream: DestinationStream): T
    suspend fun persistState(stream: DestinationStream)
}

@SuppressFBWarnings(
    "NP_NONNULL_PARAM_VIOLATION",
    justification = "state is guaranteed to be non-null by Kotlin's type system"
)
@Singleton
@Secondary
class DefaultDestinationStateManager<T : DestinationState>(
    private val persister: DestinationStatePersister<T>,
) : DestinationStateManager<T> {
    private val states: ConcurrentHashMap<DestinationStream.Descriptor, T> = ConcurrentHashMap()

    override suspend fun getState(stream: DestinationStream): T {
        return states.getOrPut(stream.descriptor) { persister.load(stream) }
    }

    override suspend fun persistState(stream: DestinationStream) {
        val state =
            states[stream.descriptor]
                ?: throw IllegalStateException("State not found for stream $stream")
        persister.persist(stream, state)
    }
}

interface DestinationStatePersister<T : DestinationState> {
    suspend fun load(stream: DestinationStream): T
    suspend fun persist(stream: DestinationStream, state: T)
}
