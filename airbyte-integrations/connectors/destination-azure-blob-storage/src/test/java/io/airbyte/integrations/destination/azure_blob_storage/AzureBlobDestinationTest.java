/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import org.junit.jupiter.api.Test;

public class AzureBlobDestinationTest {

  @Test
  public void testConfigObjectCustomDomainName() {
    final JsonNode config = Jsons.jsonNode(ImmutableMap.builder()
        .put("azure_blob_storage_account_name", "accName")
        .put("azure_blob_storage_account_key", "accKey")
        .put("azure_blob_storage_endpoint_domain_name", "accDomainName.com")
        .put("format", getFormatConfig())
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
        .put("format", getFormatConfig())
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
        .put("format", getFormatConfig())
        .build());
    final AzureBlobStorageDestinationConfig azureBlobStorageConfig =
        AzureBlobStorageDestinationConfig
            .getAzureBlobStorageConfig(config);

    assertNotNull(azureBlobStorageConfig);
  }

  @Test
  public void testConfigObjectDefaultContainerName() {
    final JsonNode config = Jsons.jsonNode(ImmutableMap.builder()
        .put("azure_blob_storage_account_name", "accName")
        .put("azure_blob_storage_account_key", "accKey")
        .put("format", getFormatConfig())
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

    assertNotNull(connectionSpecification);
  }

  @Test
  public void testConfigObjectCustomOutputBufferSize() {
    final JsonNode config = Jsons.jsonNode(ImmutableMap.builder()
        .put("azure_blob_storage_account_name", "accName")
        .put("azure_blob_storage_account_key", "accKey")
        .put("azure_blob_storage_endpoint_domain_name", "accDomainName.com")
        .put("azure_blob_storage_output_buffer_size", 10)
        .put("format", getFormatConfig())
        .build());
    final AzureBlobStorageDestinationConfig azureBlobStorageConfig = AzureBlobStorageDestinationConfig
        .getAzureBlobStorageConfig(config);

    assertEquals(10 * 1024 * 1024,
        azureBlobStorageConfig.getOutputStreamBufferSize());
  }

  @Test
  void testConfigBlobStorageSpillSize() {
    final JsonNode config = Jsons.jsonNode(ImmutableMap.builder()
        .put("azure_blob_storage_account_name", "accName")
        .put("azure_blob_storage_account_key", "accKey")
        .put("azure_blob_storage_endpoint_domain_name", "accDomainName.com")
        .put("azure_blob_storage_output_buffer_size", 10)
        .put("azure_blob_storage_spill_size", 500)
        .put("format", getFormatConfig())
        .build());

    final AzureBlobStorageDestinationConfig azureBlobStorageConfig = AzureBlobStorageDestinationConfig
        .getAzureBlobStorageConfig(config);

    assertEquals((long) 500 * 1024 * 1024,
        azureBlobStorageConfig.getBlobSpillSize());
  }

  private JsonNode getFormatConfig() {
    return Jsons.deserialize("{\n"
        + "  \"format_type\": \"JSONL\",\n"
        + "  \"file_extension\": \"true\"\n"
        + "}");
  }

}
