/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.command.SourceConfiguration
import jakarta.inject.Singleton
import kotlinx.coroutines.sync.Semaphore

fun interface Resource<T : Resource.Acquired> {
    fun interface Acquired : AutoCloseable
    fun tryAcquire(): T?
}

@Singleton
class ConcurrencyResource(val config: SourceConfiguration) :
    Resource<ConcurrencyResource.AcquiredThread> {

    private val semaphore = Semaphore(config.maxConcurrency)

    val available: Int
        get() = semaphore.availablePermits

    fun interface AcquiredThread : Resource.Acquired

    override fun tryAcquire(): AcquiredThread? {
        if (!semaphore.tryAcquire()) return null
        return AcquiredThread { semaphore.release() }
    }
}
