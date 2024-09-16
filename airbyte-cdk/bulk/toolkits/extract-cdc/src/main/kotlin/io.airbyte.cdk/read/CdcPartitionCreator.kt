/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.cdc.CdcPartitionReader
import java.util.concurrent.atomic.AtomicReference

class CdcPartitionCreator<A : CdcSharedState>(val sharedState: A) : PartitionsCreator, CdcAware {
    private val acquiredResources = AtomicReference<AcquiredResources>()

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
        if (cdcReadyToRun().not()) {
            return emptyList()
        }
        return listOf(CdcPartitionReader(sharedState))
        // TODO : Add logic to understand when debezium is done
        // TODO : Get schema history, target offset, if offset is invalid
    }

    override fun releaseResources() {
        acquiredResources.getAndSet(null)?.close()
    }
}
