/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.azureBlobStorage

import com.azure.core.http.HttpResponse
import com.azure.core.http.rest.PagedIterable
import com.azure.core.util.BinaryData
import com.azure.core.util.polling.PollResponse
import com.azure.core.util.polling.SyncPoller
import com.azure.storage.blob.BlobClient
import com.azure.storage.blob.BlobContainerClient
import com.azure.storage.blob.BlobServiceClient
import com.azure.storage.blob.models.BlobCopyInfo
import com.azure.storage.blob.models.BlobItem
import com.azure.storage.blob.models.BlobProperties
import com.azure.storage.blob.models.BlobStorageException
import com.azure.storage.blob.specialized.BlobInputStream
import com.azure.storage.blob.specialized.BlockBlobClient
import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageConfiguration
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import io.mockk.slot
import io.mockk.verify
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertArrayEquals
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class AzureBlobClientTest {

    private lateinit var serviceClient: BlobServiceClient
    private lateinit var containerClient: BlobContainerClient
    private lateinit var blobConfig: AzureBlobStorageConfiguration
    private lateinit var azureBlobClient: AzureBlobClient

    @BeforeEach
    fun setup() {
        serviceClient = mockk()
        containerClient = mockk()
        blobConfig =
            AzureBlobStorageConfiguration(
                accountName = "testAccount",
                containerName = "testContainer",
                sharedAccessSignature = "null",
            )
        every { serviceClient.getBlobContainerClient(blobConfig.containerName) } returns
            containerClient

        azureBlobClient =
            AzureBlobClient(
                serviceClient = serviceClient,
                blobConfig = blobConfig,
            )
    }

    @Test
    fun `list - returns only blobs that match prefix`() = runBlocking {
        val prefix = "testPrefix"
        val blobItem1 = mockk<BlobItem> { every { name } returns "testPrefix-blob1" }
        val blobItem2 = mockk<BlobItem> { every { name } returns "testPrefix-blob2" }
        val blobItem3 = mockk<BlobItem> { every { name } returns "other-blob" }

        val pagedIterable =
            mockk<PagedIterable<BlobItem>> {
                every { iterator() } returns
                    mutableListOf(blobItem1, blobItem2, blobItem3).iterator()
            }

        every { containerClient.listBlobs(any(), any()) } returns pagedIterable

        val results = azureBlobClient.list(prefix).toList()

        assertEquals(2, results.size)
        assertTrue(results.any { it.key == "testPrefix-blob1" })
        assertTrue(results.any { it.key == "testPrefix-blob2" })
        assertFalse(results.any { it.key == "other-blob" })

        verify(exactly = 1) { containerClient.listBlobs(any(), null) }
    }

    @Test
    fun `list - no blobs returned`() = runBlocking {
        val prefix = "emptyPrefix"
        val pagedIterable =
            mockk<PagedIterable<BlobItem>> {
                every { iterator() } returns mutableListOf<BlobItem>().iterator()
            }

        every { containerClient.listBlobs(any(), any()) } returns pagedIterable

        val results = azureBlobClient.list(prefix).toList()
        assertTrue(results.isEmpty())

        verify(exactly = 1) { containerClient.listBlobs(any(), null) }
    }

    @Test
    fun `move - copy and delete success`() = runBlocking {
        val sourceKey = "sourceBlob"
        val destKey = "destinationBlob"

        val sourceBlobClient = mockk<BlobClient>(relaxed = true)
        val destBlobClient = mockk<BlobClient>(relaxed = true)
        val pollResponse = mockk<PollResponse<BlobCopyInfo>>(relaxed = true)
        val copyOperation = mockk<SyncPoller<BlobCopyInfo, Void>>(relaxed = true)

        every {
            serviceClient.getBlobContainerClient(blobConfig.containerName).getBlobClient(sourceKey)
        } returns sourceBlobClient
        every {
            serviceClient.getBlobContainerClient(blobConfig.containerName).getBlobClient(destKey)
        } returns destBlobClient
        every { sourceBlobClient.blobUrl } returns "http://fakeurl/sourceBlob"
        every { destBlobClient.beginCopy("http://fakeurl/sourceBlob", null) } returns copyOperation

        // Simulate copy completion
        every { copyOperation.waitForCompletion() } returns pollResponse

        val result = azureBlobClient.move(sourceKey, destKey)

        verify(exactly = 1) { destBlobClient.beginCopy("http://fakeurl/sourceBlob", null) }
        verify(exactly = 1) { sourceBlobClient.delete() }

        assertEquals(destKey, result.key)
        assertEquals(blobConfig, result.storageConfig)
    }

    @Test
    fun `move - copy fails with BlobStorageException`(): Unit = runBlocking {
        val sourceKey = "sourceBlob"
        val destKey = "destinationBlob"

        val sourceBlobClient = mockk<BlobClient>()
        val destBlobClient = mockk<BlobClient>()
        val copyOperation = mockk<SyncPoller<BlobCopyInfo, Void>>(relaxed = true)

        every {
            serviceClient.getBlobContainerClient(blobConfig.containerName).getBlobClient(sourceKey)
        } returns sourceBlobClient
        every {
            serviceClient.getBlobContainerClient(blobConfig.containerName).getBlobClient(destKey)
        } returns destBlobClient
        every { sourceBlobClient.blobUrl } returns "http://fakeurl/sourceBlob"
        every {
            destBlobClient.beginCopy(
                "http://fakeurl/sourceBlob",
                null,
            )
        } returns copyOperation
        every { copyOperation.waitForCompletion() } throws
            BlobStorageException(
                "Copy failed",
                null,
                null,
            )

        assertThrows(BlobStorageException::class.java) {
            runBlocking { azureBlobClient.move(sourceKey, destKey) }
        }
    }

    @Test
    fun `get - reads stream successfully`() = runBlocking {
        val key = "someKey"
        val testData = "Hello World".toByteArray()
        val inputStream = testData.inputStream()

        val blobClient = mockk<BlobClient>()
        val blobInputStream = mockk<BlobInputStream>()
        every { blobInputStream.available() } answers { inputStream.available() }
        every { blobInputStream.read(capture(slot())) } answers { inputStream.read(firstArg()) }
        every { blobInputStream.close() } answers { inputStream.close() }

        every { containerClient.getBlobClient(key) } returns blobClient
        every { blobClient.openInputStream() } returns blobInputStream

        val result = azureBlobClient.get(key) { input -> input.readBytes().decodeToString() }

        assertEquals("Hello World", result)
        verify(exactly = 1) { blobClient.openInputStream() }
    }

    @Test
    fun `get - throws exception on openInputStream`(): Unit = runBlocking {
        val key = "nonExistentKey"
        val blobClient = mockk<BlobClient>()

        every { containerClient.getBlobClient(key) } returns blobClient
        every { blobClient.openInputStream() } throws
            BlobStorageException(
                "Not Found",
                null,
                null,
            )

        assertThrows(BlobStorageException::class.java) {
            runBlocking { azureBlobClient.get(key) {} }
        }
    }

    @Test
    fun `getMetadata - returns metadata successfully`() = runBlocking {
        val key = "metadataBlob"
        val blobClient = mockk<BlobClient>()
        val blobProperties = mockk<BlobProperties>()
        val metadataMap = mapOf("author" to "azure", "version" to "1.0")

        every { containerClient.getBlobClient(key) } returns blobClient
        every { blobClient.properties } returns blobProperties
        every { blobProperties.metadata } returns metadataMap

        val result = azureBlobClient.getMetadata(key)
        assertEquals(metadataMap, result)
    }

    @Test
    fun `getMetadata - returns empty if properties is null`() = runBlocking {
        val key = "noMetadataBlob"
        val blobClient = mockk<BlobClient>()

        every { containerClient.getBlobClient(key) } returns blobClient
        every { blobClient.properties } returns null

        val result = azureBlobClient.getMetadata(key)
        assertTrue(result.isEmpty())
    }

    @Test
    fun `getMetadata - throws BlobStorageException if not found`(): Unit = runBlocking {
        val key = "missingBlob"
        val blobClient = mockk<BlobClient>()

        every { containerClient.getBlobClient(key) } returns blobClient
        every { blobClient.properties } throws BlobStorageException("Not Found", null, null)

        assertThrows(BlobStorageException::class.java) {
            runBlocking { azureBlobClient.getMetadata(key) }
        }
    }

    @Test
    fun `put - uploads byte array successfully`() = runBlocking {
        val key = "newBlob"
        val testBytes = "foo bar".toByteArray()
        val blobClient = mockk<BlobClient>()

        every { containerClient.getBlobClient(key) } returns blobClient
        every { blobClient.upload(any<BinaryData>(), eq(true)) } just runs

        val result = azureBlobClient.put(key, testBytes)
        assertEquals(key, result.key)
        assertEquals(blobConfig, result.storageConfig)

        verify(exactly = 1) {
            blobClient.upload(
                withArg { bd: BinaryData -> assertArrayEquals(testBytes, bd.toBytes()) },
                true,
            )
        }
    }

    @Test
    fun `put - throws exception if upload fails`(): Unit = runBlocking {
        val key = "failingBlob"
        val testBytes = "failing data".toByteArray()
        val blobClient = mockk<BlobClient>()

        every { containerClient.getBlobClient(key) } returns blobClient
        every {
            blobClient.upload(
                any<BinaryData>(),
                eq(true),
            )
        } throws BlobStorageException("Upload failed", null, null)

        assertThrows(BlobStorageException::class.java) {
            runBlocking { azureBlobClient.put(key, testBytes) }
        }
    }

    @Test
    fun `delete by remoteObject - deletes blob successfully`() = runBlocking {
        val blob = AzureBlob("deleteBlob", blobConfig)
        val blobClient = mockk<BlobClient>()

        every { containerClient.getBlobClient(blob.key) } returns blobClient
        every { blobClient.delete() } just runs

        azureBlobClient.delete(blob)
        verify(exactly = 1) { blobClient.delete() }
    }

    @Test
    fun `delete by key - ignore 404 not found`() = runBlocking {
        val key = "deleteKey"
        val blobClient = mockk<BlobClient>()
        val httpResponse = mockk<HttpResponse>()
        every { httpResponse.request } returns null
        every { httpResponse.statusCode } returns 404

        every { containerClient.getBlobClient(key) } returns blobClient
        every { blobClient.delete() } throws
            BlobStorageException(
                "Not Found",
                httpResponse,
                null,
            )

        // Should not throw
        azureBlobClient.delete(key)
    }

    @Test
    fun `delete by key - rethrow if not 404`(): Unit = runBlocking {
        val key = "forbiddenKey"
        val blobClient = mockk<BlobClient>()
        val httpResponse = mockk<HttpResponse>()
        every { httpResponse.request } returns null
        every { httpResponse.statusCode } returns 403

        every { containerClient.getBlobClient(key) } returns blobClient
        every { blobClient.delete() } throws
            BlobStorageException(
                "Forbidden",
                httpResponse,
                null,
            )

        assertThrows(BlobStorageException::class.java) {
            runBlocking { azureBlobClient.delete(key) }
        }
    }

    @Test
    fun `startStreamingUpload - returns AzureBlobStreamingUpload`() = runBlocking {
        val key = "streamKey"
        val metadata = mapOf("test" to "value")

        val blockBlobClient = mockk<BlockBlobClient>()
        val blobClient =
            mockk<BlobClient> { every { getBlockBlobClient() } returns blockBlobClient }

        every { containerClient.getBlobClient(key) } returns blobClient

        val streamingUpload = azureBlobClient.startStreamingUpload(key, metadata)

        assertNotNull(streamingUpload)
        assertTrue(streamingUpload is AzureBlobStreamingUpload)
    }

    @Test
    fun `startStreamingUpload - throws exception on invalid block blob client`(): Unit =
        runBlocking {
            val key = "invalidBlockBlob"
            val blobClient =
                mockk<BlobClient> {
                    every { getBlockBlobClient() } throws
                        BlobStorageException(
                            "Cannot get block blob client",
                            null,
                            null,
                        )
                }

            every { containerClient.getBlobClient(key) } returns blobClient

            assertThrows(
                BlobStorageException::class.java,
            ) {
                runBlocking { azureBlobClient.startStreamingUpload(key, emptyMap()) }
            }
        }
}
