/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.output.sockets.SocketDataChannel
import io.airbyte.cdk.output.sockets.SocketDataChannelResourceHolder
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

/* ResourceAcquirer is a utility class that tries to acquire multiple resources of different types.
 * It returns a map of acquired resources if all requested resources are successfully acquired,
 * or null if any resource acquisition fails.
 */
@Singleton
class ResourceAcquirer(val acquierers: List<Resource<*>>) {
    @Inject
    constructor(
        cr: ConcurrencyResource,
        sr: SocketResource
    ) : this(
        listOf(
            cr,
            sr,
        )
    )

    fun tryAcquire(requested: List<ResourceType>): Map<ResourceType, Resource.Acquired>? {
        val acquired = mutableMapOf<ResourceType, Resource.Acquired>()
        // We need a run {} to be able to break out of the forEach loop if any resource acquisition
        // fails.
        run {
            requested.forEach { resourceType ->
                val res = acquierers.first { acq -> acq.type == resourceType }.tryAcquire()
                res?.apply { acquired[resourceType] = this } ?: return@run
            }
        }

        if (acquired.size != requested.size) {
            acquired.values.forEach { acq -> acq.close() }
            return null
        }
        return acquired
    }

    // convenience method to acquire a single resource of a specific type
    fun tryAcquireResource(requested: ResourceType): Resource.Acquired? {
        val acq: Map<ResourceType, Resource.Acquired>? = tryAcquire(listOf(requested))
        return acq?.get(requested)
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

/** A [Resource] representing a socket data channel. */
@Singleton
class SocketResource(val socketDataChannelResourceHolder: SocketDataChannelResourceHolder?) :
    Resource<SocketResource.AcquiredSocket> {

    class AcquiredSocket(val socketDatachannel: SocketDataChannel) : Resource.Acquired {
        // Release a socket resource unbinds it but does not close it.
        override fun close() {
            socketDatachannel.unbind()
        }
    }

    override fun tryAcquire(): AcquiredSocket? {
        val maybeSocket = socketDataChannelResourceHolder?.acquireSocketDataChannel()
        return maybeSocket?.let { AcquiredSocket(it) }
    }

    override val type: ResourceType
        get() = ResourceType.RESOURCE_OUTPUT_SOCKET
}
