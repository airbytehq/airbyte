/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import io.airbyte.cdk.load.pipeline.RoundRobinInputPartitioner
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import javax.inject.Singleton

@Singleton
class AzureBlobStorageObjectLoader(
    @Value("\${airbyte.destination.core.file-transfer.enabled}") isLegacyFileTransfer: Boolean,
    config: AzureBlobStorageConfiguration<*>
) : ObjectLoader {
    override val numPartWorkers: Int =
        if (isLegacyFileTransfer) {
            1
        } else {
            config.numPartWorkers
        }
    override val numUploadWorkers: Int = config.numUploadWorkers
    override val maxMemoryRatioReservedForParts: Double = config.maxMemoryRatioReservedForParts
    override val objectSizeBytes: Long = config.objectSizeBytes
    override val partSizeBytes: Long = config.partSizeBytes
}

@Requires(property = "airbyte.destination.core.file-transfer.enabled", value = "false")
@Singleton
class AzureRoundRobinInputPartitioner : RoundRobinInputPartitioner()
