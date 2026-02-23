/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.load.command.DestinationStream
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

/**
 * A singleton registry that maps stream descriptors to their [StreamLoader] instances. Populated
 * during stream initialization in [DestinationLifecycle] and used by the pipeline to invoke
 * per-stream lifecycle callbacks such as [StreamLoader.onStreamFlushed].
 */
@Singleton
class StreamLoaderStore {
    private val store = ConcurrentHashMap<DestinationStream.Descriptor, StreamLoader>()

    fun put(descriptor: DestinationStream.Descriptor, loader: StreamLoader) {
        store[descriptor] = loader
    }

    fun get(descriptor: DestinationStream.Descriptor): StreamLoader? = store[descriptor]

    fun getAll(): Collection<StreamLoader> = store.values
}
