/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.command.OpaqueStateValue
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicReference

private val ran: AtomicBoolean = AtomicBoolean(false)

class CdcPartitionCreator<
    A : CdcSharedState,
>(val sharedState: A, cdcContext: CdcContext, opaqueStateValue: OpaqueStateValue?) :
    PartitionsCreator, CdcAware {
    private val acquiredResources = AtomicReference<AcquiredResources>()
    val cdcContext = cdcContext
    val opaqueStateValue = opaqueStateValue

    override suspend fun run(): List<PartitionReader> {
        if (cdcReadyToRun().not()) {
            return emptyList()
        }

        return listOf(CdcPartitionReader(cdcContext, opaqueStateValue))
    }

    override fun releaseResources() {
        acquiredResources.getAndSet(null)?.close()
    }
}
