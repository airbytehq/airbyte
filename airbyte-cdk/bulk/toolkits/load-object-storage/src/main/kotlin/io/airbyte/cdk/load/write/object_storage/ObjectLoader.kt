/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import io.airbyte.cdk.load.write.LoadStrategy

/**
 * [ObjectLoader] is for the use case where a destination writers records into some number of files
 * in a file system or cloud storage whose client supports streaming multipart uploads.
 */
interface ObjectLoader : LoadStrategy {
    val numPartWorkers: Int
    val numUploadWorkers: Int
    val maxMemoryRatioReservedForParts: Double
    val objectSizeBytes: Long
    val partSizeBytes: Long

    override val inputPartitions: Int
        get() = numPartWorkers
}
