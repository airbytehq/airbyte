/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.object_storage

import io.airbyte.cdk.load.message.RemoteObject
import kotlinx.coroutines.flow.Flow

interface ObjectStorageClient<T : RemoteObject> {
    suspend fun list(prefix: String): Flow<T>
    suspend fun put(key: String, bytes: ByteArray)
    suspend fun delete(key: String)
}
