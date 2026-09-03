/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import io.airbyte.cdk.load.pipeline.RoundRobinInputPartitioner
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton

/**
 * Object loader bean that activates the CDK's parallel upload pipeline. Tuning parameters come from
 * [GcsV2Configuration]. Part workers are forced to 1 for legacy file transfer.
 */
@Singleton
class GcsV2ObjectLoader(
    config: GcsV2Configuration<*>,
    @Value("\${airbyte.destination.core.file-transfer.enabled}") isLegacyFileTransfer: Boolean,
) : ObjectLoader {
    override val numPartWorkers: Int =
        if (isLegacyFileTransfer) {
            1
        } else {
            config.numPartWorkers
        }
    override val numUploadWorkers: Int = config.numUploadWorkers
    override val numUploadCompleters: Int = config.numUploadCompleters
    override val maxMemoryRatioReservedForParts: Double = config.maxMemoryRatioReservedForParts
    override val objectSizeBytes: Long = config.objectSizeBytes
    override val partSizeBytes: Long = config.partSizeBytes
}

@Singleton
@Requires(bean = GcsV2ObjectLoader::class)
class GcsV2RoundRobinInputPartitioner : RoundRobinInputPartitioner()
