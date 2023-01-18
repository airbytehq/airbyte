/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.BlobServiceClient;
import com.azure.storage.blob.BlobServiceClientBuilder;
import com.azure.storage.blob.specialized.SpecializedBlobClientBuilder;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.jdbc.copy.azure.AzureBlobStorageConfig;
import java.nio.file.Path;
import java.sql.SQLException;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.Disabled;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This test is disabled because we have not set up a Databricks cluster with Azure storage. This
 * issue is tracked in <a href="https://github.com/airbytehq/airbyte/issues/18026">#18026</a>.
 */
@Disabled
public class DatabricksAzureBlobStorageDestinationAcceptanceTest extends DatabricksDestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabricksAzureBlobStorageDestinationAcceptanceTest.class);
  private static final String SECRETS_CONFIG_JSON = "secrets/azure_config.json";

  private AzureBlobStorageConfig azureBlobStorageConfig;
  protected SpecializedBlobClientBuilder specializedBlobClientBuilder;

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode configJson = Jsons.clone(this.configJson);
    final JsonNode dataSource = configJson.get("data_source");
    ((ObjectNode) dataSource).put("azure_blob_storage_account_name", "someInvalidName");
    return configJson;
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) {
    final JsonNode baseConfigJson = Jsons.deserialize(IOs.readFile(Path.of(SECRETS_CONFIG_JSON)));

    // Set a random Azure path and database schema for each integration test
    final String randomString = RandomStringUtils.randomAlphanumeric(5);
    final JsonNode configJson = Jsons.clone(baseConfigJson);
    ((ObjectNode) configJson).put("database_schema", "integration_test_" + randomString);
    final JsonNode dataSource = configJson.get("data_source");
    ((ObjectNode) dataSource).put("azure_blob_storage_container_name", "test-" + randomString.toLowerCase());

    this.configJson = configJson;
    this.databricksConfig = DatabricksDestinationConfig.get(configJson);
    this.azureBlobStorageConfig = databricksConfig.getStorageConfig().getAzureBlobStorageConfigOrThrow();
    LOGGER.info("Test full path: {}/{}", azureBlobStorageConfig.getEndpointUrl(), azureBlobStorageConfig.getContainerName(),
        azureBlobStorageConfig);

    this.specializedBlobClientBuilder = new SpecializedBlobClientBuilder()
        .endpoint(azureBlobStorageConfig.getEndpointUrl())
        .sasToken(azureBlobStorageConfig.getSasToken())
        .containerName(
            azureBlobStorageConfig.getContainerName());// Like user\schema in DB
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws SQLException {
    final BlobServiceClient storageClient = new BlobServiceClientBuilder()
        .endpoint(azureBlobStorageConfig.getEndpointUrl())
        .sasToken(azureBlobStorageConfig.getSasToken())
        .buildClient();

    final BlobContainerClient blobContainerClient = storageClient
        .getBlobContainerClient(azureBlobStorageConfig.getContainerName());

    if (blobContainerClient.exists()) {
      LOGGER.info("Deleting test env: " + azureBlobStorageConfig.getContainerName());
      blobContainerClient.delete();
    }

    super.tearDown(testEnv);
  }

}
