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

import static io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageDestinationConstants.*;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Locale;

public class AzureBlobStorageDestinationConfig {

  private final String endpointUrl;
  private final String accountName;
  private final String accountKey;
  private final String containerName;
  private final AzureBlobStorageFormatConfig formatConfig;

  public AzureBlobStorageDestinationConfig(
                                           String endpointUrl,
                                           String accountName,
                                           String accountKey,
                                           String containerName,
                                           AzureBlobStorageFormatConfig formatConfig) {
    this.endpointUrl = endpointUrl;
    this.accountName = accountName;
    this.accountKey = accountKey;
    this.containerName = containerName;
    this.formatConfig = formatConfig;
  }

  public String getEndpointUrl() {
    return endpointUrl;
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

  public AzureBlobStorageFormatConfig getFormatConfig() {
    return formatConfig;
  }

  public static AzureBlobStorageDestinationConfig getAzureBlobStorageConfig(JsonNode config) {
    final String accountNameFomConfig = config.get("azure_blob_storage_account_name").asText();
    final String accountKeyFromConfig = config.get("azure_blob_storage_account_key").asText();
    final JsonNode endpointFromConfig = config
        .get("azure_blob_storage_endpoint_domain_name");
    final JsonNode containerName = config.get("azure_blob_storage_container_name");
    final JsonNode blobName = config.get("azure_blob_storage_blob_name"); // streamId

    final String endpointComputed = String.format(Locale.ROOT, DEFAULT_STORAGE_ENDPOINT_FORMAT,
        DEFAULT_STORAGE_ENDPOINT_HTTP_PROTOCOL,
        accountNameFomConfig,
        endpointFromConfig == null ? DEFAULT_STORAGE_ENDPOINT_DOMAIN_NAME
            : endpointFromConfig.asText());

    final String containerNameComputed =
        containerName == null ? DEFAULT_STORAGE_CONTAINER_NAME : containerName.asText();

    return new AzureBlobStorageDestinationConfig(
        endpointComputed,
        accountNameFomConfig,
        accountKeyFromConfig,
        containerNameComputed,
        AzureBlobStorageFormatConfigs.getAzureBlobStorageFormatConfig(config));
  }

}
