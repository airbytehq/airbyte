/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.azureblobstorage;

import static org.assertj.core.api.Assertions.assertThat;

import com.azure.core.util.BinaryData;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.Iterator;
import java.util.List;
import java.util.stream.Stream;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class AzureBlobStorageSourceTest {

  private AzureBlobStorageSource azureBlobStorageSource;

  private AzureBlobStorageContainer azureBlobStorageContainer;

  private JsonNode jsonConfig;

  private static final String STREAM_NAME = "airbyte-container";

  @BeforeEach
  void setup() {
    azureBlobStorageContainer = new AzureBlobStorageContainer().withExposedPorts(10000);
    azureBlobStorageContainer.start();
    azureBlobStorageSource = new AzureBlobStorageSource();
    jsonConfig = AzureBlobStorageDataFactory.createAzureBlobStorageConfig(
        "http://127.0.0.1:" + azureBlobStorageContainer.getMappedPort(10000), STREAM_NAME);

    var azureBlobStorageConfig = AzureBlobStorageConfig.createAzureBlobStorageConfig(jsonConfig);
    var blobContainerClient = azureBlobStorageConfig.createBlobContainerClient();
    blobContainerClient.createIfNotExists();
    blobContainerClient.getBlobClient("FolderA/FolderB/blob1.json")
        .upload(BinaryData.fromString("{\"attr_1\":\"str_1\"}\n"));
    blobContainerClient.getBlobClient("FolderA/FolderB/blob2.json")
        .upload(BinaryData.fromString("{\"attr_2\":\"str_2\"}\n"));
    // blob in ignored path
    blobContainerClient.getBlobClient("FolderA/blob3.json").upload(BinaryData.fromString("{}"));
  }

  @AfterEach
  void tearDown() {
    azureBlobStorageContainer.stop();
    azureBlobStorageContainer.close();
  }

  @Test
  void testCheckConnectionWithSucceeded() {
    var airbyteConnectionStatus = azureBlobStorageSource.check(jsonConfig);

    assertThat(airbyteConnectionStatus.getStatus()).isEqualTo(AirbyteConnectionStatus.Status.SUCCEEDED);

  }

  @Test
  void testCheckConnectionWithFailed() {

    var failingConfig = AzureBlobStorageDataFactory.createAzureBlobStorageConfig(
        "http://127.0.0.1:" + azureBlobStorageContainer.getMappedPort(10000), "missing-container");

    var airbyteConnectionStatus = azureBlobStorageSource.check(failingConfig);

    assertThat(airbyteConnectionStatus.getStatus()).isEqualTo(AirbyteConnectionStatus.Status.FAILED);

  }

  @Test
  void testDiscover() {
    var airbyteCatalog = azureBlobStorageSource.discover(jsonConfig);

    assertThat(airbyteCatalog.getStreams())
        .hasSize(1)
        .element(0)
        .hasFieldOrPropertyWithValue("name", STREAM_NAME)
        .hasFieldOrPropertyWithValue("sourceDefinedCursor", true)
        .hasFieldOrPropertyWithValue("defaultCursorField", List.of(AzureBlobAdditionalProperties.LAST_MODIFIED))
        .hasFieldOrPropertyWithValue("supportedSyncModes", List.of(SyncMode.INCREMENTAL, SyncMode.FULL_REFRESH))
        .extracting("jsonSchema")
        .isNotNull();

  }

  @Test
  void testRead() {
    var configuredAirbyteCatalog = AzureBlobStorageDataFactory.createConfiguredAirbyteCatalog(STREAM_NAME);

    Iterator<AirbyteMessage> iterator =
        azureBlobStorageSource.read(jsonConfig, configuredAirbyteCatalog, Jsons.emptyObject());

    var airbyteRecordMessages = Stream.generate(() -> null)
        .takeWhile(x -> iterator.hasNext())
        .map(n -> iterator.next())
        .filter(am -> am.getType() == AirbyteMessage.Type.RECORD)
        .map(AirbyteMessage::getRecord)
        .toList();

    assertThat(airbyteRecordMessages)
        .hasSize(2)
        .anyMatch(arm -> arm.getStream().equals(STREAM_NAME) &&
            Jsons.serialize(arm.getData()).contains(
                "\"attr_1\":\"str_1\""))
        .anyMatch(arm -> arm.getStream().equals(STREAM_NAME) &&
            Jsons.serialize(arm.getData()).contains(
                "\"attr_2\":\"str_2\""));

  }

}
