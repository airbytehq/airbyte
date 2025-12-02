/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc.copy.azure

import com.fasterxml.jackson.databind.JsonNode
import java.util.*

class AzureBlobStorageConfig(
    val endpointDomainName: String = DEFAULT_STORAGE_ENDPOINT_DOMAIN_NAME,
    val accountName: String,
    val containerName: String,
    val sasToken: String
) {

    val endpointUrl: String
        get() = String.format(Locale.ROOT, "https://%s.%s", accountName, endpointDomainName)

    companion object {
        private const val DEFAULT_STORAGE_ENDPOINT_DOMAIN_NAME = "blob.core.windows.net"

        fun getAzureBlobConfig(config: JsonNode): AzureBlobStorageConfig {
            return AzureBlobStorageConfig(
                if (config["azure_blob_storage_endpoint_domain_name"] == null)
                    DEFAULT_STORAGE_ENDPOINT_DOMAIN_NAME
                else config["azure_blob_storage_endpoint_domain_name"].asText(),
                config["azure_blob_storage_account_name"].asText(),
                config["azure_blob_storage_container_name"].asText(),
                config["azure_blob_storage_sas_token"].asText()
            )
        }
    }
}
