/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.cdc.CdcPartitionReader
import io.airbyte.cdk.command.OpaqueStateValue
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicReference

private val ran: AtomicBoolean = AtomicBoolean(false)

class CdcPartitionCreator<
    A : CdcSharedState,
>(val sharedState: A, cdcContext: CdcContext, opaqueStateValue: OpaqueStateValue?) :
    PartitionsCreator {
    private val acquiredResources = AtomicReference<AcquiredResources>()
    val cdcContext = cdcContext
    val opaqueStateValue = opaqueStateValue

    /** Calling [close] releases the resources acquired for the [JdbcPartitionsCreator]. */
    fun interface AcquiredResources : AutoCloseable

    override fun tryAcquireResources(): PartitionsCreator.TryAcquireResourcesStatus {
        val acquiredResources: AcquiredResources =
            sharedState.tryAcquireResourcesForCreator()
                ?: return PartitionsCreator.TryAcquireResourcesStatus.RETRY_LATER
        this.acquiredResources.set(acquiredResources)
        return PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run(): List<PartitionReader> {
        return listOf(CdcPartitionReader(cdcContext, opaqueStateValue))
    }

    override fun releaseResources() {
        acquiredResources.getAndSet(null)?.close()
    }
}
