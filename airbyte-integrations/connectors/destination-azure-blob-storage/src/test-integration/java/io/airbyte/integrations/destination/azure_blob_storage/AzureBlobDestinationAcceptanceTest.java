/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.azure_blob_storage;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
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
