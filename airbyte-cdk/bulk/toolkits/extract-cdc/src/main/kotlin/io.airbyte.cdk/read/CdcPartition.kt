/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

interface CdcPartition<S : JdbcSharedState> {
    val sharedState: S

    /** Tries to acquire resources for [JdbcPartitionReader]. */
    fun tryAcquireResourcesForReader(): JdbcPartitionReader.AcquiredResources? =
        // Acquire global resources by default.
        sharedState.tryAcquireResourcesForReader()
}
