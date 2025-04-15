/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.gcs

import com.google.cloud.storage.BlobId
import com.google.cloud.storage.BlobInfo
import com.google.cloud.storage.Storage
import io.airbyte.cdk.load.command.gcs.GcsClientConfiguration
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.InputStream
import java.nio.channels.Channels
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

/** Represents a single blob in Google Cloud Storage. */
data class GcsBlob(override val key: String, override val storageConfig: GcsClientConfiguration) :
    RemoteObject<GcsClientConfiguration>

class GcsClient(private val storage: Storage, private val config: GcsClientConfiguration) :
    ObjectStorageClient<GcsBlob> {

    private val log = KotlinLogging.logger {}

    override suspend fun list(prefix: String): Flow<GcsBlob> = flow {
        val fullPrefix = combinePath(config.gcsBucketName, prefix)
        val blobs = storage.list(config.gcsBucketName, Storage.BlobListOption.prefix(fullPrefix))

        for (blob in blobs.iterateAll()) {
            emit(GcsBlob(blob.name, config))
        }
    }

    override suspend fun move(key: String, toKey: String): GcsBlob {
        val fullSourceKey = combinePath(config.path, key)
        val fullTargetKey = combinePath(config.path, toKey)

        val sourceBlobId = BlobId.of(config.gcsBucketName, fullSourceKey)
        val targetBlobId = BlobId.of(config.gcsBucketName, fullTargetKey)

        storage.copy(
            Storage.CopyRequest.newBuilder().setSource(sourceBlobId).setTarget(targetBlobId).build()
        )
        storage.delete(sourceBlobId)

        return GcsBlob(toKey, config)
    }

    override suspend fun <U> get(key: String, block: (InputStream) -> U): U {
        val fullKey = combinePath(config.path, key)
        val blob = storage.get(BlobId.of(config.gcsBucketName, fullKey))

        // Convert ReadChannel to InputStream
        return Channels.newInputStream(blob.reader()).use { inputStream -> block(inputStream) }
    }

    override suspend fun getMetadata(key: String): Map<String, String> {
        val fullKey = combinePath(config.path, key)
        val blob = storage.get(BlobId.of(config.gcsBucketName, fullKey))

        // Convert Map<String, String?> to Map<String, String> by filtering out null values
        return blob.metadata?.mapNotNull { (key, value) -> value?.let { key to it } }?.toMap()
            ?: emptyMap()
    }

    override suspend fun put(key: String, bytes: ByteArray): GcsBlob {
        val fullKey = combinePath(config.path, key)
        val blobId = BlobId.of(config.gcsBucketName, fullKey)
        val blobInfo = BlobInfo.newBuilder(blobId).build()

        storage.create(blobInfo, bytes)

        return GcsBlob(key, config)
    }

    override suspend fun delete(key: String) {
        val fullKey = combinePath(config.path, key)
        storage.delete(BlobId.of(config.gcsBucketName, fullKey))
    }

    override suspend fun startStreamingUpload(
        key: String,
        metadata: Map<String, String>
    ): StreamingUpload<GcsBlob> {
        log.info { "Starting streaming upload for $key" }
        return GcsStreamingUpload(storage, key, config, metadata)
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
}
