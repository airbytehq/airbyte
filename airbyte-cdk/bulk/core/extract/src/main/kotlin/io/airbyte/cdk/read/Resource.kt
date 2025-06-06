/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.output.sockets.SocketManager
import io.airbyte.cdk.output.sockets.SocketWrapper
import jakarta.inject.Inject
import jakarta.inject.Singleton
import kotlinx.coroutines.sync.Semaphore

/** [Resource] models a shared resource which can be acquired and released. */
interface Resource<T : Resource.Acquired> {

    /** [Acquired] is the acquired resource itself, released by calling [close]. */
    fun interface Acquired : AutoCloseable

    /** Attempts to acquire the resource. */
    fun tryAcquire(): T?

    val type: ResourceType
}

enum class ResourceType {
    RESOURCE_DB_CONNECTION,
    RESOURCE_OUTPUT_SOCKET,
}

@Singleton
class ResourceAcquirer(val acqs: List<Resource<Resource.Acquired>>) {
    fun tryAcquire(requested: List<ResourceType>): Map<ResourceType, Resource.Acquired>? {
        val acquired = mutableMapOf<ResourceType, Resource.Acquired>()
        run {
            requested.forEach { resourceType ->
                val res = acqs.first { acq -> acq.type == resourceType }.tryAcquire()
                res?.apply { acquired[resourceType] = this }
                    ?: return@run
            }
        }

        if (acquired.size != requested.size) {
            acquired.values.forEach { acq -> acq.close() }
            return null
        }
        return acquired
    }
}

/** A [Resource] used to manage concurrency. */
@Singleton
class ConcurrencyResource(maxConcurrency: Int) : Resource<ConcurrencyResource.AcquiredThread> {

    @Inject constructor(configuration: SourceConfiguration) : this(configuration.maxConcurrency)

    private val semaphore = Semaphore(maxConcurrency)

    val available: Int
        get() = semaphore.availablePermits

    fun interface AcquiredThread : Resource.Acquired

    override fun tryAcquire(): AcquiredThread? {
        if (!semaphore.tryAcquire()) return null
        return AcquiredThread { semaphore.release() }
    }

    override val type: ResourceType
        get() = ResourceType.RESOURCE_DB_CONNECTION
}

@Singleton
class SocketResource(val socketManager: SocketManager?) : Resource<SocketResource.AcquiredSocket> {

    class AcquiredSocket(val socketWrapper: SocketWrapper): Resource.Acquired {
        override fun close() {
            socketWrapper.unbindSocket()
        }
    }

    override fun tryAcquire(): AcquiredSocket? {
        val maybeSocket = socketManager?.bindFreeSocket()
        return maybeSocket?.let { AcquiredSocket(it) }

    }

    override val type: ResourceType
        get() = ResourceType.RESOURCE_OUTPUT_SOCKET
}
