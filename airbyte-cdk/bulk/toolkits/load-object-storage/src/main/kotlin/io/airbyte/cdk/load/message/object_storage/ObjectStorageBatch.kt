/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message.object_storage

import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.Batch

sealed interface ObjectStorageBatch : Batch

// An indexed bytearray containing an uploadable chunk of a file.
// Returned by the batch accumulator after processing records.
data class LoadablePart(val part: Part) : ObjectStorageBatch {
    override val groupId = null
    override val state = Batch.State.PROCESSED

    // Hide the data from the logs
    override fun toString(): String {
        return "LoadablePart(partIndex=${part.partIndex}, key=${part.key}, fileNumber=${part.fileNumber}, empty=${part.isEmpty})"
    }
}

// An UploadablePart that has been uploaded to an incomplete object.
// Returned by processBatch
data class IncompletePartialUpload(val key: String) : ObjectStorageBatch {
    override val state: Batch.State = Batch.State.STAGED
    override val groupId: String = key
}

// An UploadablePart that has triggered a completed upload.
data class LoadedObject<T : RemoteObject<*>>(
    val remoteObject: T,
    val fileNumber: Long,
    val isEmpty: Boolean
) : ObjectStorageBatch {
    override val state: Batch.State = Batch.State.COMPLETE
    override val groupId = remoteObject.key
}
