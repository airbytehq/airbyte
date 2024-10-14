/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

interface ObjectStorageClient<T : RemoteObject<*>> {
    suspend fun delete(key: String)
    suspend fun list(prefix: String): List<T>
    suspend fun move(remoteObject: T, toKey: String)
    suspend fun streamingUpload(key: String, collector: suspend () -> ByteArray?): StreamingUpload<T>
    suspend fun streamingUpload(key: String, inputs: Iterator<ByteArray>): StreamingUpload<T> =
        streamingUpload(key) {
            if (inputs.hasNext()) {
                inputs.next()
            } else {
                null
            }
        }
}

interface StreamingUpload<T: RemoteObject<*>> {
    suspend fun mapPart(f: suspend (ByteArray) -> ByteArray): StreamingUpload<T>
    suspend fun upload(): T
}
