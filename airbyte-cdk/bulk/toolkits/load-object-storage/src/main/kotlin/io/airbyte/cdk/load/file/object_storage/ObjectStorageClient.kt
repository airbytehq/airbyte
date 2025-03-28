/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.object_storage

import java.io.InputStream
import kotlinx.coroutines.flow.Flow

interface ObjectStorageClient<T : RemoteObject<*>> {
    suspend fun list(prefix: String): Flow<T>
    suspend fun move(remoteObject: T, toKey: String): T
    suspend fun move(key: String, toKey: String): T
    suspend fun <U> get(key: String, block: (InputStream) -> U): U
    suspend fun getMetadata(key: String): Map<String, String>
    suspend fun put(key: String, bytes: ByteArray): T
    suspend fun delete(remoteObject: T)
    suspend fun delete(key: String)

    /** Experimental sane replacement interface */
    suspend fun startStreamingUpload(
        key: String,
        metadata: Map<String, String> = emptyMap()
    ): StreamingUpload<T>
}

interface StreamingUpload<T : RemoteObject<*>> {
    /**
     * Uploads a part of the object. Each part must have a unique index. The parts do not need to be
     * uploaded in order. The index is 1-based.
     */
    suspend fun uploadPart(part: ByteArray, index: Int)

    /**
     * Completes a multipart upload. All parts must be uploaded before completing the upload, and
     * there cannot be gaps in the indexes. Idempotent, Multiple calls will return the same object,
     * but only the first call will have side effects.
     *
     * NOTE: If no parts were uploaded, it will skip the complete call but still return the object.
     * This is a temporary hack to support empty files.
     */
    suspend fun complete(): T
}
