/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.gcs

import io.airbyte.cdk.load.command.gcs.GcsClientConfiguration
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import java.io.InputStream
import kotlinx.coroutines.flow.Flow

/** Represents a single blob in Azure. */
data class GcsBlob(override val key: String, override val storageConfig: GcsClientConfiguration) :
    RemoteObject<GcsClientConfiguration>

class GcsClient : ObjectStorageClient<GcsBlob> {
    override suspend fun list(prefix: String): Flow<GcsBlob> {
        TODO("Not yet implemented")
    }

    override suspend fun move(key: String, toKey: String): GcsBlob {
        TODO("Not yet implemented")
    }

    override suspend fun <U> get(key: String, block: (InputStream) -> U): U {
        TODO("Not yet implemented")
    }

    override suspend fun getMetadata(key: String): Map<String, String> {
        TODO("Not yet implemented")
    }

    override suspend fun put(key: String, bytes: ByteArray): GcsBlob {
        TODO("Not yet implemented")
    }

    override suspend fun delete(key: String) {
        TODO("Not yet implemented")
    }

    override suspend fun startStreamingUpload(
        key: String,
        metadata: Map<String, String>
    ): StreamingUpload<GcsBlob> {
        TODO("Not yet implemented")
    }

    override suspend fun delete(remoteObject: GcsBlob) {
        TODO("Not yet implemented")
    }

    override suspend fun move(remoteObject: GcsBlob, toKey: String): GcsBlob {
        TODO("Not yet implemented")
    }
}
