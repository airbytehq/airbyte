/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.azureBlobStorage

import com.azure.storage.blob.specialized.BlockBlobClient
import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageConfiguration
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.airbyte.cdk.load.util.setOnce
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.BufferedInputStream
import java.nio.ByteBuffer
import java.util.Base64
import java.util.concurrent.ConcurrentSkipListMap
import java.util.concurrent.atomic.AtomicBoolean

private const val BLOB_ID_PREFIX = "block"

class AzureBlobStreamingUpload(
    private val blockBlobClient: BlockBlobClient,
    private val config: AzureBlobStorageConfiguration,
    private val metadata: Map<String, String>
) : StreamingUpload<AzureBlob> {

    private val log = KotlinLogging.logger {}
    private val isComplete = AtomicBoolean(false)
    private val blockIds = ConcurrentSkipListMap<Int, String>()

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
        BufferedInputStream(part.inputStream()).use {
            blockBlobClient.stageBlock(
                blockId,
                it,
                part.size.toLong(),
            )
        }

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
                blockBlobClient.setMetadata(metadata)
            }
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
}
