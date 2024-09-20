/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.cdc.CdcPartitionReader
import io.airbyte.cdk.read.CdcPartitionCreator
import io.airbyte.cdk.read.CdcSharedState
import io.airbyte.cdk.read.JdbcPartitionReader
import io.airbyte.cdk.read.JdbcPartitionsCreator
import io.airbyte.cdk.read.JdbcSharedState

fun JdbcSharedState.toCdcSharedState(): CdcSharedState =
    object : CdcSharedState {
        override fun tryAcquireResourcesForCreator(): CdcPartitionCreator.AcquiredResources? =
            this@toCdcSharedState.tryAcquireResourcesForCreator()
                ?.toCdcPartitionCreatorAcquiredResources()

        override fun tryAcquireResourcesForReader(): CdcPartitionReader.AcquiredResources? =
            this@toCdcSharedState.tryAcquireResourcesForReader()
                ?.toCdcPartitionReaderAcquiredResources()
    }

fun JdbcPartitionsCreator.AcquiredResources.toCdcPartitionCreatorAcquiredResources():
    CdcPartitionCreator.AcquiredResources {
    return object : CdcPartitionCreator.AcquiredResources {
        override fun close() {
            this@toCdcPartitionCreatorAcquiredResources.close()
        }
    }
}

fun JdbcPartitionReader.AcquiredResources.toCdcPartitionReaderAcquiredResources():
    CdcPartitionReader.AcquiredResources {
    return object : CdcPartitionReader.AcquiredResources {
        override fun close() {
            this@toCdcPartitionReaderAcquiredResources.close()
        }
    }
}
