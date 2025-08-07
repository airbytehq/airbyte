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
    private val config: AzureBlobStorageConfiguration<*>
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
    override fun socketPartSizeBytes(numberOfSockets: Int): Long {
        return config.azureBlobStorageClientConfiguration.partSize!! * 1024L * 1024L
        //        return min((numberOfSockets * 4), 32) * 1024L * 1024
    }

    override fun socketUploadParallelism(numberOfSockets: Int): Int {
        return config.azureBlobStorageClientConfiguration.numUploaders!!
        //        return min((numberOfSockets * 4), 16)
    }
}

@Requires(property = "airbyte.destination.core.file-transfer.enabled", value = "false")
@Singleton
class AzureRoundRobinInputPartitioner : RoundRobinInputPartitioner()
