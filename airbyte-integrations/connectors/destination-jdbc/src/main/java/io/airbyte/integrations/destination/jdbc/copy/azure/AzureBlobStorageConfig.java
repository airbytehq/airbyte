/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.azure;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Locale;

public class AzureBlobStorageConfig {

  private static final String DEFAULT_STORAGE_ENDPOINT_DOMAIN_NAME = "blob.core.windows.net";

  private final String endpointDomainName;
  private final String accountName;
  private final String containerName;
  private final String sasToken;

  public AzureBlobStorageConfig(
                                String endpointDomainName,
                                String accountName,
                                String containerName,
                                String sasToken) {
    this.endpointDomainName = endpointDomainName;
    this.accountName = accountName;
    this.containerName = containerName;
    this.sasToken = sasToken;
  }

  public String getEndpointDomainName() {
    return endpointDomainName == null ? DEFAULT_STORAGE_ENDPOINT_DOMAIN_NAME : endpointDomainName;
  }

  public String getAccountName() {
    return accountName;
  }

  public String getContainerName() {
    return containerName;
  }

  public String getSasToken() {
    return sasToken;
  }

  public String getEndpointUrl() {
    return String.format(Locale.ROOT, "https://%s.%s", getAccountName(), getEndpointDomainName());
  }

  public static AzureBlobStorageConfig getAzureBlobConfig(JsonNode config) {

    return new AzureBlobStorageConfig(
        config.get("azure_blob_storage_endpoint_domain_name") == null ? DEFAULT_STORAGE_ENDPOINT_DOMAIN_NAME
            : config.get("azure_blob_storage_endpoint_domain_name").asText(),
        config.get("azure_blob_storage_account_name").asText(),
        config.get("azure_blob_storage_container_name").asText(),
        config.get("azure_blob_storage_sas_token").asText());

  }

}
