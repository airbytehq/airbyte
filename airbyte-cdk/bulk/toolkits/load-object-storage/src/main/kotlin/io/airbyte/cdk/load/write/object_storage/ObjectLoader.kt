/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import io.airbyte.cdk.load.message.Batch
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
 * - [maxMemoryRatioReservedForParts] is proportion of the total heap reserved for parts in memory.
 * This is used to calculate the size of the work queue, which when full will cause the part workers
 * to suspend until the upload workers have processed some parts.
 * - [partSizeBytes] is the approximate desired part size in bytes. When this much part data has
 * been accumulated by a part worker, it will be forwarded to an upload worker and uploaded to the
 * destination.
 * - [objectSizeBytes] is the approximate desired file size in bytes. When this much part data has
 * been accumulated, the upload will be completed, and the file will become visible to the end user.
 * - [batchStateOnUpload] determines whether work is considered COMPLETE on upload (the default),
 * PERSISTED (not complete but recoverable and safe to ack to the platform), or STAGED/PROCESSED
 * (neither). Connector devs who are implementing file storage destinations should not need to
 * change this. It is for use internally by pipelines that compose object storage into more complex
 * workflows (ie, bulk load).
 *
 * Partitioning:
 *
 * The default partitioning is to distribute the records round-robin (in small batches) to the part
 * workers (using [io.airbyte.cdk.load.pipeline.RoundRobinInputPartitioner]). To override this,
 * declare a bean implementing [io.airbyte.cdk.load.pipeline.InputPartitioner], however it should be
 * fine for most purposes.
 *
 * The parts are also distributed round-robin to the upload workers using
 * [io.airbyte.cdk.load.pipeline.object_storage.ObjectLoaderPartPartitioner]. This is not currently
 * configurable.
 *
 * Post-processing:
 *
 * If a connector dev implements this interface directly, there will by default be no
 * post-processing of individual files (except what is done when the stream is closed).
 *
 * However, CDK devs who are composing this into part of a larger strategy will probably also want
 * to declare a named object ["objectLoaderObjectQueue"] to pass the final uploaded object to
 * another step (see [io.airbyte.cdk.load.pipeline.object_storage.ObjectLoaderUploadStep]).
 */
interface ObjectLoader : LoadStrategy {
    val numPartWorkers: Int
        get() = 1
    val numUploadWorkers: Int
        get() = 5
    val maxMemoryRatioReservedForParts: Double
        get() = 0.2
    val partSizeBytes: Long
        get() = 10L * 1024 * 1024
    val objectSizeBytes: Long
        get() = 200L * 1024 * 1024

    val batchStateOnUpload: Batch.State
        get() = Batch.State.COMPLETE
    override val inputPartitions: Int
        get() = numPartWorkers
}
