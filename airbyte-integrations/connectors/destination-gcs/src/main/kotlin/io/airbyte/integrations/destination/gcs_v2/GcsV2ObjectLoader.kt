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
 * Mirror of S3V2ObjectLoader. Its mere presence as an [ObjectLoader] @Singleton is what activates
 * the generic ObjectLoaderPipeline (@Requires(bean = ObjectLoader::class)) — this is the whole
 * "fast" mechanism (3-stage part-format / part-load / upload-complete pipeline with a
 * memory-reserving back-pressured queue). Tuning knobs come from [GcsV2Configuration].
 * numPartWorkers is forced to 1 under legacy file transfer, identical to S3.
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
