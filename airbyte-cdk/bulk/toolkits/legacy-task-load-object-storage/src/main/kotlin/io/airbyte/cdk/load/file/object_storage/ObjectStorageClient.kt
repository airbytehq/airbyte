/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
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
    suspend fun delete(keys: Set<String>)

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

    /**
     * Aborts an in-progress upload, releasing any server-side state (e.g. an S3 multipart upload
     * initiated by [ObjectStorageClient.startStreamingUpload]).
     *
     * Should be called when no parts will be (or have been) uploaded and [complete] will not be
     * invoked, to avoid leaking dangling multipart uploads. Idempotent and safe to call after
     * [complete]; implementations should swallow non-fatal errors (such as the upload no longer
     * existing) and only log them.
     *
     * Default implementation is a no-op for backends that do not require explicit cancellation
     * (e.g. file-based or fully-buffered backends).
     */
    suspend fun abort() {
        // no-op by default
    }
}
