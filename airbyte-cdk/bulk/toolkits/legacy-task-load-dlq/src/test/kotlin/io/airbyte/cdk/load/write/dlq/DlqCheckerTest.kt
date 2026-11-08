/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.dlq

import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.check.dlq.DlqChecker
import io.airbyte.cdk.load.command.dlq.AzureBlobObjectStorageConfig
import io.airbyte.cdk.load.command.dlq.DisabledObjectStorageConfig
import io.airbyte.cdk.load.command.dlq.ObjectStorageSpec
import io.airbyte.cdk.load.command.dlq.toObjectStorageConfig
import io.airbyte.cdk.load.file.azureBlobStorage.AzureBlob
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.micronaut.context.BeanProvider
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import io.mockk.slot
import io.mockk.verify
import kotlinx.coroutines.flow.emptyFlow
import kotlinx.coroutines.flow.flowOf
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

class DlqCheckerTest {
    @Test
    fun `disabled storage never resolves a client`() {
        val provider = mockk<BeanProvider<ObjectStorageClient<*>>>()
        DlqChecker(provider).check(DisabledObjectStorageConfig())
        verify(exactly = 0) { provider.get() }
    }

    @ParameterizedTest
    @ValueSource(strings = ["present", "empty", "failure"])
    fun `Azure checker writes lists and cleans up even when listing fails`(listing: String) {
        val config =
            ValidatedJsonUtils.parseOne(
                    ObjectStorageSpec::class.java,
                    """{
                "storage_type":"AzureBlob",
                "azure_blob_storage_account_name":"testaccount",
                "azure_blob_storage_container_name":"rejected",
                "shared_access_signature":"test-sas",
                "bucket_path":"prefix"
            }""",
                )
                .toObjectStorageConfig() as AzureBlobObjectStorageConfig<*>
        val client = mockk<ObjectStorageClient<AzureBlob>>()
        val provider = mockk<BeanProvider<ObjectStorageClient<*>>>()
        every { provider.get() } returns client
        val upload = mockk<StreamingUpload<AzureBlob>>()
        val key = slot<String>()
        val bytes = slot<ByteArray>()
        coEvery { client.startStreamingUpload(capture(key), any()) } returns upload
        coEvery { upload.uploadPart(capture(bytes), 1) } returns Unit
        coEvery { upload.complete() } answers
            {
                AzureBlob(key.captured, config.azureBlobStorageClientConfiguration)
            }
        val listingError = IllegalStateException("listing failed")
        coEvery { client.list(any()) } answers
            {
                when (listing) {
                    "present" ->
                        flowOf(AzureBlob(key.captured, config.azureBlobStorageClientConfiguration))
                    "empty" -> emptyFlow()
                    else -> throw listingError
                }
            }
        coEvery { client.delete(any<AzureBlob>()) } returns Unit

        val checker = DlqChecker(provider)
        when (listing) {
            "present" -> checker.check(config)
            "empty" ->
                assertEquals(
                    "Failed to write to the object storage",
                    assertThrows(IllegalStateException::class.java) { checker.check(config) }
                        .message,
                )
            else ->
                assertEquals(
                    listingError,
                    assertThrows(IllegalStateException::class.java) { checker.check(config) },
                )
        }

        assertEquals("prefix/1/testing/test/_check_test", key.captured)
        assertEquals("""{"data":1}""", bytes.captured.toString(Charsets.UTF_8))
        coVerify(exactly = 1) {
            client.delete(AzureBlob(key.captured, config.azureBlobStorageClientConfiguration))
        }
    }
}
