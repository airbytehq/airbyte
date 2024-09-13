/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.cdc.CdcPartitionReader
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicReference

private val ran: AtomicBoolean = AtomicBoolean(false)
class CdcPartitionCreator<
    A : CdcSharedState,
    >(val sharedState: A) : PartitionsCreator {
    private val acquiredResources = AtomicReference<AcquiredResources>()

    /** Calling [close] releases the resources acquired for the [JdbcPartitionsCreator]. */
    fun interface AcquiredResources : AutoCloseable

    override fun tryAcquireResources(): PartitionsCreator.TryAcquireResourcesStatus {
        return PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN
    }

    class MyCdcPartition(val state: CdcSharedState) : CdcPartition<CdcSharedState> {
        override val sharedState: CdcSharedState = state
    }
    override suspend fun run(): List<PartitionReader> {
        if (ran.get()) {
            return emptyList()
        }
        ran.set(true)
        val p = MyCdcPartition(sharedState)
        return listOf(CdcPartitionReader(p), )
        // TODO : Add logic to understand when debezium is done
        // TODO : Get schema history, target offset, if offset is invalid
    }

    override fun releaseResources() {
        //no-op
    }
}
