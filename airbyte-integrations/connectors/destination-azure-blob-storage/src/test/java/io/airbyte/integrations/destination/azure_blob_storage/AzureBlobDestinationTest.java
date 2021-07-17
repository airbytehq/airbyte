package io.airbyte.integrations.destination.azure_blob_storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.ConnectorSpecification;
import org.junit.jupiter.api.Test;

public class AzureBlobDestinationTest {

  @Test
  public void testConfigObjectCustomDomainName() {
    final JsonNode config = Jsons.jsonNode(ImmutableMap.builder()
        .put("azure_blob_storage_account_name", "accName")
        .put("azure_blob_storage_account_key", "accKey")
        .put("azure_blob_storage_endpoint_domain_name", "accDomainName.com")
        .build());
    final AzureBlobStorageDestinationConfig azureBlobStorageConfig = AzureBlobStorageDestinationConfig
        .getAzureBlobStorageConfig(config);

    assertEquals("https://accName.accDomainName.com",
        azureBlobStorageConfig.getEndpointUrl());
  }

  @Test
  public void testConfigObjectDefaultDomainName() {
    final JsonNode config = Jsons.jsonNode(ImmutableMap.builder()
        .put("azure_blob_storage_account_name", "accName")
        .put("azure_blob_storage_account_key", "accKey")
        .build());
    final AzureBlobStorageDestinationConfig azureBlobStorageConfig = AzureBlobStorageDestinationConfig
        .getAzureBlobStorageConfig(config);

    assertEquals("https://accName.blob.core.windows.net",
        azureBlobStorageConfig.getEndpointUrl());
  }

  @Test
  public void testConfigObjectDefaultBlobName() {
    final JsonNode config = Jsons.jsonNode(ImmutableMap.builder()
        .put("azure_blob_storage_account_name", "accName")
        .put("azure_blob_storage_account_key", "accKey")
        .build());
    final AzureBlobStorageDestinationConfig azureBlobStorageConfig = AzureBlobStorageDestinationConfig
        .getAzureBlobStorageConfig(config);

    assertEquals("airbyteblob", azureBlobStorageConfig.getBlobName());
  }

  @Test
  public void testConfigObjectDefaultContainerName() {
    final JsonNode config = Jsons.jsonNode(ImmutableMap.builder()
        .put("azure_blob_storage_account_name", "accName")
        .put("azure_blob_storage_account_key", "accKey")
        .build());
    final AzureBlobStorageDestinationConfig azureBlobStorageConfig = AzureBlobStorageDestinationConfig
        .getAzureBlobStorageConfig(config);

    assertEquals("airbytecontainer", azureBlobStorageConfig.getContainerName());
  }

  @Test
  public void testSpec() throws Exception {
    final AzureBlobStorageDestination azureBlobStorageDestination = new AzureBlobStorageDestination();
    final ConnectorSpecification spec = azureBlobStorageDestination.spec();
    final JsonNode connectionSpecification = spec.getConnectionSpecification();

    // if not fail and not null - then we have all mandatory params in schema
    AzureBlobStorageDestinationConfig properties = AzureBlobStorageDestinationConfig
        .getAzureBlobStorageConfig(connectionSpecification.get("properties"));

    assertNotNull(properties);
  }


}
