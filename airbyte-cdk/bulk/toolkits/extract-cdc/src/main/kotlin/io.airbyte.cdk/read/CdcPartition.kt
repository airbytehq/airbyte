/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.cdc.CdcPartitionReader

interface CdcPartition<S : CdcSharedState> {
    val sharedState: S

    /** Tries to acquire resources for [CdcPartitionReader]. */
    fun tryAcquireResourcesForReader(): CdcPartitionReader.AcquiredResources? =
        // Acquire global resources by default.
        sharedState.tryAcquireResourcesForReader()
}
