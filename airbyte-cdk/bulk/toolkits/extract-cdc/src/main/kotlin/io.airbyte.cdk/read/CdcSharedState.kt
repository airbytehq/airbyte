/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.cdc.CdcPartitionReader
import io.airbyte.cdk.command.SourceConfiguration

interface CdcSharedState {
    val configuration: SourceConfiguration

    fun tryAcquireResourcesForCreator(): CdcPartitionCreator.AcquiredResources?

    fun tryAcquireResourcesForReader(): CdcPartitionReader.AcquiredResources?
}
