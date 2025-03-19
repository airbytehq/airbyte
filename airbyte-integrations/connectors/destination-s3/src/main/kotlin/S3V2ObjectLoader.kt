/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.pipeline.RoundRobinInputPartitioner
import io.airbyte.cdk.load.write.object_storage.ObjectLoader

/**
 * These are temporarily disabled so that we can merge the underlying changes without doing a full
 * S3 release. I will do a separate PR to re-enable this and roll it out gradually.
 */
// @Singleton
class S3V2ObjectLoader(config: S3V2Configuration<*>) : ObjectLoader {
    override val numPartWorkers: Int = config.numPartWorkers
    override val numUploadWorkers: Int = config.numUploadWorkers
    override val maxMemoryRatioReservedForParts: Double = config.maxMemoryRatioReservedForParts
    override val objectSizeBytes: Long = config.objectSizeBytes
    override val partSizeBytes: Long = config.partSizeBytes
}

// @Singleton
class S3V2RoundRobinInputPartitioner : RoundRobinInputPartitioner()
