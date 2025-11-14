/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.load.command.DestinationStream
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

/**
 * Can be used by the dev connector to pass state between different parts of the connector. To use
 * it is sufficient to inject a StreamStateStore of any type into any component. The expected use is
 * for making state generated during initialization generally available to the Loaders.
 */
@Singleton
class StreamStateStore<S> {
    private val store = ConcurrentHashMap<DestinationStream.Descriptor, S>()

    fun put(stream: DestinationStream.Descriptor, state: S) {
        store[stream] = state
    }

    fun get(stream: DestinationStream.Descriptor): S? {
        return store[stream]
    }
}
