/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
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
import io.airbyte.cdk.load.command.gcs.GcsWorkloadIdentityFederationConfiguration
import io.mockk.every
import io.mockk.mockk
import io.mockk.slot
import io.mockk.verify
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertInstanceOf
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

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
            region.region,
        )
    private val gcsClient = GcsNativeClient(storage, config)

    @Test
    fun `test list with empty prefix`() = runBlocking {
        val prefix = ""
        val expectedFullPrefix = prefix
        val blob1 = mockBlob("$bucketPath/test-file1")
        val blobs = listOf(blob1)

        every {
            storage.list(bucketName, Storage.BlobListOption.prefix(expectedFullPrefix))
        } returns mockk { every { iterateAll() } returns blobs }

        val results = gcsClient.list(prefix).toList()

        assertEquals(1, results.size)
        assertEquals("$bucketPath/test-file1", results[0].key)

        verify { storage.list(bucketName, Storage.BlobListOption.prefix(expectedFullPrefix)) }
    }

    @Test
    fun `test list with prefix`() = runBlocking {
        // Keys and prefixes are full object names: neither the bucket name nor the bucket path is
        // prepended.
        val prefix = "$bucketPath/subfolder"
        val expectedFullPrefix = prefix
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
        val sourceKey = "$bucketPath/source-file"
        val targetKey = "$bucketPath/target-file"
        val fullSourceKey = sourceKey
        val fullTargetKey = targetKey

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
        val sourceKey = "$bucketPath/source-file"
        val targetKey = "$bucketPath/target-file"
        val fullSourceKey = sourceKey
        val fullTargetKey = targetKey

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
        val key = "$bucketPath/test-file"
        val fullKey = key
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
        val key = "$bucketPath/test-file"
        val fullKey = key
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
        val key = "$bucketPath/test-file"
        val fullKey = key
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
        val key = "$bucketPath/test-file"
        val fullKey = key
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
        val key = "$bucketPath/test-file"
        val fullKey = key
        val blobId = BlobId.of(bucketName, fullKey)

        every { storage.delete(blobId) } returns true

        gcsClient.delete(key)

        verify { storage.delete(blobId) }
    }

    @Test
    fun `test delete with remoteObject`() = runBlocking {
        val key = "$bucketPath/test-file"
        val fullKey = key
        val blobId = BlobId.of(bucketName, fullKey)
        val blob = GcsBlob(key, config)

        every { storage.delete(blobId) } returns true

        gcsClient.delete(blob)

        verify { storage.delete(blobId) }
    }

    @Test
    fun `test delete multiple keys`() = runBlocking {
        val key1 = "$bucketPath/test-file-1"
        val key2 = "$bucketPath/test-file-2"
        val blobIds = setOf(BlobId.of(bucketName, key1), BlobId.of(bucketName, key2))

        every { storage.delete(*blobIds.toTypedArray()) } returns listOf(true, true)

        gcsClient.delete(setOf(key1, key2))

        verify { storage.delete(*blobIds.toTypedArray()) }
    }

    @Test
    fun `test keys are not prefixed with the bucket path`() = runBlocking {
        // The pipeline passes keys that already include the bucket path; prepending it again would
        // write to "test-path/test-path/...".
        val key = "$bucketPath/stream/file.jsonl"
        val blobId = BlobId.of(bucketName, key)

        every { storage.delete(blobId) } returns true

        gcsClient.delete(key)

        verify { storage.delete(blobId) }
        verify(exactly = 0) { storage.delete(BlobId.of(bucketName, "$bucketPath/$key")) }
    }

    @Test
    fun `test get throws when the object does not exist`() {
        val key = "$bucketPath/missing"
        every { storage.get(BlobId.of(bucketName, key)) } returns null

        assertThrows<NoSuchElementException> { runBlocking { gcsClient.getMetadata(key) } }
    }

    @Test
    fun `test factory builds a native client for workload identity federation`() {
        val wifConfig =
            config.copy(
                credential =
                    GcsWorkloadIdentityFederationConfiguration.fromCredentialsJson(
                        """
                        {
                          "type": "external_account",
                          "audience": "//iam.googleapis.com/projects/1/locations/global/workloadIdentityPools/p/providers/q",
                          "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
                          "token_url": "https://sts.googleapis.com/v1/token",
                          "credential_source": {"file": "/var/run/token"}
                        }
                        """
                            .trimIndent(),
                    ),
            )

        assertInstanceOf(GcsNativeClient::class.java, GcsClientFactory.make(wifConfig))
    }

    @Test
    fun `test factory builds an S3 client for HMAC keys`() {
        assertInstanceOf(GcsS3Client::class.java, GcsClientFactory.make(config))
    }
}
