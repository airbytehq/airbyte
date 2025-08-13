/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.load.file.azureBlobStorage

import com.azure.core.http.rest.Response
import com.azure.storage.blob.models.BlobStorageException
import com.azure.storage.blob.models.BlockBlobItem
import com.azure.storage.blob.options.BlockBlobCommitBlockListOptions
import com.azure.storage.blob.specialized.BlockBlobClient
import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageClientConfiguration
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import io.mockk.slot
import io.mockk.verify
import java.io.InputStream
import java.nio.charset.StandardCharsets
import java.util.Base64
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class AzureBlobStreamingUploadTest {

    private lateinit var blockBlobClient: BlockBlobClient
    private lateinit var config: AzureBlobStorageClientConfiguration
    private val metadata = mapOf("env" to "dev", "author" to "testUser", "ab_generation_id" to "0")
    private lateinit var streamingUpload: AzureBlobStreamingUpload

    @BeforeEach
    fun setup() {
        blockBlobClient = mockk()
        config =
            AzureBlobStorageClientConfiguration(
                accountName = "fakeAccount",
                containerName = "fakeContainer",
                sharedAccessSignature = "",
                accountKey = "test",
            )
        every { blockBlobClient.blobName } returns "testBlob"
        streamingUpload = AzureBlobStreamingUpload(blockBlobClient, config, metadata)
    }

    @Test
    fun `uploadPart - stages block successfully`() = runBlocking {
        val partData = "Hello Azure".toByteArray()
        val index = 1
        every { blockBlobClient.stageBlock(any(), any<InputStream>(), any()) } just runs

        streamingUpload.uploadPart(partData, index)

        verify(exactly = 1) {
            blockBlobClient.stageBlock(any(), any<InputStream>(), partData.size.toLong())
        }
    }

    @Test
    fun `uploadPart - throws if stageBlock fails`(): Unit = runBlocking {
        every { blockBlobClient.stageBlock(any(), any<InputStream>(), any()) } throws
            BlobStorageException("Staging failed", null, null)

        assertThrows(BlobStorageException::class.java) {
            runBlocking { streamingUpload.uploadPart(ByteArray(4), 0) }
        }
    }

    @Test
    fun `complete - commits empty blob when no parts uploaded`() = runBlocking {
        val response = mockk<Response<BlockBlobItem>>()
        val optsSlot = slot<BlockBlobCommitBlockListOptions>()

        every { blockBlobClient.commitBlockListWithResponse(capture(optsSlot), null, null) } returns
            response

        val result = streamingUpload.complete()

        verify(exactly = 1) { blockBlobClient.commitBlockListWithResponse(any(), null, null) }
        assertTrue(optsSlot.captured.base64BlockIds.isEmpty(), "Block list should be empty")
        assertEquals(metadata, optsSlot.captured.metadata)
        assertEquals("testBlob", result.key)
        assertEquals(config, result.storageConfig)
    }

    @Test
    fun `complete - commits blocks in ascending index order`() = runBlocking {
        val response = mockk<Response<BlockBlobItem>>()
        val optsSlot = slot<BlockBlobCommitBlockListOptions>()

        every { blockBlobClient.stageBlock(any(), any<InputStream>(), any()) } just runs
        every { blockBlobClient.commitBlockListWithResponse(capture(optsSlot), null, null) } returns
            response

        // upload out of order
        streamingUpload.uploadPart("B".toByteArray(), 2)
        streamingUpload.uploadPart("A".toByteArray(), 0)
        streamingUpload.uploadPart("C".toByteArray(), 1)

        val result = streamingUpload.complete()

        verify(exactly = 1) { blockBlobClient.commitBlockListWithResponse(any(), null, null) }
        // Ensure 3 blocks & ascending order
        assertEquals(3, optsSlot.captured.base64BlockIds.size)
        val ids = optsSlot.captured.base64BlockIds
        assertTrue(ids == ids.sorted(), "Block IDs must be in ascending order")

        assertEquals(metadata, optsSlot.captured.metadata)
        assertEquals("testBlob", result.key)
        assertEquals(config, result.storageConfig)
    }

    @Test
    fun `complete - idempotent, commit only once`() = runBlocking {
        val response = mockk<Response<BlockBlobItem>>()
        every { blockBlobClient.stageBlock(any(), any<InputStream>(), any()) } just runs
        every { blockBlobClient.commitBlockListWithResponse(any(), null, null) } returns response

        streamingUpload.uploadPart("hello".toByteArray(), 5)

        val first = streamingUpload.complete()
        val second = streamingUpload.complete()

        verify(exactly = 1) { blockBlobClient.commitBlockListWithResponse(any(), null, null) }
        assertEquals(first.key, second.key)
        assertEquals(config, first.storageConfig)
    }

    @Test
    fun `complete - propagates exception from commitBlockListWithResponse`() = runBlocking {
        every { blockBlobClient.stageBlock(any(), any<InputStream>(), any()) } just runs
        every { blockBlobClient.commitBlockListWithResponse(any(), null, null) } throws
            BlobStorageException("Commit failed", null, null)

        streamingUpload.uploadPart("abc".toByteArray(), 1)

        assertThrows(BlobStorageException::class.java) {
            runBlocking { streamingUpload.complete() }
        }
    }

    @Test
    fun `generateBlockId - returns fixed 32-byte structure`() {
        val client = mockk<BlockBlobClient>(relaxed = true)
        val cfg =
            AzureBlobStorageClientConfiguration(
                accountName = "acc",
                containerName = "container",
                sharedAccessSignature = "",
                accountKey = "key"
            )
        val uploader = AzureBlobStreamingUpload(client, cfg, emptyMap())

        val id42 = uploader.generateBlockId(42)
        val id1 = uploader.generateBlockId(1)
        assertEquals(id42.length, id1.length, "Base64 strings must be fixed-length")

        val decoded = Base64.getDecoder().decode(id42)
        assertEquals(32, decoded.size)

        val prefix = decoded.copyOfRange(0, 10).toString(StandardCharsets.US_ASCII)
        assertEquals("block     ", prefix)

        val idx = decoded.copyOfRange(10, 20).toString(StandardCharsets.US_ASCII)
        assertEquals("0000000042", idx)

        decoded.copyOfRange(20, 32).forEach { c ->
            val ch = c.toInt().toChar()
            assertTrue(ch.isUpperCase() || ch.isDigit(), "Suffix char '$ch' must be A-Z or 0-9")
        }
    }
}
