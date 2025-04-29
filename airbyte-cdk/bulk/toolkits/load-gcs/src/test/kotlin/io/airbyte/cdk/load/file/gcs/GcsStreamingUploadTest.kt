/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.gcs

import com.google.cloud.storage.BlobId
import com.google.cloud.storage.BlobInfo
import com.google.cloud.storage.Storage
import com.google.cloud.storage.Storage.ComposeRequest
import io.airbyte.cdk.load.command.gcs.GcsClientConfiguration
import io.airbyte.cdk.load.command.gcs.GcsHmacKeyConfiguration
import io.airbyte.cdk.load.command.gcs.GcsRegion
import io.mockk.every
import io.mockk.mockk
import io.mockk.slot
import io.mockk.verify
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class GcsStreamingUploadTest {

    private lateinit var storage: Storage
    private lateinit var config: GcsClientConfiguration
    private lateinit var key: String
    private lateinit var metadata: Map<String, String>
    private lateinit var streamingUpload: GcsStreamingUpload

    @BeforeEach
    fun setup() {
        storage = mockk()
        key = "test-object-key"
        config =
            GcsClientConfiguration(
                gcsBucketName = "test-bucket",
                path = "test-path",
                credential = GcsHmacKeyConfiguration("dummy-access-key", "dummy-secret-key"),
                region = GcsRegion.US_WEST1.region
            )
        metadata = mapOf("env" to "test", "author" to "testUser")
        streamingUpload = GcsStreamingUpload(storage, key, config, metadata)
    }

    @Test
    fun `uploadPart - uploads blob successfully`() = runBlocking {
        // Arrange
        val partData = "Hello GCS".toByteArray()
        val index = 1

        // Capture the BlobInfo and verify it later
        val blobInfoSlot = slot<BlobInfo>()
        every { storage.create(capture(blobInfoSlot), any<ByteArray>()) } returns mockk()

        // Act
        streamingUpload.uploadPart(partData, index)

        // Assert
        verify(exactly = 1) { storage.create(any(), partData) }

        // Verify the blob info has the correct bucket and path format
        val capturedBlobInfo = blobInfoSlot.captured
        assertTrue(capturedBlobInfo.name.contains("test-path"))
        assertTrue(capturedBlobInfo.name.contains("-part-1"))
        assertEquals("test-bucket", capturedBlobInfo.bucket)
    }

    @Test
    fun `complete - no parts uploaded, returns blob without composing`() = runBlocking {
        // Act
        val result = streamingUpload.complete()

        // Assert
        // No compose request should be made
        verify(exactly = 0) { storage.compose(any()) }

        // Should return a blob with the original key
        assertEquals(key, result.key)
        assertEquals(config, result.storageConfig)
    }

    @Test
    fun `complete - multiple parts uploaded, composes and cleans up parts`() = runBlocking {
        // Arrange
        // Mock successful part uploads
        every { storage.create(any(), any<ByteArray>()) } returns mockk()

        // Mock successful compose
        every { storage.compose(any()) } returns mockk()

        // Mock successful delete
        every { storage.delete(any<BlobId>()) } returns true

        // First, upload some parts
        streamingUpload.uploadPart("part1".toByteArray(), 0)
        streamingUpload.uploadPart("part2".toByteArray(), 1)
        streamingUpload.uploadPart("part3".toByteArray(), 2)

        // Capture the compose request
        val composeRequestSlot = slot<ComposeRequest>()
        every { storage.compose(capture(composeRequestSlot)) } returns mockk()

        // Act
        val result = streamingUpload.complete()

        // Assert
        // Compose should be called once
        verify(exactly = 1) { storage.compose(any()) }

        // Delete should be called for each part (3 times)
        verify(exactly = 3) { storage.delete(any<BlobId>()) }

        // The final blob should have our key
        assertEquals(key, result.key)
        assertEquals(config, result.storageConfig)

        // Verify compose request included target with metadata
        val capturedRequest = composeRequestSlot.captured
        val blobInfo = capturedRequest.target
        assertEquals(metadata, blobInfo.metadata)
        assertEquals("test-bucket", blobInfo.bucket)
        assertEquals(key, blobInfo.name)
    }

    @Test
    fun `uploadPart - throws when more than 32 parts uploaded`() = runBlocking {
        // Arrange - Set up 32 parts
        every { storage.create(any(), any<ByteArray>()) } returns mockk()

        // First, upload 32 parts (the maximum allowed)
        for (i in 0..31) {
            streamingUpload.uploadPart("data".toByteArray(), i)
        }

        // Act & Assert - the implementation should throw when trying to upload the 33rd part
        val exception =
            org.junit.jupiter.api.Assertions.assertThrows(IllegalStateException::class.java) {
                runBlocking { streamingUpload.uploadPart("data".toByteArray(), 32) }
            }

        // Verify message mentions the 32 part limit
        assertTrue(
            exception.message?.contains("32") ?: false,
            "Exception should mention 32 part limit"
        )
    }

    @Test
    fun `complete - is idempotent, only composes once`() = runBlocking {
        // Arrange
        // Mock successful part uploads
        every { storage.create(any(), any<ByteArray>()) } returns mockk()

        // Mock successful compose
        every { storage.compose(any()) } returns mockk()

        // Mock successful delete
        every { storage.delete(any<BlobId>()) } returns true

        // Upload a part
        streamingUpload.uploadPart("data".toByteArray(), 0)

        // Act - call complete twice
        val result1 = streamingUpload.complete()
        val result2 = streamingUpload.complete()

        // Assert
        // Compose should be called only once
        verify(exactly = 1) { storage.compose(any()) }

        // Both results should have the same key
        assertEquals(key, result1.key)
        assertEquals(key, result2.key)
    }

    @Test
    fun `combinePath - correctly combines paths`(): Unit = runBlocking {
        // Test with non-empty path
        val config1 =
            GcsClientConfiguration(
                gcsBucketName = "bucket",
                path = "prefix",
                credential = GcsHmacKeyConfiguration("dummy-access-key", "dummy-secret-key"),
                region = GcsRegion.US_WEST1.region
            )
        val upload1 = GcsStreamingUpload(storage, "key", config1, emptyMap())

        // Test without a path
        val config2 =
            GcsClientConfiguration(
                gcsBucketName = "bucket",
                path = "",
                credential = GcsHmacKeyConfiguration("dummy-access-key", "dummy-secret-key"),
                region = GcsRegion.US_WEST1.region
            )
        val upload2 = GcsStreamingUpload(storage, "key", config2, emptyMap())

        // Mock for uploadPart to work
        every { storage.create(any(), any<ByteArray>()) } returns mockk()

        // Act - calling uploadPart uses combinePath internally
        upload1.uploadPart("data".toByteArray(), 1)
        upload2.uploadPart("data".toByteArray(), 1)

        // Assert
        // Use list to capture all BlobInfo instances since there were multiple calls
        val blobInfoList = mutableListOf<BlobInfo>()

        verify(atLeast = 2) { storage.create(capture(blobInfoList), any<ByteArray>()) }

        // Check that at least one blob has prefix/ and at least one doesn't
        val prefixBlob = blobInfoList.find { it.name.contains("prefix/") }
        val nonPrefixBlob =
            blobInfoList.find { !it.name.contains("prefix/") && it.name.contains("key") }

        // Verify blob with prefix
        assertTrue(prefixBlob != null, "Expected to find a blob with 'prefix/' in name")
        prefixBlob?.let {
            assertEquals("bucket", it.bucket)
            assertTrue(it.name.contains("-part-"), "Expected part name to contain '-part-'")
        }

        // Verify blob without prefix
        assertTrue(nonPrefixBlob != null, "Expected to find a blob without 'prefix/' in name")
        nonPrefixBlob?.let {
            assertEquals("bucket", it.bucket)
            assertFalse(it.name.startsWith("/"), "Blob name should not start with '/'")
        }
    }

    @Test
    fun `uploadId - generates unique upload IDs`() {
        // Create multiple instances and verify upload IDs are different
        val upload1 = GcsStreamingUpload(storage, key, config, metadata)
        val upload2 = GcsStreamingUpload(storage, key, config, metadata)

        // Get the private uploadId field value using reflection
        val uploadIdField1 = GcsStreamingUpload::class.java.getDeclaredField("uploadId")
        uploadIdField1.isAccessible = true
        val uploadId1 = uploadIdField1.get(upload1) as String

        val uploadIdField2 = GcsStreamingUpload::class.java.getDeclaredField("uploadId")
        uploadIdField2.isAccessible = true
        val uploadId2 = uploadIdField2.get(upload2) as String

        // Assert they are different
        assertFalse(uploadId1 == uploadId2, "Upload IDs should be unique")

        // Assert they contain the key as a prefix
        assertTrue(uploadId1.startsWith(key), "Upload ID should start with the key")
        assertTrue(uploadId2.startsWith(key), "Upload ID should start with the key")
    }
}
