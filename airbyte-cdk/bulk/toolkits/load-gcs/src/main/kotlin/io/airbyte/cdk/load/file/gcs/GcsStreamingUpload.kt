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
 * until
 * ```
 *    it is composed into a final object. That’s usually acceptable for BigQuery usage, but be aware
 *    if building a pure GCS-based destination.
 * ```
 */
class GcsStreamingUpload(
    private val storage: Storage,
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

    // GCS requires metadata keys to conform to RFC 2616 (HTTP/1.1)
    private val invalidMetadataCharsRegex = Regex("[^\\w\\-_.]")

    /** Upload a part to GCS. Each part is stored as a temporary blob. */
    override suspend fun uploadPart(part: ByteArray, index: Int) {
        val partName = combinePath("$uploadId-part-$index")
        log.info { "Uploading part #$index => $partName" }

        val partBlobId = BlobId.of(config.gcsBucketName, partName)
        val partBlobInfo = BlobInfo.newBuilder(partBlobId).build()

        storage.create(partBlobInfo, part)

        parts[index] = partName

        log.info { "Uploaded part #$index => $partName, size: ${part.size} bytes" }
    }

    /** Compose all parts into the final object. If no parts exist, create an empty object. */
    override suspend fun complete(): GcsBlob {
        val finalObjectKey = combinePath("$uploadId-final")

        if (!isComplete.setOnce()) {
            log.warn {
                "Complete called multiple times for gs://${config.gcsBucketName}/$finalObjectKey"
            }
            return GcsBlob(finalObjectKey, config)
        }

        // Prepare the final blob info with metadata
        val finalBlobId = BlobId.of(config.gcsBucketName, finalObjectKey)
        val finalBlobInfo =
            BlobInfo.newBuilder(finalBlobId).setMetadata(filterInvalidMetadata(metadata)).build()

        if (parts.isEmpty()) {
            // Create an empty object if no parts were uploaded
            log.warn {
                "No parts uploaded. Creating empty object: gs://${config.gcsBucketName}/$finalObjectKey"
            }
            storage.create(finalBlobInfo, ByteArray(0))
            return GcsBlob(finalObjectKey, config)
        }

        // Compose all part objects (possibly more than 32) into one.
        val allPartNames = parts.values.toList()
        log.info {
            "Composing ${allPartNames.size} parts into gs://${config.gcsBucketName}/$finalObjectKey"
        }

        // multiLevelCompose returns the name of a single object that combines all parts
        val composedName = multiLevelCompose(allPartNames)

        // If multiLevelCompose did not produce finalObjectKey directly,
        // compose that single result into the final blob so we can set metadata
        if (composedName != finalObjectKey) {
            val composeRequest =
                ComposeRequest.newBuilder().setTarget(finalBlobInfo).addSource(composedName).build()
            storage.compose(composeRequest)

            // Clean up that last intermediate
            storage.delete(BlobId.of(config.gcsBucketName, composedName))
        } else {
            // Otherwise, just update metadata on it (in case it was created directly)
            val existing = storage.get(finalBlobId)
            existing?.toBuilder()?.setMetadata(filterInvalidMetadata(metadata))?.build()?.also {
                storage.update(it)
            }
        }

        // Clean up the individual part objects
        cleanupParts()

        return GcsBlob(finalObjectKey, config)
    }

    /**
     * Compose an arbitrary list of object names into one GCS object, respecting the 32-object
     * limit. We do so in multiple passes ("layers"), chunking up to 32 objects at each step.
     */
    private fun multiLevelCompose(sources: List<String>): String {
        var currentParts = sources
        var pass = 0

        // Repeat until we have 32 or fewer objects.
        while (currentParts.size > 32) {
            val newParts = mutableListOf<String>()

            // In each pass, chunk the list into sublists of up to 32 items,
            // compose them into a new intermediate object, and collect those intermediates.
            for ((i, chunk) in currentParts.chunked(32).withIndex()) {
                val intermediateName = combinePath("$uploadId-intermediate-pass${pass}-$i")
                val intermediateBlobId = BlobId.of(config.gcsBucketName, intermediateName)
                val intermediateInfo = BlobInfo.newBuilder(intermediateBlobId).build()

                val composeRequest =
                    ComposeRequest.newBuilder()
                        .setTarget(intermediateInfo)
                        .addSource(chunk) // chunk is an Iterable<String>
                        .build()

                storage.compose(composeRequest)
                newParts.add(intermediateName)
            }

            currentParts = newParts
            pass++
        }

        // Now we have 32 or fewer objects left. If it's exactly 1, we're done.
        if (currentParts.size == 1) {
            return currentParts[0]
        }

        // Otherwise, compose them all in one final pass.
        val finalIntermediate = combinePath("$uploadId-intermediate-pass${pass}-final")
        val finalBlobId = BlobId.of(config.gcsBucketName, finalIntermediate)
        val finalBlobInfo = BlobInfo.newBuilder(finalBlobId).build()

        val request =
            ComposeRequest.newBuilder()
                .setTarget(finalBlobInfo)
                .addSource(currentParts) // 2..32 objects
                .build()

        storage.compose(request)
        return finalIntermediate
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
        return "gcs-upload-${System.currentTimeMillis()}-$randomSuffix"
    }

    /** Filter out invalid metadata keys/values and rename invalid chars in keys to underscores. */
    private fun filterInvalidMetadata(metadata: Map<String, String>): Map<String, String> {
        return metadata
            .mapKeys { (key, _) ->
                // Convert invalid characters to underscore and force lowercase
                key.lowercase().replace(invalidMetadataCharsRegex, "_")
            }
            .filter { (key, value) -> key.isNotBlank() && value.isNotBlank() }
    }

    private fun combinePath(key: String): String {
        return if (config.path.isBlank()) {
            key
        } else {
            "${config.path}/$key".replace("//", "/")
        }
    }
}
