/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import io.airbyte.cdk.load.write.LoadStrategy

/**
 * [ObjectLoader] is for the use case where a destination writes records into some number of files
 * in a file system or cloud storage provider whose client supports multipart uploads.
 *
 * Usage:
 *
 * - declare a bean implementing this interface and optionally override the default configuration
 * values
 * - declare the necessary beans to initialize an
 * [io.airbyte.cdk.load.file.object_storage.ObjectStorageClient]
 * - declare a bean of
 * [io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider] to configure
 * the path for each object (typically you would add this to your
 * [io.airbyte.cdk.load.command.DestinationConfiguration])
 * - declare a bean of
 * [io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider] to control
 * the format in which the data is loaded
 *
 * Configuration:
 *
 * - [numPartWorkers] is the number of threads (coroutines) devoted to formatting records into
 * uploadable parts. (This is typically CPU-bound).
 * - [numUploadWorkers] is the number of threads (coroutines) devoted to uploading parts to the
 * object storage. (This is typically Network IO-bound).
 * - [numUploadCompleters] in practice is simpler and more efficient to complete the uploads async
 * than to try to have the loaders coordinate to determine when all parts are done. This is the
 * number of workers devoted to that task. In practice there's very little to gain here. Two is a
 * good number.
 * - [maxMemoryRatioReservedForParts] is proportion of the total heap reserved for parts in memory.
 * This is used to calculate the size of the work queue, which when full will cause the part workers
 * to suspend until the upload workers have processed some parts.
 * - [partSizeBytes] is the desired approximate part size in bytes. When this much part data has
 * been accumulated by a part worker, it will be forwarded to an upload worker and uploaded to the
 * destination. 10MB is a good default. Try up to 50 when tuning, but be aware of memory
 * requirements.
 * - [objectSizeBytes] is the desired approximate file size in bytes. When this much part data has
 * been accumulated, the upload will be completed, and the file will become visible to the end user.
 *
 * Partitioning:
 *
 * The default partitioning is to distribute the records round-robin (in small batches) to the part
 * workers (using [io.airbyte.cdk.load.pipeline.RoundRobinInputPartitioner]). To override this,
 * declare a bean implementing [io.airbyte.cdk.load.pipeline.InputPartitioner], however it should be
 * fine for most purposes.
 *
 * The parts are distributed evenly across the loading and completing workers w/o regard to object
 * key or stream. This is currently not configurable, but tests have shown it is optimal.
 */
interface ObjectLoader : LoadStrategy {
    val numPartWorkers: Int
        get() = 2
    val numUploadWorkers: Int
        get() = 5
    val numUploadCompleters: Int
        get() = 1
    val maxMemoryRatioReservedForParts: Double
        get() = 0.2
    val partSizeBytes: Long
        get() = 10L * 1024 * 1024
    val objectSizeBytes: Long
        get() = 200L * 1024 * 1024

    override val inputPartitions: Int
        get() = numPartWorkers
}
