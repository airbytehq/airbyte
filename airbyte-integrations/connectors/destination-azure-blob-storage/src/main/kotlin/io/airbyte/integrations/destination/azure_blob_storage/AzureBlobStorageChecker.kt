/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.file.azureBlobStorage.AzureBlobStorageClientFactory
import java.io.OutputStream
import javax.inject.Singleton
import kotlinx.coroutines.runBlocking

@Singleton
class AzureBlobStorageChecker<T : OutputStream> :
    DestinationChecker<AzureBlobStorageConfiguration<T>> {
    override fun check(config: AzureBlobStorageConfiguration<T>) {
        val azureBlobClient = AzureBlobStorageClientFactory(config).make()

        // Prepare test data
        val testData = "test".toByteArray()
        val checkFilePath = "check_test_data"

        runBlocking {
            // 1) Upload blob
            val checkBlob = azureBlobClient.put(checkFilePath, testData)

            try {
                // 2) Verify the blob exists by attempting to get metadata
                val metadata =
                    try {
                        azureBlobClient.getMetadata(checkFilePath)
                        true // If we reach this point, the blob exists
                    } catch (e: Exception) {
                        false // The blob doesn't exist
                    }

                check(metadata) { "Failed to verify blob existence after upload" }

                // 3) List blobs to verify the blob appears in the container
                var blobFound = false
                azureBlobClient.list(checkFilePath.substringBefore("/")).collect { blob ->
                    if (blob.key == checkFilePath) {
                        blobFound = true
                    }
                }

                check(blobFound) { "Uploaded blob not found in blob listing" }
            } finally {
                // 4) Clean up remote files
                azureBlobClient.delete(checkBlob)
            }
        }
    }
}
