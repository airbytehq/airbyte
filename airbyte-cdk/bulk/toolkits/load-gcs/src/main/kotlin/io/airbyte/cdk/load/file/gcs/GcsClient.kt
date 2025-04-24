/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.gcs

import com.google.cloud.storage.BlobId
import com.google.cloud.storage.BlobInfo
import com.google.cloud.storage.Storage
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.gcs.GcsClientConfiguration
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.airbyte.cdk.load.file.s3.S3Client
import io.airbyte.cdk.load.file.s3.S3Object
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.InputStream
import java.nio.channels.Channels
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.map

/** Represents a single blob in Google Cloud Storage. */
data class GcsBlob(override val key: String, override val storageConfig: GcsClientConfiguration) :
    RemoteObject<GcsClientConfiguration>

interface GcsClient : ObjectStorageClient<GcsBlob>

fun S3Object.toGcsBlob(config: GcsClientConfiguration) = GcsBlob(this.key, config)

fun GcsBlob.toS3Object() = S3Object(this.key, this.storageConfig.s3BucketConfiguration())

/**
 * This client is currently the primary class. It is specifically built around the S3Client. It
 * exists to allow us to no load the S3 toolkit and avoid client collision. We specifically need it
 * because we are forced into the HMAC auth for legacy reasons. At the end of the day, this is just
 * a bare-bone wrapper around the S3Client
 */
@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class GcsS3Client(
    private val s3Client: S3Client,
    private val config: GcsClientConfiguration,
) : GcsClient {
    override suspend fun list(prefix: String): Flow<GcsBlob> =
        s3Client.list(prefix).map { it.toGcsBlob(config) }

    override suspend fun move(remoteObject: GcsBlob, toKey: String): GcsBlob =
        s3Client.move(remoteObject.toS3Object(), toKey).toGcsBlob(config)

    override suspend fun move(key: String, toKey: String): GcsBlob =
        s3Client.move(key, toKey).toGcsBlob(config)

    override suspend fun <U> get(key: String, block: (InputStream) -> U): U =
        s3Client.get(key, block)

    override suspend fun getMetadata(key: String): Map<String, String> = s3Client.getMetadata(key)

    override suspend fun put(key: String, bytes: ByteArray): GcsBlob =
        s3Client.put(key, bytes).toGcsBlob(config)

    override suspend fun delete(remoteObject: GcsBlob) = s3Client.delete(remoteObject.toS3Object())

    override suspend fun delete(key: String) = s3Client.delete(key)

    override suspend fun startStreamingUpload(
        key: String,
        metadata: Map<String, String>
    ): StreamingUpload<GcsBlob> {
        val s3Upload = s3Client.startStreamingUpload(key, metadata)
        return object : StreamingUpload<GcsBlob> {
            override suspend fun uploadPart(part: ByteArray, index: Int) =
                s3Upload.uploadPart(part, index)

            override suspend fun complete(): GcsBlob = s3Upload.complete().toGcsBlob(config)
        }
    }
}

/**
 * THis client should be used when we finally decide to support native GCP auth. We can then swap
 * over to this client instead of the [GcsS3Client] which will require us to use HMAC auth.
 */
class GcsNativeClient(private val storage: Storage, private val config: GcsClientConfiguration) :
    GcsClient {

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
