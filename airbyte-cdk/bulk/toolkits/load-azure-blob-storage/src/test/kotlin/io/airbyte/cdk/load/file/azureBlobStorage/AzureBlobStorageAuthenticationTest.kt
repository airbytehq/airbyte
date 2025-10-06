/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.azureBlobStorage

import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageClientConfiguration
import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageClientConfigurationProvider
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow

class AzureBlobStorageAuthenticationTest {

    @Test
    fun testAccountKeyAuthentication() {
        val config =
            AzureBlobStorageClientConfiguration(
                accountName = "testaccount",
                containerName = "testcontainer",
                sharedAccessSignature = null,
                accountKey = "testkey123",
                tenantId = null,
                clientId = null,
                clientSecret = null
            )

        assertDoesNotThrow { config }
    }

    @Test
    fun testSasTokenAuthentication() {
        val config =
            AzureBlobStorageClientConfiguration(
                accountName = "testaccount",
                containerName = "testcontainer",
                sharedAccessSignature = "sv=2021-08-06&st=2025-04-11T00%3A00%3A00Z",
                accountKey = null,
                tenantId = null,
                clientId = null,
                clientSecret = null
            )

        assertDoesNotThrow { config }
    }

    @Test
    fun testEntraIdAuthentication() {
        val config =
            AzureBlobStorageClientConfiguration(
                accountName = "testaccount",
                containerName = "testcontainer",
                sharedAccessSignature = null,
                accountKey = null,
                tenantId = "12345678-1234-1234-1234-123456789012",
                clientId = "87654321-4321-4321-4321-210987654321",
                clientSecret = "testsecret"
            )

        assertDoesNotThrow { config }
    }

    @Test
    fun testNoAuthenticationProvided() {
        assertThrows(IllegalStateException::class.java) {
            AzureBlobStorageClientConfiguration(
                accountName = "testaccount",
                containerName = "testcontainer",
                sharedAccessSignature = null,
                accountKey = null,
                tenantId = null,
                clientId = null,
                clientSecret = null
            )
        }
    }

    @Test
    fun testMultipleAuthenticationMethods() {
        assertThrows(IllegalStateException::class.java) {
            AzureBlobStorageClientConfiguration(
                accountName = "testaccount",
                containerName = "testcontainer",
                sharedAccessSignature = "sv=2021-08-06&st=2025-04-11T00%3A00%3A00Z",
                accountKey = "testkey123",
                tenantId = null,
                clientId = null,
                clientSecret = null
            )
        }
    }

    @Test
    fun testIncompleteEntraIdAuthentication() {
        assertThrows(IllegalStateException::class.java) {
            AzureBlobStorageClientConfiguration(
                accountName = "testaccount",
                containerName = "testcontainer",
                sharedAccessSignature = null,
                accountKey = null,
                tenantId = "12345678-1234-1234-1234-123456789012",
                clientId = "87654321-4321-4321-4321-210987654321",
                clientSecret = null
            )
        }
    }

    @Test
    fun testClientFactoryWithAccountKey() {
        val config =
            AzureBlobStorageClientConfiguration(
                accountName = "testaccount",
                containerName = "testcontainer",
                sharedAccessSignature = null,
                accountKey = "testkey123",
                tenantId = null,
                clientId = null,
                clientSecret = null
            )

        val provider =
            mockk<AzureBlobStorageClientConfigurationProvider> {
                every { azureBlobStorageClientConfiguration } returns config
            }

        val factory = AzureBlobStorageClientFactory(provider)

        assertDoesNotThrow { factory.make() }
    }

    @Test
    fun testClientFactoryWithSasToken() {
        val config =
            AzureBlobStorageClientConfiguration(
                accountName = "testaccount",
                containerName = "testcontainer",
                sharedAccessSignature = "sv=2021-08-06&st=2025-04-11T00%3A00%3A00Z",
                accountKey = null,
                tenantId = null,
                clientId = null,
                clientSecret = null
            )

        val provider =
            mockk<AzureBlobStorageClientConfigurationProvider> {
                every { azureBlobStorageClientConfiguration } returns config
            }

        val factory = AzureBlobStorageClientFactory(provider)

        assertDoesNotThrow { factory.make() }
    }

    @Test
    fun testClientFactoryWithEntraId() {
        val config =
            AzureBlobStorageClientConfiguration(
                accountName = "testaccount",
                containerName = "testcontainer",
                sharedAccessSignature = null,
                accountKey = null,
                tenantId = "12345678-1234-1234-1234-123456789012",
                clientId = "87654321-4321-4321-4321-210987654321",
                clientSecret = "testsecret"
            )

        val provider =
            mockk<AzureBlobStorageClientConfigurationProvider> {
                every { azureBlobStorageClientConfiguration } returns config
            }

        val factory = AzureBlobStorageClientFactory(provider)

        assertDoesNotThrow { factory.make() }
    }

    @Test
    fun testClientFactoryWithNoAuthentication() {
        assertThrows(IllegalStateException::class.java) {
            AzureBlobStorageClientConfiguration(
                accountName = "testaccount",
                containerName = "testcontainer",
                sharedAccessSignature = null,
                accountKey = null,
                tenantId = null,
                clientId = null,
                clientSecret = null
            )
        }
    }
}
