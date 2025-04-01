/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

import com.google.cloud.storage.BlobId
import com.google.cloud.storage.BlobInfo
import com.google.cloud.storage.Storage
import io.airbyte.cdk.load.command.gcs.GcsClientConfiguration
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import java.io.InputStream
import java.nio.channels.Channels
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOn

/** Represents a single blob in Google Cloud Storage. */
data class GcsBlob(override val key: String, override val storageConfig: GcsClientConfiguration) :
    RemoteObject<GcsClientConfiguration>

class GcsClient(private val storage: Storage, private val config: GcsClientConfiguration) :
    ObjectStorageClient<GcsBlob> {

    override suspend fun list(prefix: String): Flow<GcsBlob> =
        flow {
                val fullPrefix = combinePath(config.bucketPath, prefix)
                val blobs =
                    storage.list(config.bucketName, Storage.BlobListOption.prefix(fullPrefix))

                for (blob in blobs.iterateAll()) {
                    emit(GcsBlob(blob.name, config))
                }
            }
            .flowOn(Dispatchers.IO)

    override suspend fun move(key: String, toKey: String): GcsBlob {
        val fullSourceKey = combinePath(config.bucketPath, key)
        val fullTargetKey = combinePath(config.bucketPath, toKey)

        val sourceBlobId = BlobId.of(config.bucketName, fullSourceKey)
        val targetBlobId = BlobId.of(config.bucketName, fullTargetKey)

        storage.copy(
            Storage.CopyRequest.newBuilder().setSource(sourceBlobId).setTarget(targetBlobId).build()
        )
        storage.delete(sourceBlobId)

        GcsBlob(toKey, config)
    }

    override suspend fun <U> get(key: String, block: (InputStream) -> U): U {
        val fullKey = combinePath(config.bucketPath, key)
        val blob = storage.get(BlobId.of(config.bucketName, fullKey))

        // Convert ReadChannel to InputStream
        Channels.newInputStream(blob.reader()).use { inputStream -> block(inputStream) }
    }

    override suspend fun getMetadata(key: String): Map<String, String> {
        val fullKey = combinePath(config.bucketPath, key)
        val blob = storage.get(BlobId.of(config.bucketName, fullKey))

        // Convert Map<String, String?> to Map<String, String> by filtering out null values
        blob.metadata?.mapNotNull { (key, value) -> value?.let { key to it } }?.toMap()
            ?: emptyMap()
    }

    override suspend fun put(key: String, bytes: ByteArray): GcsBlob {
        val fullKey = combinePath(config.bucketPath, key)
        val blobId = BlobId.of(config.bucketName, fullKey)
        val blobInfo = BlobInfo.newBuilder(blobId).build()

        storage.create(blobInfo, bytes)

        GcsBlob(key, config)
    }

    override suspend fun delete(key: String) {
        val fullKey = combinePath(config.bucketPath, key)
        storage.delete(BlobId.of(config.bucketName, fullKey))
    }

    override suspend fun delete(remoteObject: GcsBlob) {
        delete(remoteObject.key)
    }

    override suspend fun move(remoteObject: GcsBlob, toKey: String): GcsBlob {
        return move(remoteObject.key, toKey)
    }

    private fun combinePath(bucketPath: String, key: String): String {
        return if (bucketPath.isEmpty()) key else "$bucketPath/$key".replace("//", "/")
    }

    override suspend fun startStreamingUpload(
        key: String,
        metadata: Map<String, String>
    ): StreamingUpload<GcsBlob> {
        TODO("Not yet implemented")
    }
}
