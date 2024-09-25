/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionsCreator
import java.util.concurrent.atomic.AtomicReference

class CdcPartitionsCreator(
    val concurrencyResource: ConcurrencyResource,
    val cdcContext: CdcContext,
    val opaqueStateValue: OpaqueStateValue?
) : PartitionsCreator {
    private val acquiredThread = AtomicReference<ConcurrencyResource.AcquiredThread>()

    /** Calling [close] releases the resources acquired for the [JdbcPartitionsCreator]. */
    fun interface AcquiredResources : AutoCloseable

    override fun tryAcquireResources(): PartitionsCreator.TryAcquireResourcesStatus {
        val acquiredThread: ConcurrencyResource.AcquiredThread =
            concurrencyResource.tryAcquire()
                ?: return PartitionsCreator.TryAcquireResourcesStatus.RETRY_LATER
        this.acquiredThread.set(acquiredThread)
        return PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN
    }
    override suspend fun run(): List<PartitionReader> {
        // successful acquisition means that CDC is complete
        if (cdcContext.cdcGlobalLockResource.tryAcquire() != null) {
            // For the time being, only do one round
            return listOf()
        }
        return listOf(CdcPartitionReader(concurrencyResource, cdcContext, opaqueStateValue))
    }

    override fun releaseResources() {
        acquiredThread.getAndSet(null)?.close()
    }
}
