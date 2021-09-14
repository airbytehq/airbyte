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
import static org.junit.jupiter.api.Assertions.assertNotNull;

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

  private JsonNode getFormatConfig() {
    return Jsons.deserialize("{\n"
        + "  \"format_type\": \"JSONL\"\n"
        + "}");
  }

}
