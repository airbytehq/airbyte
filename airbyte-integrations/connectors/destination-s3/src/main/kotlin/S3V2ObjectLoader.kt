/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.pipeline.RoundRobinInputPartitioner
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton

@Singleton
class S3V2ObjectLoader(
    config: S3V2Configuration<*>,
    @Value("\${airbyte.destination.core.file-transfer.enabled}") isLegacyFileTransfer: Boolean
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

@Singleton
@Requires(bean = S3V2ObjectLoader::class)
class S3V2RoundRobinInputPartitioner : RoundRobinInputPartitioner()
