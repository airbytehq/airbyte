/*
 * Binds the AzureBlobStorageClientConfigurationProvider interface to the
 * MicrosoftOneLakeConfiguration so that the shared AzureBlobStorageClientFactory
 * always uses the OneLake configuration in this connector.
 */

package io.airbyte.integrations.destination.azure_onelake

import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageClientConfiguration
import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageClientConfigurationProvider
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.io.OutputStream

@Singleton
@Primary
class MicrosoftOneLakeAzureClientConfigProvider(
    private val config: MicrosoftOneLakeConfiguration<out OutputStream>
) : AzureBlobStorageClientConfigurationProvider {

    override val azureBlobStorageClientConfiguration: AzureBlobStorageClientConfiguration
        get() = config.azureBlobStorageClientConfiguration
}

