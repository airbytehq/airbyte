/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.gcs

import com.google.cloud.storage.BlobId
import com.google.cloud.storage.BlobInfo
import com.google.cloud.storage.Storage
import io.airbyte.cdk.load.command.gcs.GcsClientConfiguration
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.airbyte.cdk.load.util.setOnce
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.ConcurrentSkipListMap
import java.util.concurrent.atomic.AtomicBoolean

/**
 * This class is responsible for uploading individual parts to GSC and compose them at the end.
 *
 * /!\ One thing to note here is that, unlike a multipart upload, which does not render the file
 * until everything has been finalized, this will create all the chunks on storage and they will be
 * visible. This is breaking change for an eventual GCS destination. It should be okay however for
 * BigQuery. We may also decide to add all the chunks under a specific Airbyte controlled folder /!\
 */
class GcsStreamingUpload(
    private val storage: Storage,
    private val config: GcsClientConfiguration,
    private val metadata: Map<String, String>
) : StreamingUpload<GcsBlob> {

    private val log = KotlinLogging.logger {}
    private val isComplete = AtomicBoolean(false)
    private val uploadId = generateUploadId()
    private val parts = ConcurrentSkipListMap<Int, String>()

    // GCS requires metadata keys to conform to RFC 2616 (HTTP/1.1)
    private val invalidMetadataCharsRegex = Regex("[^\\w\\-_.]")

    /**
     * Upload a part to the GCS object as part of a resumable upload. Each part gets its own unique
     * upload URL within the session.
     */
    override suspend fun uploadPart(part: ByteArray, index: Int) {
        // Generate a unique part name using the upload ID and index
        val partName = combinePath("$uploadId-part-$index")
        log.info { "Uploading part #$index => $partName" }

        // Create a temporary blob for each part
        val partBlobId = BlobId.of(config.gcsBucketName, partName)
        val partBlobInfo = BlobInfo.newBuilder(partBlobId).build()

        // Upload the part
        storage.create(partBlobInfo, part)

        // Keep track of the parts in the order they arrived
        parts[index] = partName

        log.info { "Uploaded part #$index => $partName, size: ${part.size} bytes" }
    }

    /**
     * Complete the upload by composing all uploaded parts into the final object. If no parts were
     * uploaded, create an empty object.
     */
    override suspend fun complete(): GcsBlob {
        // Generate final object key based on upload ID
        val finalObjectKey = combinePath("$uploadId-final")

        if (isComplete.setOnce()) {
            if (parts.isEmpty()) {
                log.warn {
                    "No parts uploaded. Creating empty object: gs://${config.gcsBucketName}/$finalObjectKey"
                }
                // Create an empty object
                val blobId = BlobId.of(config.gcsBucketName, finalObjectKey)
                val blobInfo =
                    BlobInfo.newBuilder(blobId).setMetadata(filterInvalidMetadata(metadata)).build()

                storage.create(blobInfo, ByteArray(0))
            } else {
                log.info {
                    "Composing parts for gs://${config.gcsBucketName}/$finalObjectKey: ${parts.values}"
                }

                // Create the final blob with metadata
                val blobId = BlobId.of(config.gcsBucketName, finalObjectKey)
                val blobInfo =
                    BlobInfo.newBuilder(blobId).setMetadata(filterInvalidMetadata(metadata)).build()

                // WARNING We need to keep the order of the upload unchanged when we compose.
                // Meaning that we will need to ensure that we compose based on the index
                // I also just remembered that there is a limit of 32 parts at a time when we
                // compose
                // I need to deal with that

                // Build the compose request with all part names as sources
                val composeRequest = Storage.ComposeRequest.newBuilder().setTarget(blobInfo)

                // Add each part as a source
                parts.values.forEach { partName -> composeRequest.addSource(partName) }

                // Compose all parts into the final object
                storage.compose(composeRequest.build())

                // Clean up temporary part objects
                cleanupParts()
            }
        } else {
            log.warn {
                "Complete called multiple times for gs://${config.gcsBucketName}/$finalObjectKey"
            }
        }

        return GcsBlob(finalObjectKey, config)
    }

    /** Delete all temporary part objects after successful composition */
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
        return "gcs-upload-${System.currentTimeMillis()}-${(1..8).map { ('a'..'z').random() }.joinToString("")}"
    }

    private fun filterInvalidMetadata(metadata: Map<String, String>): Map<String, String> {
        return metadata
            .mapKeys { (key, _) ->
                // Convert invalid characters to underscore and ensure lowercase
                key.lowercase().replace(invalidMetadataCharsRegex, "_")
            }
            .filter { (key, value) ->
                // Filter out entries with empty keys or values
                key.isNotBlank() && value.isNotBlank()
            }
    }

    private fun combinePath(key: String): String {
        return if (config.path.isBlank()) key else "${config.path}/$key".replace("//", "/")
    }
}
