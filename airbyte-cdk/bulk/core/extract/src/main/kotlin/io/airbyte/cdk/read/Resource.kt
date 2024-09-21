/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.command.SourceConfiguration
import io.micronaut.context.annotation.DefaultImplementation
import jakarta.inject.Singleton
import kotlinx.coroutines.sync.Semaphore

/** [Resource] models a shared resource which can be acquired and released. */
fun interface Resource<T : Resource.Acquired> {

    /** [Acquired] is the acquired resource itself, released by calling [close]. */
    fun interface Acquired : AutoCloseable

    /** Attempts to acquire the resource. */
    fun tryAcquire(): T?
}

@Singleton
/** A [Resource] used to manage concurrency. */
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

@DefaultImplementation(NoOpGlobalLockResource::class)
/** A [Resource] used to synchronize operations such as CDC. Defaults to a no-op implementation. */
fun interface GlobalLockResource : Resource<GlobalLockResource.AcquiredGlobalLock> {
    fun interface AcquiredGlobalLock : Resource.Acquired
}

@Singleton
class NoOpGlobalLockResource : GlobalLockResource {

    override fun tryAcquire(): GlobalLockResource.AcquiredGlobalLock {
        // Always acquire.
        return GlobalLockResource.AcquiredGlobalLock {}
    }
}
