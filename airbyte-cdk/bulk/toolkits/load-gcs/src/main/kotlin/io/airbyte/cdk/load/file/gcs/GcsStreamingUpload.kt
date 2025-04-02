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
        val partName = "$objectName-part-$index"
        log.info { "Uploading part #$index => $partName" }

        // Create a temporary blob for each part
        val partBlobId = BlobId.of(bucketName, partName)
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
        if (isComplete.setOnce()) {
            if (parts.isEmpty()) {
                log.warn {
                    "No parts uploaded. Creating empty object: gs://$bucketName/$objectName"
                }
                // Create an empty object
                val blobId = BlobId.of(bucketName, objectName)
                val blobInfo =
                    BlobInfo.newBuilder(blobId).setMetadata(filterInvalidMetadata(metadata)).build()

                storage.create(blobInfo, ByteArray(0))
            } else {
                log.info { "Composing parts for gs://$bucketName/$objectName: ${parts.values}" }

                // Create a list of source blobs from all the parts
                val sourceBlobs =
                    parts.values.map { partName ->
                        Storage.BlobSourceOption.generationMatch()
                        Storage.ComposeRequest.SourceBlob.newBuilder().setName(partName).build()
                    }

                // Create the final blob with metadata
                val blobId = BlobId.of(bucketName, objectName)
                val blobInfo =
                    BlobInfo.newBuilder(blobId).setMetadata(filterInvalidMetadata(metadata)).build()

                // Compose all parts into the final object
                storage.compose(
                    Storage.ComposeRequest.newBuilder()
                        .addSource(sourceBlobs)
                        .setTarget(blobInfo)
                        .build()
                )

                // Clean up temporary part objects
                cleanupParts()
            }
        } else {
            log.warn { "Complete called multiple times for gs://$bucketName/$objectName" }
        }

        return GcsBlob(objectName, config)
    }

    /** Delete all temporary part objects after successful composition */
    private fun cleanupParts() {
        parts.values.forEach { partName ->
            try {
                storage.delete(BlobId.of(bucketName, partName))
                log.info { "Deleted temporary part: gs://$bucketName/$partName" }
            } catch (e: Exception) {
                log.warn(e) { "Failed to delete temporary part: gs://$bucketName/$partName" }
            }
        }
    }

    /** Generate a unique upload ID for this session */
    private fun generateUploadId(): String {
        return "gcs-upload-${System.currentTimeMillis()}-${(1..8).map { ('a'..'z').random() }.joinToString("")}"
    }

    /** Filter out invalid metadata keys according to GCS requirements */
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
}
