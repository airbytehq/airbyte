package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.read.JdbcNonResumablePartitionReader
import io.airbyte.cdk.read.JdbcPartition
import io.airbyte.cdk.read.JdbcResumablePartitionReader
import io.airbyte.cdk.read.JdbcSplittablePartition
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.CdcAware

class CdcAwareJdbcNonResumablePartitionReader<P : JdbcPartition<*>>(
    partition: P,
) : JdbcNonResumablePartitionReader<P>(partition), CdcAware {

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        if (!cdcReadyToRun()) {
            return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
        }
        return super.tryAcquireResources()
    }
}

class CdcAwareJdbcResumablePartitionReader<P : JdbcSplittablePartition<*>>(
    partition: P,
) : JdbcResumablePartitionReader<P>(partition), CdcAware {

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        if (cdcDoneRunning().not()) {
            return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
        }
        return super.tryAcquireResources()
    }
}
