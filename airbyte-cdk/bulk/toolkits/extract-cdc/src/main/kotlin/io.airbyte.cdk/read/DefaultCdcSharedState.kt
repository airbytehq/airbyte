/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.cdc.CdcPartitionReader
import io.airbyte.cdk.command.SourceConfiguration
import kotlinx.coroutines.sync.Semaphore

class DefaultCdcSharedState(override val configuration: SourceConfiguration) : CdcSharedState {
    internal val semaphore = Semaphore(configuration.maxConcurrency)

    override fun tryAcquireResourcesForCreator(): CdcPartitionCreator.AcquiredResources? =
        if (semaphore.tryAcquire()) {
            CdcPartitionCreator.AcquiredResources { semaphore.release() }
        } else {
            null
        }

    override fun tryAcquireResourcesForReader(): CdcPartitionReader.AcquiredResources? =
        if (semaphore.tryAcquire()) {
            CdcPartitionReader.AcquiredResources { semaphore.release() }
        } else {
            null
        }
}
