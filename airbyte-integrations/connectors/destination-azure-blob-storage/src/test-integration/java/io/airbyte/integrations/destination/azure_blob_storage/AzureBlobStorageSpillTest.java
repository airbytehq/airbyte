/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage;

import static org.assertj.core.api.Assertions.assertThat;

import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.BlobContainerClientBuilder;
import com.azure.storage.common.StorageSharedKeyCredential;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.azure_blob_storage.jsonl.AzureBlobStorageJsonlFormatConfig;
import io.airbyte.integrations.destination.azure_blob_storage.writer.ProductionWriterFactory;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.Instant;
import java.util.List;
import java.util.function.Function;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class AzureBlobStorageSpillTest {

  private static final String AIRBYTE_NAMESPACE = "airbyte_namespace";

  private static final String AIRBYTE_STREAM = "airbyte_stream";

  private AzureBlobStorageContainer azureBlobStorageContainer;

  private AzureBlobStorageConsumer azureBlobStorageConsumer;

  private BlobContainerClient blobContainerClient;

  private static final ObjectMapper mapper = MoreMappers.initMapper();

  @BeforeEach
  void setup() {
    azureBlobStorageContainer = new AzureBlobStorageContainer().withExposedPorts(10000);
    azureBlobStorageContainer.start();
    var azureBlobStorageDestinationConfig = createConfig(azureBlobStorageContainer.getHost(), azureBlobStorageContainer.getMappedPort(10000));
    var configuredAirbyteCatalog = createConfiguredAirbyteCatalog();
    azureBlobStorageConsumer =
        new AzureBlobStorageConsumer(azureBlobStorageDestinationConfig, configuredAirbyteCatalog,
            new ProductionWriterFactory(), m -> {});
    var credential = new StorageSharedKeyCredential(
        azureBlobStorageDestinationConfig.getAccountName(),
        azureBlobStorageDestinationConfig.getAccountKey());

    blobContainerClient = new BlobContainerClientBuilder()
        .endpoint(azureBlobStorageDestinationConfig.getEndpointUrl())
        .credential(credential)
        .containerName(azureBlobStorageDestinationConfig.getContainerName())
        .buildClient();

  }

  @AfterEach
  void tearDown() {
    azureBlobStorageContainer.stop();
    azureBlobStorageContainer.close();
  }

  @Test
  void testSpillBlobWithExceedingSize() throws Exception {
    // when
    String content = Files.readString(Paths.get("src/test-integration/resources/test_data"));

    azureBlobStorageConsumer.startTracked();

    Function<String, JsonNode> function =
        data -> Jsons.jsonNode(ImmutableMap.builder().put("property", data).build());

    // create blob exceeding 1mb in size
    for (int i = 1; i <= 512; i++) {
      azureBlobStorageConsumer.acceptTracked(
          createAirbyteMessage(function.apply(content)));
    }

    azureBlobStorageConsumer.close(false);

    // then
    assertThat(blobContainerClient.listBlobs())
        .hasSize(2)
        .anyMatch(blobItem -> blobItem.getName().endsWith("_0"))
        .anyMatch(blobItem -> blobItem.getName().endsWith("_1"));

  }

  private static AzureBlobStorageDestinationConfig createConfig(String host, Integer mappedPort) {
    final ObjectNode stubFormatConfig = mapper.createObjectNode();
    stubFormatConfig.put("file_extension", Boolean.TRUE);
    final ObjectNode stubConfig = mapper.createObjectNode();
    stubConfig.set("format", stubFormatConfig);

    return new AzureBlobStorageDestinationConfig(
        "http://" + host + ":" + mappedPort + "/devstoreaccount1",
        "devstoreaccount1",
        "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==",
        "container-name",
        1,
        1,
        new AzureBlobStorageJsonlFormatConfig(stubConfig));
  }

  private static AirbyteMessage createAirbyteMessage(JsonNode data) {
    return new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(AIRBYTE_STREAM)
            .withNamespace(AIRBYTE_NAMESPACE)
            .withData(data)
            .withEmittedAt(Instant.now().toEpochMilli()));
  }

  private static AirbyteStream createAirbyteStream() {
    return new AirbyteStream()
        .withName(AIRBYTE_STREAM)
        .withNamespace(AIRBYTE_NAMESPACE)
        .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH));
  }

  private static ConfiguredAirbyteStream createConfiguredAirbyteStream() {
    return new ConfiguredAirbyteStream()
        .withDestinationSyncMode(DestinationSyncMode.APPEND)
        .withStream(createAirbyteStream());
  }

  private static ConfiguredAirbyteCatalog createConfiguredAirbyteCatalog() {
    return new ConfiguredAirbyteCatalog().withStreams(List.of(createConfiguredAirbyteStream()));
  }

}
