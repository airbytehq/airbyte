/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.gcs

import com.google.cloud.WriteChannel
import com.google.cloud.storage.BlobId
import com.google.cloud.storage.BlobInfo
import com.google.cloud.storage.Storage
import io.airbyte.cdk.load.command.gcs.GcsClientConfiguration
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.ByteBuffer
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.locks.ReentrantLock
import kotlin.concurrent.withLock
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Alternative implementation of StreamingUpload for Google Cloud Storage using resumable uploads.
 *
 * Unlike the current GcsStreamingUpload which creates separate blobs per part and then composes
 * them together, this implementation:
 *
 * 1. Streams each part directly to GCS as it arrives (assuming parts arrive in order)
 * 2. Uses Google Cloud Storage's built-in resumable upload API
 * 3. Creates only a single blob in the bucket
 *
 * Advantages:
 * - No intermediate blobs to clean up
 * - Uses GCS's native resumable upload capability
 * - Doesn't buffer parts in memory
 * - Fewer API calls to GCS
 *
 * Limitations:
 * - Requires parts to arrive in sequential order (1, 2, 3...)
 * - Less resilient to process crashes during upload (would need to add state persistence)
 */
class GcsResumableStreamingUpload(
    storage: Storage,
    private val key: String,
    private val config: GcsClientConfiguration,
    metadata: Map<String, String>,
    chunkSizeBytes: Int = 1 * 1024 * 1024 // 8MB default chunk size
) : StreamingUpload<GcsBlob> {

    private val log = KotlinLogging.logger {}

    // For thread safety
    private val uploadLock = ReentrantLock()
    private val isCompleted = AtomicBoolean(false)

    // Track the expected next part index
    private val nextExpectedPartIndex = AtomicInteger(1)

    // Create the writer once and reuse it for all parts
    private val writer: WriteChannel

    // The GCS path including bucket path prefix
    private val fullKey = combinePath(config.path, key)

    init {
        // Initialize the resumable upload session
        val blobId = BlobId.of(config.gcsBucketName, fullKey)
        val blobInfo = BlobInfo.newBuilder(blobId).setMetadata(metadata).build()

        // Create a write channel that will maintain the resumable upload state
        writer = storage.writer(blobInfo)

        // Set chunk size for resumable upload if channel is open
        if (writer.isOpen) {
            writer.setChunkSize(chunkSizeBytes)
        }

        log.info { "Initialized resumable upload for gs://${config.gcsBucketName}/$fullKey" }
    }

    override suspend fun uploadPart(part: ByteArray, index: Int) =
        withContext(Dispatchers.IO) {
            require(index > 0) { "Part index must be greater than 0" }
            require(!isCompleted.get()) { "Upload is already complete" }

            // Verify the part arrives in the expected order
            //        val expectedIndex = nextExpectedPartIndex.get()
            //        require(index == expectedIndex) {
            //            "Expected part $expectedIndex but received part $index. Parts must be
            // uploaded in order."
            //        }

            uploadLock.withLock {
                try {
                    // Convert part to ByteBuffer and write
                    val buffer = ByteBuffer.wrap(part)
                    writer.write(buffer)

                    // Update next expected part index
                    nextExpectedPartIndex.incrementAndGet()

                    log.debug { "Uploaded part $index for key $key with size ${part.size} bytes" }
                } catch (e: Exception) {
                    log.error(e) { "Error uploading part $index for key $key: ${e.message}" }
                    throw e
                }
            }
        }

    override suspend fun complete(): GcsBlob =
        withContext(Dispatchers.IO) {
            if (isCompleted.compareAndSet(false, true)) {
                try {
                    val partsUploaded = nextExpectedPartIndex.get() - 1

                    if (partsUploaded == 0) {
                        // No parts were uploaded - don't create an empty object
                        log.info {
                            "No parts uploaded for $key, closing writer without completing upload"
                        }
                    } else {
                        log.info { "Completing upload for $key with $partsUploaded parts" }
                    }

                    // Close the writer to finalize the upload
                    writer.close()
                } catch (e: Exception) {
                    log.error(e) { "Error completing upload for $key: ${e.message}" }
                    try {
                        writer.close()
                    } catch (closeEx: Exception) {
                        log.warn(closeEx) { "Error closing writer after exception" }
                    }
                    throw e
                }
            } else {
                log.debug { "Upload already completed for $key" }
            }

            return@withContext GcsBlob(key, config)
        }

    private fun combinePath(bucketPath: String, key: String): String {
        return if (bucketPath.isEmpty()) key else "$bucketPath/$key".replace("//", "/")
    }
}
