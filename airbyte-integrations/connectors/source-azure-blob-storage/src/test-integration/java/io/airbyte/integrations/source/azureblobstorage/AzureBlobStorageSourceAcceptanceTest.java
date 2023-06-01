/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.azureblobstorage;

import com.azure.core.util.BinaryData;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.util.HashMap;

public class AzureBlobStorageSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final String STREAM_NAME = "airbyte-container";

  private AzureBlobStorageContainer azureBlobStorageContainer;

  private JsonNode jsonConfig;

  @Override
  protected String getImageName() {
    return "airbyte/source-azure-blob-storage:dev";
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return jsonConfig;
  }

  @Override
  protected void setupEnvironment(TestDestinationEnv environment) {
    azureBlobStorageContainer = new AzureBlobStorageContainer().withExposedPorts(10000);
    azureBlobStorageContainer.start();
    jsonConfig = AzureBlobStorageDataFactory.createAzureBlobStorageConfig(
        "http://127.0.0.1:" + azureBlobStorageContainer.getMappedPort(10000), STREAM_NAME);

    var azureBlobStorageConfig = AzureBlobStorageConfig.createAzureBlobStorageConfig(jsonConfig);
    var blobContainerClient = azureBlobStorageConfig.createBlobContainerClient();
    blobContainerClient.createIfNotExists();
    blobContainerClient.getBlobClient("FolderA/FolderB/blob1.json").upload(BinaryData.fromString("{\"attr1\":\"str_1\",\"attr2\":1}\n"));
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    azureBlobStorageContainer.stop();
    azureBlobStorageContainer.close();
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return AzureBlobStorageDataFactory.createConfiguredAirbyteCatalog(STREAM_NAME);
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

}
