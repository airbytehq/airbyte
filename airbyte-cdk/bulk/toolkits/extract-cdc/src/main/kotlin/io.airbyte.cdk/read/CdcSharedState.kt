package io.airbyte.cdk.read

import io.airbyte.cdk.cdc.CdcPartitionReader
import io.airbyte.cdk.command.SourceConfiguration

interface CdcSharedState {
    val configuration: SourceConfiguration

    fun tryAcquireResourcesForCreator(): CdcPartitionCreator.AcquiredResources?

    fun tryAcquireResourcesForReader(): CdcPartitionReader.AcquiredResources?
}
