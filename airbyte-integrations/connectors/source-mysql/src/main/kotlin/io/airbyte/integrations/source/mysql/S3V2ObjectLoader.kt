/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.load.pipeline.RoundRobinInputPartitioner
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import jakarta.inject.Singleton

/**
 * These are temporarily disabled so that we can merge the underlying changes without doing a full
 * S3 release. I will do a separate PR to re-enable this and roll it out gradually.
 */
@Singleton
class S3V2ObjectLoader(
    config: MySqlSourceConfiguration<*>,
) : ObjectLoader {
    override val numPartWorkers: Int = config.numThreads
    override val numUploadWorkers: Int = config.numUploadWorkers
    override val maxMemoryRatioReservedForParts: Double = config.maxMemoryRatioReservedForParts
    override val objectSizeBytes: Long = config.objectSizeBytes
    override val partSizeBytes: Long = config.partSizeBytes
}

// @Singleton
class S3V2RoundRobinInputPartitioner : RoundRobinInputPartitioner()
