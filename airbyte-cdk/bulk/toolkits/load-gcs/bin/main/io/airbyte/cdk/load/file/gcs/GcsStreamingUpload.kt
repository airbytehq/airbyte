/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.gcs

import com.google.cloud.storage.BlobId
import com.google.cloud.storage.BlobInfo
import com.google.cloud.storage.Storage
import com.google.cloud.storage.Storage.ComposeRequest
import io.airbyte.cdk.load.command.gcs.GcsClientConfiguration
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.airbyte.cdk.load.util.setOnce
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.ConcurrentSkipListMap
import java.util.concurrent.atomic.AtomicBoolean

/**
 * This class is responsible for uploading individual parts to GCS and composing them at the end.
 *
 * /!\ Unlike typical "multipart upload" semantics, each part is visible as a standalone object
 * until it is composed into a final object. That’s usually acceptable for BigQuery usage, but Will
 * be an issue with a dedicated GCS destination as it would probably be a breaking change
 */
class GcsStreamingUpload(
    private val storage: Storage,
    private val key: String,
    private val config: GcsClientConfiguration,
    private val metadata: Map<String, String>
) : StreamingUpload<GcsBlob> {

    private val log = KotlinLogging.logger {}
    private val isComplete = AtomicBoolean(false)
    private val uploadId = generateUploadId()

    /**
     * Store part references: index => temporary object name. We do not store file contents in
     * memory.
     */
    private val parts = ConcurrentSkipListMap<Int, String>()

    /** Upload a part to GCS. Each part is stored as a temporary blob. */
    override suspend fun uploadPart(part: ByteArray, index: Int) {
        check(parts.size + 1 <= 32) {
            "We are attempting to compose more than 32 parts for key $key. " +
                "GCS is not capable of doing that."
        }
        val partName = combinePath("$uploadId-part-$index")
        log.info { "Uploading part #$index => $partName" }

        val partBlobId = BlobId.of(config.gcsBucketName, partName)
        val partBlobInfo = BlobInfo.newBuilder(partBlobId).build()

        storage.create(partBlobInfo, part)

        parts[index] = partName

        log.info { "Uploaded part #$index => $partName, size: ${part.size} bytes" }
    }

    /** Compose all parts into the final object. */
    override suspend fun complete(): GcsBlob {
        if (!isComplete.setOnce()) {
            log.warn { "Complete called multiple times for gs://${config.gcsBucketName}/$key" }
            return GcsBlob(key, config)
        }

        if (parts.isEmpty()) {
            // This is not ideal but follows what S3 is doing. Ideally we would return null
            // or throw here. But until we update the CDK to handle that use case, this is
            // better than creating an empty object in storage.
            log.warn { "No parts uploaded. returning a blob pointing at nothing" }
            return GcsBlob(key, config)
        }

        // We can assume here that we won't have more than 32 parts. This should be handled
        // in the configuration (total size / chunk_size <= 32)
        val allPartNames = parts.values.toList()
        log.info { "Composing ${allPartNames.size} parts into gs://${config.gcsBucketName}/$key" }

        // Create the final blob with metadata
        val finalBlobId = BlobId.of(config.gcsBucketName, key)
        val finalBlobInfo = BlobInfo.newBuilder(finalBlobId).setMetadata(metadata).build()

        // Build the compose request with all part names as sources
        val composeRequest = ComposeRequest.newBuilder().setTarget(finalBlobInfo)

        // Add each part as a source
        parts.values.forEach { partName -> composeRequest.addSource(partName) }

        // Compose it all
        storage.compose(composeRequest.build())

        // Clean up the individual part objects
        cleanupParts()

        return GcsBlob(key, config)
    }

    /**
     * Delete all temporary part objects after successful composition. Intermediate objects get
     * cleaned up in the multi-level composition process or after the final composition.
     */
    private fun cleanupParts() {
        parts.values.forEach { partName ->
            try {
                storage.delete(BlobId.of(config.gcsBucketName, partName))
                log.info { "Deleted temporary part: gs://${config.gcsBucketName}/$partName" }
            } catch (e: Exception) {
                log.warn(e) {
                    "Failed to delete temporary part: gs://${config.gcsBucketName}/$partName"
                }
            }
        }
    }

    private fun generateUploadId(): String {
        val randomSuffix = (1..8).map { ('a'..'z').random() }.joinToString("")
        return "$key-${System.currentTimeMillis()}-$randomSuffix"
    }

    private fun combinePath(key: String): String {
        return if (config.path.isBlank()) {
            key
        } else {
            "${config.path}/$key".replace("//", "/")
        }
    }
}
