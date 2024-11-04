/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.object_storage

import io.airbyte.cdk.load.file.StreamProcessor
import java.io.InputStream
import java.io.OutputStream
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

    /**
     * Streaming upload should provide an [OutputStream] managed within the lifecycle of [block].
     * The stream should be closed after the block completes, however it should be safe for users of
     * the stream to close early (some writers do this by default, especially those that write whole
     * files). Specifically, the method should guarantee that no operations will be performed on the
     * stream after [block] completes.
     */
    suspend fun <V : OutputStream> streamingUpload(
        key: String,
        metadata: Map<String, String> = emptyMap(),
        streamProcessor: StreamProcessor<V>? = null,
        block: suspend (OutputStream) -> Unit
    ): T
}
