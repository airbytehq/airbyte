/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.gcs

import com.google.cloud.storage.Blob
import com.google.cloud.storage.BlobId
import com.google.cloud.storage.BlobInfo
import com.google.cloud.storage.CopyWriter
import com.google.cloud.storage.Storage
import io.airbyte.cdk.load.command.gcs.GcsClientConfiguration
import io.airbyte.cdk.load.command.gcs.GcsHmacKeyConfiguration
import io.airbyte.cdk.load.command.gcs.GcsRegion
import io.mockk.every
import io.mockk.mockk
import io.mockk.slot
import io.mockk.verify
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class GcsClientTest {
    private val bucketName = "test-bucket"
    private val bucketPath = "test-path"
    private val region = GcsRegion.US_WEST1

    private fun mockBlob(mockName: String): Blob = mockk<Blob> { every { name } returns mockName }

    private val storage: Storage = mockk()
    private val config =
        GcsClientConfiguration(
            bucketName,
            bucketPath,
            GcsHmacKeyConfiguration("test-access-key", "test-secret-key"),
            region.region
        )
    private val gcsClient = GcsNativeClient(storage, config)

    @Test
    fun `test list with empty prefix`() = runBlocking {
        val prefix = ""
        val expectedFullPrefix = "$bucketName/$prefix"
        val blob1 = mockBlob("$expectedFullPrefix/test-file1")
        val blobs = listOf(blob1)

        every {
            storage.list(bucketName, Storage.BlobListOption.prefix(expectedFullPrefix))
        } returns mockk { every { iterateAll() } returns blobs }

        val results = gcsClient.list(prefix).toList()

        assertEquals(1, results.size)
        assertEquals("$expectedFullPrefix/test-file1", results[0].key)

        verify { storage.list(bucketName, Storage.BlobListOption.prefix(expectedFullPrefix)) }
    }

    @Test
    fun `test list with prefix`() = runBlocking {
        val prefix = "subfolder"
        val expectedFullPrefix = "$bucketName/$prefix"
        val blob1 = mockBlob("$expectedFullPrefix/test-file1")
        val blobs = listOf(blob1)

        every {
            storage.list(bucketName, Storage.BlobListOption.prefix(expectedFullPrefix))
        } returns mockk { every { iterateAll() } returns blobs }

        val results = gcsClient.list(prefix).toList()

        assertEquals(1, results.size)
        assertEquals("$expectedFullPrefix/test-file1", results[0].key)

        verify { storage.list(bucketName, Storage.BlobListOption.prefix(expectedFullPrefix)) }
    }

    @Test
    fun `test move`() = runBlocking {
        val sourceKey = "source-file"
        val targetKey = "target-file"
        val fullSourceKey = "$bucketPath/$sourceKey"
        val fullTargetKey = "$bucketPath/$targetKey"

        val sourceBlobId = BlobId.of(bucketName, fullSourceKey)
        val targetBlobId = BlobId.of(bucketName, fullTargetKey)
        val copyRequestSlot = slot<Storage.CopyRequest>()
        val copyWriter = mockk<CopyWriter>()

        every { storage.copy(capture(copyRequestSlot)) } returns copyWriter
        every { storage.delete(sourceBlobId) } returns true

        val result = gcsClient.move(sourceKey, targetKey)

        assertEquals(targetKey, result.key)
        assertEquals(config, result.storageConfig)

        assertEquals(sourceBlobId.bucket, copyRequestSlot.captured.source.bucket)
        assertEquals(sourceBlobId.name, copyRequestSlot.captured.source.name)
        assertEquals(targetBlobId.bucket, copyRequestSlot.captured.target.bucket)
        assertEquals(targetBlobId.name, copyRequestSlot.captured.target.name)

        verify { storage.delete(sourceBlobId) }
    }

    @Test
    fun `test move with remoteObject`() = runBlocking {
        val sourceKey = "source-file"
        val targetKey = "target-file"
        val fullSourceKey = "$bucketPath/$sourceKey"
        val fullTargetKey = "$bucketPath/$targetKey"

        val sourceBlobId = BlobId.of(bucketName, fullSourceKey)
        val targetBlobId = BlobId.of(bucketName, fullTargetKey)
        val copyRequestSlot = slot<Storage.CopyRequest>()
        val copyWriter = mockk<CopyWriter>()

        every { storage.copy(capture(copyRequestSlot)) } returns copyWriter
        every { storage.delete(sourceBlobId) } returns true

        val sourceBlob = GcsBlob(sourceKey, config)

        val result = gcsClient.move(sourceBlob, targetKey)

        assertEquals(targetKey, result.key)
        assertEquals(config, result.storageConfig)

        assertEquals(sourceBlobId.bucket, copyRequestSlot.captured.source.bucket)
        assertEquals(sourceBlobId.name, copyRequestSlot.captured.source.name)
        assertEquals(targetBlobId.bucket, copyRequestSlot.captured.target.bucket)
        assertEquals(targetBlobId.name, copyRequestSlot.captured.target.name)

        verify { storage.delete(sourceBlobId) }
    }

    @Test
    fun `test getMetadata`() = runBlocking {
        val key = "test-file"
        val fullKey = "$bucketPath/$key"
        val blobId = BlobId.of(bucketName, fullKey)
        val blob = mockk<Blob>()
        val metadata = mapOf("key1" to "value1", "key2" to "value2")

        every { storage.get(blobId) } returns blob
        every { blob.metadata } returns metadata

        val result = gcsClient.getMetadata(key)

        assertEquals(metadata, result)

        verify { storage.get(blobId) }
        verify { blob.metadata }
    }

    @Test
    fun `test getMetadata with null values`() = runBlocking {
        val key = "test-file"
        val fullKey = "$bucketPath/$key"
        val blobId = BlobId.of(bucketName, fullKey)
        val blob = mockk<Blob>()
        val metadata = mapOf("key1" to "value1", "key2" to null)

        every { storage.get(blobId) } returns blob
        every { blob.metadata } returns metadata

        val result = gcsClient.getMetadata(key)

        assertEquals(mapOf("key1" to "value1"), result)

        verify { storage.get(blobId) }
        verify { blob.metadata }
    }

    @Test
    fun `test getMetadata with null metadata`() = runBlocking {
        val key = "test-file"
        val fullKey = "$bucketPath/$key"
        val blobId = BlobId.of(bucketName, fullKey)
        val blob = mockk<Blob>()

        every { storage.get(blobId) } returns blob
        every { blob.metadata } returns null

        val result = gcsClient.getMetadata(key)

        assertEquals(emptyMap<String, String>(), result)

        verify { storage.get(blobId) }
        verify { blob.metadata }
    }

    @Test
    fun `test put`() = runBlocking {
        val key = "test-file"
        val fullKey = "$bucketPath/$key"
        val blobId = BlobId.of(bucketName, fullKey)
        val blobInfoSlot = slot<BlobInfo>()
        val content = "test content".toByteArray()
        val mockResultBlob = mockk<Blob>()
        every { mockResultBlob.name } returns fullKey

        every { storage.create(capture(blobInfoSlot), content) } returns mockResultBlob

        val result = gcsClient.put(key, content)

        assertEquals(key, result.key)
        assertEquals(config, result.storageConfig)
        assertEquals(blobId, blobInfoSlot.captured.blobId)

        verify { storage.create(any(), content) }
    }

    @Test
    fun `test delete with key`() = runBlocking {
        val key = "test-file"
        val fullKey = "$bucketPath/$key"
        val blobId = BlobId.of(bucketName, fullKey)

        every { storage.delete(blobId) } returns true

        gcsClient.delete(key)

        verify { storage.delete(blobId) }
    }

    @Test
    fun `test delete with remoteObject`() = runBlocking {
        val key = "test-file"
        val fullKey = "$bucketPath/$key"
        val blobId = BlobId.of(bucketName, fullKey)
        val blob = GcsBlob(key, config)

        every { storage.delete(blobId) } returns true

        gcsClient.delete(blob)

        verify { storage.delete(blobId) }
    }

    @Test
    fun `test combinePath with empty path`() = runBlocking {
        val config =
            GcsClientConfiguration(
                bucketName,
                "",
                GcsHmacKeyConfiguration("test-access-key", "test-secret-key"),
                region.region
            )
        val gcsClient = GcsNativeClient(storage, config)
        val key = "test-file"
        val blobId = BlobId.of(bucketName, key)

        every { storage.delete(blobId) } returns true

        gcsClient.delete(key)

        verify { storage.delete(blobId) }
    }

    @Test
    fun `test combinePath removes double slashes`() = runBlocking {
        val config =
            GcsClientConfiguration(
                bucketName,
                "path",
                GcsHmacKeyConfiguration("test-access-key", "test-secret-key"),
                region.region
            )
        val gcsClient = GcsNativeClient(storage, config)
        val key = "/test-file"

        val expectedPath = "path/test-file"
        val blobId = BlobId.of(bucketName, expectedPath)

        every { storage.delete(blobId) } returns true

        gcsClient.delete(key)

        verify { storage.delete(blobId) }
    }
}
