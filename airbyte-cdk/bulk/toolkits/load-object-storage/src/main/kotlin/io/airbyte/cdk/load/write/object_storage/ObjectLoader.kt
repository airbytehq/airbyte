/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.write.LoadStrategy

/**
 * [ObjectLoader] is for the use case where a destination writes records into some number of files
 * in a file system or cloud storage whose client supports streaming multipart uploads.
 *
 * [batchStateOnUpload] determines whether work is considered COMPLETE on upload (the default),
 * PERSISTED (not complete but recoverable and safe to ack to the platform), or STAGED/PROCESSED
 * (neither). Connector devs who are implementing file storage destinations should not need to
 * change this. It is for use internally by pipelines that compose object storage into more complex
 * workflows (ie, bulk load).
 *
 * CDK devs who are composing this into part of a larger strategy will probably also want to declare
 * a named object ["objectLoaderObjectQueue"] to pass the final uploaded object to another step (see
 * [io.airbyte.cdk.load.pipeline.object_storage.ObjectLoaderUploadStep]).
 */
interface ObjectLoader : LoadStrategy {
    val numPartWorkers: Int
    val numUploadWorkers: Int
    val maxMemoryRatioReservedForParts: Double
        get() = 0.2
    val objectSizeBytes: Long
    val partSizeBytes: Long

    val batchStateOnUpload: Batch.State
        get() = Batch.State.COMPLETE

    override val inputPartitions: Int
        get() = numPartWorkers
}
