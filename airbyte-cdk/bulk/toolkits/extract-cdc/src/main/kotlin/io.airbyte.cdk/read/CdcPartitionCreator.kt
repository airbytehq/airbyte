/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.cdc.CdcPartitionReader
import java.util.concurrent.atomic.AtomicBoolean

private val ran: AtomicBoolean = AtomicBoolean(false)
class CdcPartitionCreator<
    A : JdbcSharedState,
    S : JdbcStreamState<A>,
    P : JdbcPartition<S>,
    >(val sharedState: A) : PartitionsCreator {
    override fun tryAcquireResources(): PartitionsCreator.TryAcquireResourcesStatus {
        return PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN
    }

    class MyCdcPartition(val state: JdbcSharedState) : CdcPartition<JdbcSharedState> {
        override val sharedState: JdbcSharedState = state
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
