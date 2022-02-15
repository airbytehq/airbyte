/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.azure;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Locale;

public class AzureBlobStorageConfig {

  private final String endpointDomainName;
  private final String accountName;
  private final String accountKey;
  private final String containerName;
  private final String snowflakeAzureExternalStageName;

  public AzureBlobStorageConfig(
                                String endpointDomainName,
                                String accountName,
                                String accountKey,
                                String containerName,
                                String snowflakeAzureExternalStageName) {
    this.endpointDomainName = endpointDomainName;
    this.accountName = accountName;
    this.accountKey = accountKey;
    this.containerName = containerName;
    this.snowflakeAzureExternalStageName = snowflakeAzureExternalStageName;
  }

  public String getEndpointDomainName() {
    return endpointDomainName;
  }

  public String getAccountName() {
    return accountName;
  }

  public String getAccountKey() {
    return accountKey;
  }

  public String getContainerName() {
    return containerName;
  }

  public String getSnowflakeAzureExternalStageName() {
    return snowflakeAzureExternalStageName;
  }

  public String getEndpointUrl() {
    // The Java Azure client requires 'https' for the protocol. Snowflake requires 'azure'
    return String.format(Locale.ROOT, "https://%s.%s", getAccountName(), getEndpointDomainName());
  }

  public static AzureBlobStorageConfig getAzureBlobConfig(JsonNode config) {

    return new AzureBlobStorageConfig(
        config.get("azure_blob_storage_endpoint_domain_name") == null ? "" : config.get("azure_blob_storage_endpoint_domain_name").asText(),
        config.get("azure_blob_storage_account_name").asText(),
        config.get("azure_blob_storage_account_key").asText(),
        config.get("azure_blob_storage_container_name").asText(),
        config.get("snowflake_azure_external_stage_name").asText());
  }

}
