/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.cdc.CdcPartitionReader

interface CdcSharedState {
    fun tryAcquireResourcesForCreator(): CdcPartitionCreator.AcquiredResources?

    fun tryAcquireResourcesForReader(): CdcPartitionReader.AcquiredResources?
}
