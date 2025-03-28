/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import io.airbyte.cdk.load.file.azureBlobStorage.GENERATION_ID_METADATA_KEY_OVERRIDE
import io.airbyte.cdk.load.pipeline.RoundRobinInputPartitioner
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import javax.inject.Singleton

@Singleton
class AzureBlobStorageObjectLoader(config: AzureBlobStorageConfiguration<*>) : ObjectLoader {
    override val generationIdMetadataKeyOverride: String
        get() = GENERATION_ID_METADATA_KEY_OVERRIDE

    override val numPartWorkers: Int = config.numPartWorkers
    override val numUploadWorkers: Int = config.numUploadWorkers
    override val maxMemoryRatioReservedForParts: Double = config.maxMemoryRatioReservedForParts
    override val objectSizeBytes: Long = config.objectSizeBytes
    override val partSizeBytes: Long = config.partSizeBytes
}

@Singleton class AzureRoundRobinInputPartitioner : RoundRobinInputPartitioner()
