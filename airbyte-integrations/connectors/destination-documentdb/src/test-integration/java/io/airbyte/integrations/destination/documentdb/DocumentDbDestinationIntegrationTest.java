/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.documentdb;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.client.MongoClients;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.mongodb.MongodbNameTransformer;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.wait.strategy.Wait;
import org.testcontainers.utility.DockerImageName;

class DocumentDbDestinationIntegrationTest {

  private static final String IMAGE = "ghcr.io/documentdb/documentdb/documentdb-local:latest";

  @Test
  void checksAndWritesToDocumentDb() throws Exception {
    try (GenericContainer<?> container = documentDbContainer()) {
      container.start();
      final JsonNode config = config(container);
      final DocumentDbDestination destination = new DocumentDbDestination();
      assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, destination.check(config).getStatus());

      final var stream = new AirbyteStream().withName("products").withJsonSchema(Jsons.jsonNode(Map.of("type", "object")));
      final var catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(new ConfiguredAirbyteStream()
          .withStream(stream)
          .withSyncMode(SyncMode.FULL_REFRESH)
          .withDestinationSyncMode(DestinationSyncMode.APPEND)));
      final var consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);
      consumer.start();
      consumer.accept(new AirbyteMessage().withType(AirbyteMessage.Type.RECORD).withRecord(new AirbyteRecordMessage()
          .withStream("products")
          .withEmittedAt(System.currentTimeMillis())
          .withData(Jsons.jsonNode(Map.of("name", "keyboard", "quantity", 2)))));
      consumer.accept(new AirbyteMessage().withType(AirbyteMessage.Type.STATE)
          .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(Map.of("checkpoint", 1)))));
      consumer.close();

      try (var client = MongoClients.create(DocumentDbDestination.buildConnectionString(config))) {
        final String collectionName = new MongodbNameTransformer().getRawTableName("products");
        final var record = client.getDatabase("airbyte").getCollection(collectionName).find().first();
        assertEquals("keyboard", record.get("_airbyte_data", org.bson.Document.class).getString("name"));
      }
    }
  }

  private static GenericContainer<?> documentDbContainer() {
    return new GenericContainer<>(DockerImageName.parse(IMAGE))
        .withEnv("ALLOW_EXTERNAL_CONNECTIONS", "true")
        .withEnv("USERNAME", "airbyte")
        .withEnv("PASSWORD", "password")
        .withExposedPorts(10260)
        .waitingFor(Wait.forListeningPort())
        .withStartupTimeout(Duration.ofMinutes(3));
  }

  private static JsonNode config(final GenericContainer<?> container) {
    return Jsons.jsonNode(Map.of(
        "host", container.getHost(),
        "port", container.getMappedPort(10260),
        "database", "airbyte",
        "username", "airbyte",
        "password", "password",
        "tls", false,
        "direct_connection", true));
  }
}