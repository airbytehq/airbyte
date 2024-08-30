/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

class CdcPartitionCreator : PartitionsCreator {
    override fun tryAcquireResources(): PartitionsCreator.TryAcquireResourcesStatus {
        TODO("Not yet implemented")
    }

    override suspend fun run(): List<PartitionReader> {
        TODO("Not yet implemented")
        // TODO : Add logic to understand when debezium is done
        // TODO : Get schema history, target offset, if offset is invalid
    }

    override fun releaseResources() {
        TODO("Not yet implemented")
    }
}
