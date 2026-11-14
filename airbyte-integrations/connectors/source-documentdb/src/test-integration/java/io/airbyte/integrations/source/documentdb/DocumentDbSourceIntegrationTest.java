/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.documentdb;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.client.MongoClients;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import org.bson.Document;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.wait.strategy.Wait;
import org.testcontainers.utility.DockerImageName;

class DocumentDbSourceIntegrationTest {

  private static final String IMAGE = "ghcr.io/documentdb/documentdb/documentdb-local:latest";

  @Test
  void checksDiscoversAndReadsDocumentDb() throws Exception {
    try (GenericContainer<?> container = documentDbContainer()) {
      container.start();
      final JsonNode config = config(container);
      try (var client = MongoClients.create(DocumentDbSource.buildConnectionString(config))) {
        client.getDatabase("inventory").getCollection("products").insertOne(new Document("name", "keyboard").append("quantity", 2));
      }

      final DocumentDbSource source = new DocumentDbSource();
      assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, source.check(config).getStatus());
      final var catalog = source.discover(config);
      final var products = catalog.getStreams().stream().filter(stream -> stream.getName().equals("products")).findFirst().orElseThrow();
      assertEquals(List.of(SyncMode.FULL_REFRESH), products.getSupportedSyncModes());
      assertTrue(products.getJsonSchema().get("properties").has("name"));

      final var configuredCatalog = new ConfiguredAirbyteCatalog().withStreams(List.of(new ConfiguredAirbyteStream()
          .withStream(products)
          .withSyncMode(SyncMode.FULL_REFRESH)));
      try (var messages = source.read(config, configuredCatalog, Jsons.jsonNode(Map.of()))) {
        boolean foundRecord = false;
        while (messages.hasNext()) {
          final var message = messages.next();
          if (message.getRecord() != null) {
            assertEquals("keyboard", message.getRecord().getData().get("name").asText());
            foundRecord = true;
            break;
          }
        }
        assertTrue(foundRecord);
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
        "databases", List.of("inventory"),
        "username", "airbyte",
        "password", "password",
        "tls", false,
        "direct_connection", true));
  }

}
