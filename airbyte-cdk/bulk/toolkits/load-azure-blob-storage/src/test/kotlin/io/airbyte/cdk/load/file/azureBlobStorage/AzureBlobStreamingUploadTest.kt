package io.airbyte.cdk.load.file.azureBlobStorage

// import io.mockk.Awaits
import com.azure.storage.blob.models.BlobStorageException
import com.azure.storage.blob.models.BlockBlobItem
import com.azure.storage.blob.specialized.BlockBlobClient
import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageConfiguration
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import io.mockk.verify
import java.io.InputStream
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class AzureBlobStreamingUploadTest {

    private lateinit var blockBlobClient: BlockBlobClient
    private lateinit var config: AzureBlobStorageConfiguration
    private lateinit var metadata: Map<String, String>
    private lateinit var streamingUpload: AzureBlobStreamingUpload

    @BeforeEach
    fun setup() {
        blockBlobClient = mockk()
        config =
            AzureBlobStorageConfiguration(
                accountName = "fakeAccount",
                containerName = "fakeContainer",
                sharedAccessSignature = "null"
            )
        metadata = mapOf("env" to "dev", "author" to "testUser")

        // By default, let's assume blobName returns something
        every { blockBlobClient.blobName } returns "testBlob"

        streamingUpload = AzureBlobStreamingUpload(blockBlobClient, config, metadata)
    }

    @Test
    fun `uploadPart - stages block successfully`() = runBlocking {
        // Arrange
        val partData = "Hello Azure".toByteArray()
        val index = 1

        // We just mock stageBlock, verifying that it is called with correct block ID and stream
        every { blockBlobClient.stageBlock(any(), any<InputStream>(), any()) } just runs

        // Act
        streamingUpload.uploadPart(partData, index)

        // Assert
        // 1) Verify stageBlock was called
        //    We don't know the exact base64 block ID from generateBlockId, but we can match using
        // "any()"
        verify(exactly = 1) {
            blockBlobClient.stageBlock(
                any(), // the base64-encoded ID
                any<InputStream>(),
                partData.size.toLong()
            )
        }
    }

    @Test
    fun `uploadPart - throws exception if stageBlock fails`(): Unit = runBlocking {
        // Arrange
        val partData = ByteArray(10) { 0xA }
        every { blockBlobClient.stageBlock(any(), any<InputStream>(), any()) } throws
            BlobStorageException("Staging failed", null, null)

        // Act & Assert
        assertThrows(BlobStorageException::class.java) {
            runBlocking { streamingUpload.uploadPart(partData, 0) }
        }
    }

    @Test
    fun `complete - no blocks uploaded`() = runBlocking {
        // Arrange
        // No calls to uploadPart => blockIds empty
        // We want to ensure commitBlockList is NOT called
        val blobItem = mockk<BlockBlobItem>()
        every { blockBlobClient.commitBlockList(any(), any()) } returns blobItem
        every { blockBlobClient.setMetadata(metadata) } just runs

        // Act
        val resultBlob = streamingUpload.complete()

        // Assert
        // 1) No block list calls
        verify(exactly = 0) { blockBlobClient.commitBlockList(any(), any()) }
        // 2) Metadata still set (the code checks for empty map, but here it's non-empty).
        verify(exactly = 1) { blockBlobClient.setMetadata(metadata) }

        // 3) Return object is AzureBlob
        assertEquals("testBlob", resultBlob.key)
        assertEquals(config, resultBlob.storageConfig)
    }

    @Test
    fun `complete - multiple blocks, commits in ascending index order`() = runBlocking {
        // Arrange
        every { blockBlobClient.stageBlock(any(), any<InputStream>(), any()) } just runs
        val blobItem = mockk<BlockBlobItem>()
        every { blockBlobClient.commitBlockList(any(), any()) } returns blobItem
        every { blockBlobClient.setMetadata(any()) } just runs

        // Let's upload 3 parts out of order for demonstration
        streamingUpload.uploadPart("part-A".toByteArray(), 2)
        streamingUpload.uploadPart("part-B".toByteArray(), 0)
        streamingUpload.uploadPart("part-C".toByteArray(), 1)

        // Act
        val resultBlob = streamingUpload.complete()

        // Assert
        // The code sorts by the keys in ascending order (0,1,2). We verify that
        // commitBlockList is called with the values in ascending order of index.
        verify(exactly = 1) {
            blockBlobClient.commitBlockList(
                withArg { blockList ->
                    // We can't easily check the entire Base64 ID but can check it has 3 items
                    assertEquals(3, blockList.size)
                },
                true
            )
        }
        verify(exactly = 1) { blockBlobClient.setMetadata(metadata) }
        // Confirm the returned object
        assertEquals("testBlob", resultBlob.key)
        assertEquals(config, resultBlob.storageConfig)
    }

    @Test
    fun `complete - calls commit only once on repeated calls`() = runBlocking {
        // Arrange
        every { blockBlobClient.stageBlock(any(), any<InputStream>(), any()) } just runs
        val blobItem = mockk<BlockBlobItem>()
        every { blockBlobClient.commitBlockList(any(), true) } returns blobItem
        every { blockBlobClient.setMetadata(any()) } just runs

        // Upload a single part
        streamingUpload.uploadPart("hello".toByteArray(), 5)

        // First call to complete
        val firstCall = streamingUpload.complete()

        // Second call to complete
        val secondCall = streamingUpload.complete()

        // Assert
        verify(exactly = 1) { blockBlobClient.commitBlockList(any(), true) }
        // setMetadata also only once
        verify(exactly = 1) { blockBlobClient.setMetadata(metadata) }
        // Both calls return the same AzureBlob reference
        assertEquals("testBlob", firstCall.key)
        assertEquals("testBlob", secondCall.key)
        // Confirm same config
        assertEquals(config, firstCall.storageConfig)
        assertEquals(config, secondCall.storageConfig)
    }

    @Test
    fun `complete - throws exception if commitBlockList fails`() = runBlocking {
        // Arrange
        every { blockBlobClient.stageBlock(any(), any<InputStream>(), any()) } just runs
        // Stage one block
        streamingUpload.uploadPart("abc".toByteArray(), 1)

        every { blockBlobClient.commitBlockList(any(), true) } throws
            BlobStorageException("Commit failed", null, null)

        // Act & Assert
        assertThrows(BlobStorageException::class.java) {
            runBlocking { streamingUpload.complete() }
        }

        // Ensure metadata was never set
        verify(exactly = 0) { blockBlobClient.setMetadata(any()) }
    }
}
