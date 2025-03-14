/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.azureBlobStorage

import com.azure.storage.blob.specialized.BlockBlobClient
import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageConfiguration
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.airbyte.cdk.load.util.setOnce
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.ByteBuffer
import java.util.Base64
import java.util.concurrent.ConcurrentSkipListMap
import java.util.concurrent.atomic.AtomicBoolean

private const val BLOB_ID_PREFIX = "block"
private const val RESERVED_PREFIX = "x-ms-"

class AzureBlobStreamingUpload(
    private val blockBlobClient: BlockBlobClient,
    private val config: AzureBlobStorageConfiguration,
    private val metadata: Map<String, String>
) : StreamingUpload<AzureBlob> {

    private val log = KotlinLogging.logger {}
    private val isComplete = AtomicBoolean(false)
    private val blockIds = ConcurrentSkipListMap<Int, String>()
    private val invalidCharsRegex = Regex("[<>:\"/\\\\?#*\\-]")

    /**
     * Each part that arrives is treated as a new block. We must generate unique block IDs for each
     * call (Azure requires base64-encoded strings).
     */
    override suspend fun uploadPart(part: ByteArray, index: Int) {
        // Generate a unique block id. We’ll just use index or a random
        val rawBlockId = "block-$index-${System.nanoTime()}"
        val blockId = generateBlockId(index)

        log.info { "Staging block #$index => $rawBlockId (encoded = $blockId)" }

        // The stageBlock call can be done asynchronously or blocking.
        // Here we use the blocking call in a coroutine context.
        part.inputStream().use {
            blockBlobClient.stageBlock(
                blockId,
                it,
                part.size.toLong(),
            )
        }

        log.info { "Staged block #$index => $rawBlockId (encoded = $blockId)" }

        // Keep track of the blocks in the order they arrived (or the index).
        blockIds[index] = blockId
    }

    /**
     * After all parts are uploaded, we finalize by committing the block list in ascending order. If
     * no parts were uploaded, we skip.
     */
    override suspend fun complete(): AzureBlob {
        if (isComplete.setOnce()) {
            if (blockIds.isEmpty()) {
                log.warn {
                    "No blocks uploaded. Committing empty blob: ${blockBlobClient.blobName}"
                }
            } else {
                val blockList = blockIds.values.toList()
                log.info { "Committing block list for ${blockBlobClient.blobName}: $blockList" }
                blockBlobClient.commitBlockList(blockIds.values.toList(), true) // Overwrite = true
            }

            // Set any metadata
            if (metadata.isNotEmpty()) {
                val filteredMetadata = filterInvalidMetadata(metadata)
                if (filteredMetadata.isNotEmpty()) {
                    blockBlobClient.setMetadata(filteredMetadata)
                }
            }
        } else {
            log.warn { "Complete called multiple times for ${blockBlobClient.blobName}" }
        }

        return AzureBlob(blockBlobClient.blobName, config)
    }

    fun generateBlockId(index: Int): String {
        // Create a fixed-size ByteBuffer to store all components
        val buffer = ByteBuffer.allocate(32) // Fixed size buffer

        // Write prefix (padded to 10 bytes)
        BLOB_ID_PREFIX.padEnd(10, ' ').forEach { buffer.put(it.code.toByte()) }

        // Write integer (padded to 10 digits)
        index.toString().padStart(10, '0').forEach { buffer.put(it.code.toByte()) }

        // Generate random suffix (exactly 12 chars)
        val suffixChars = ('A'..'Z') + ('0'..'9')
        (1..12).forEach { _ -> buffer.put(suffixChars.random().code.toByte()) }

        // Encode the entire fixed-length buffer to Base64
        return Base64.getEncoder().encodeToString(buffer.array())
    }
    /**
     * Return a new map containing only valid key/value pairs according to Azure metadata
     * constraints.
     */
    private fun filterInvalidMetadata(metadata: Map<String, String>): Map<String, String> {
        return metadata.filter { (key, value) -> isValidKey(key) && isValidValue(value) }
    }
    /**
     * Validates if the provided key string meets the required criteria.
     *
     * @param key The string to validate as a key
     * @return Boolean indicating whether the key is valid
     */
    private fun isValidKey(key: String): Boolean {
        // Reject empty keys or keys that start with reserved prefix
        if (key.isBlank() || key.startsWith(RESERVED_PREFIX)) return false

        // Reject keys containing any characters matching the invalid pattern
        if (invalidCharsRegex.containsMatchIn(key)) return false

        // Ensure all characters are within the printable ASCII range (32-126)
        // This includes letters, numbers, and common symbols
        return key.all { it.code in 32..126 }
    }

    /**
     * Validates if the provided value string meets the required criteria.
     *
     * @param value The string to validate as a value
     * @return Boolean indicating whether the value is valid
     */
    private fun isValidValue(value: String): Boolean {
        // Reject values containing any characters matching the invalid pattern
        if (invalidCharsRegex.containsMatchIn(value)) return false

        // Ensure all characters are within the printable ASCII range (32-126)
        // This includes letters, numbers, and common symbols
        return value.all { it.code in 32..126 }
    }
}
