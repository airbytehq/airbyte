/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.cdc

import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader

class CdcPartitionReader() : PartitionReader {
    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        TODO("Not yet implemented")
        // Acquire global lock
    }

    override suspend fun run() {
        TODO("Not yet implemented")
    }

    override fun checkpoint(): PartitionReadCheckpoint {
        TODO("Not yet implemented")
    }

    override fun releaseResources() {
        TODO("Not yet implemented")
        // Release global CDC lock
    }
}
