/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_onelake

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.file.azureBlobStorage.AzureBlobStorageClientFactory
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.io.OutputStream
import kotlinx.coroutines.runBlocking

/**
 * Connection checker for the Microsoft OneLake destination.
 *
 * Validates connectivity and write access by uploading a small test blob under
 * Files/<subPath>/ and then cleaning it up. Metadata and listing verification
 * are best-effort only: OneLake's Blob API may not expose properties or listing
 * the same way as standard Azure Blob Storage, so a successful upload is sufficient
 * to pass the check.
 */
@Singleton
@Primary
class MicrosoftOneLakeChecker<T : OutputStream> :
    DestinationChecker<MicrosoftOneLakeConfiguration<T>> {

    override fun check(config: MicrosoftOneLakeConfiguration<T>) {
        // Re-use the Azure Blob Storage client pointed at the OneLake endpoint
        val client = AzureBlobStorageClientFactory(config).make()

        // Place the check file inside the configured Files/ prefix so we validate
        // that the service principal has write access to the correct Lakehouse path.
        val checkFilePath = "${config.objectStoragePathConfiguration.prefix}_airbyte_check_test"
        val testData = "airbyte-onelake-check".toByteArray()

        runBlocking {
            val checkBlob = client.put(checkFilePath, testData)

            try {
                // 1. Verify metadata if supported (OneLake may not expose blob properties immediately)
                try {
                    client.getMetadata(checkFilePath)
                } catch (e: Exception) {
                    System.err.println(
                        "[WARN] MicrosoftOneLakeChecker: could not get metadata for '$checkFilePath': ${e.message}. " +
                            "Upload succeeded; continuing."
                    )
                }

                // 2. Listing is best-effort; OneLake listing may differ from standard Blob API
                try {
                    var blobFound = false
                    client.list(checkFilePath.substringBefore("/")).collect { blob ->
                        if (blob.key == checkFilePath) blobFound = true
                    }
                    if (!blobFound) {
                        System.err.println(
                            "[WARN] MicrosoftOneLakeChecker: blob not found in listing at '${checkFilePath.substringBefore("/")}'. " +
                                "Upload succeeded; OneLake listing may differ."
                        )
                    }
                } catch (e: Exception) {
                    System.err.println(
                        "[WARN] MicrosoftOneLakeChecker: listing failed for '${checkFilePath.substringBefore("/")}': ${e.message}. " +
                            "Upload succeeded; continuing."
                    )
                }
            } finally {
                // Always clean up the test blob
                try {
                    client.delete(checkBlob)
                } catch (e: Exception) {
                    System.err.println(
                        "[WARN] MicrosoftOneLakeChecker: failed to delete check blob '$checkFilePath': ${e.message}"
                    )
                }
            }
        }
    }
}

