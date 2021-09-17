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

package io.airbyte.integrations.destination.jdbc.copy.azureblob;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Locale;

public class AzureBlobConfig {

  private final String endpointDomainName;
  private final String accountName;
  private final String accountKey;
  private final String containerName;
  private final String snowflakeAzureExternalStageName;

  public AzureBlobConfig(
    String endpointDomainName, 
    String accountName, 
    String accountKey, 
    String containerName,
    String snowflakeAzureExternalStageName
  ) {
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

  public static AzureBlobConfig getAzureBlobConfig(JsonNode config) {

    return new AzureBlobConfig(
      config.get("azure_blob_storage_endpoint_domain_name") == null ? "" : config.get("azure_blob_storage_endpoint_domain_name").asText(),    
      config.get("azure_blob_storage_account_name").asText(),
      config.get("azure_blob_storage_account_key").asText(),
      config.get("azure_blob_storage_container_name").asText(),
      config.get("snowflake_azure_external_stage_name").asText()
      );
  }

}
