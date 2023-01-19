/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class AzureBlobDestinationAcceptanceTest {

  protected final String secretFilePath = "secrets/config.json";
  private JsonNode config;

  @BeforeEach
  public void beforeAll() {
    final JsonNode configFomSecrets = Jsons.deserialize(IOs.readFile(Path.of(secretFilePath)));
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("azure_blob_storage_account_name", configFomSecrets.get("azure_blob_storage_account_name"))
        .put("azure_blob_storage_account_key", configFomSecrets.get("azure_blob_storage_account_key"))
        .put("azure_blob_storage_endpoint_domain_name", configFomSecrets.get("azure_blob_storage_endpoint_domain_name"))
        .put("format", getJsonlFormatConfig())
        .build());
  }

  @Test
  public void testCheck() {
    final AzureBlobStorageDestination azureBlobStorageDestination = new AzureBlobStorageDestination();
    final AirbyteConnectionStatus checkResult = azureBlobStorageDestination.check(config);

    assertEquals(Status.SUCCEEDED, checkResult.getStatus());
  }

  @Test
  public void testCheckInvalidAccountName() {
    final JsonNode invalidConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("azure_blob_storage_account_name", "someInvalidName")
        .put("azure_blob_storage_account_key", config.get("azure_blob_storage_account_key"))
        .put("format", getJsonlFormatConfig())
        .build());
    final AzureBlobStorageDestination azureBlobStorageDestination = new AzureBlobStorageDestination();
    final AirbyteConnectionStatus checkResult = azureBlobStorageDestination.check(invalidConfig);

    assertEquals(Status.FAILED, checkResult.getStatus());
  }

  @Test
  public void testCheckInvalidKey() {
    final JsonNode invalidConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("azure_blob_storage_account_name", config.get("azure_blob_storage_account_name"))
        .put("azure_blob_storage_account_key", "someInvalidKey")
        .put("format", getJsonlFormatConfig())
        .build());
    final AzureBlobStorageDestination azureBlobStorageDestination = new AzureBlobStorageDestination();
    final AirbyteConnectionStatus checkResult = azureBlobStorageDestination.check(invalidConfig);

    assertEquals(Status.FAILED, checkResult.getStatus());
  }

  @Test
  public void testCheckInvaliDomainName() {
    final JsonNode invalidConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("azure_blob_storage_account_name", config.get("azure_blob_storage_account_name"))
        .put("azure_blob_storage_account_key", config.get("azure_blob_storage_account_key"))
        .put("azure_blob_storage_endpoint_domain_name", "invalidDomain.com.invalid123")
        .put("format", getJsonlFormatConfig())
        .build());
    final AzureBlobStorageDestination azureBlobStorageDestination = new AzureBlobStorageDestination();
    final AirbyteConnectionStatus checkResult = azureBlobStorageDestination.check(invalidConfig);

    assertEquals(Status.FAILED, checkResult.getStatus());
  }

  private JsonNode getJsonlFormatConfig() {
    return Jsons.deserialize("{\n"
        + "  \"format_type\": \"JSONL\"\n"
        + "}");
  }

}
