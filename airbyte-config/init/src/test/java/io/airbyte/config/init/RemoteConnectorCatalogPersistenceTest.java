/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.io.Resources;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import java.io.IOException;
import java.net.URI;
import java.net.URL;
import java.nio.charset.Charset;
import java.time.Duration;
import java.util.Collections;
import java.util.Map;
import java.util.stream.Stream;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class RemoteConnectorCatalogPersistenceTest {

  private static RemoteConnectorCatalogPersistence persistence;
  private static MockWebServer webServer;
  private static MockResponse validCatalogResponse;

  @BeforeEach
  void setup() throws IOException {
    webServer = new MockWebServer();
    final URL testCatalog = Resources.getResource("connector_catalog.json");
    final String jsonBody = Resources.toString(testCatalog, Charset.defaultCharset());
    validCatalogResponse = new MockResponse().setResponseCode(200)
        .addHeader("Content-Type", "application/json; charset=utf-8")
        .addHeader("Cache-Control", "no-cache")
        .setBody(jsonBody);
  }

  @Test
  void testGetConfig() throws Exception {
    webServer.enqueue(validCatalogResponse);
    persistence = new RemoteConnectorCatalogPersistence(webServer.url("/connector_catalog.json").toString());
    // source
    final String stripeSourceId = "e094cb9a-26de-4645-8761-65c0c425d1de";
    final StandardSourceDefinition stripeSource = persistence
        .getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, stripeSourceId, StandardSourceDefinition.class);
    assertEquals(stripeSourceId, stripeSource.getSourceDefinitionId().toString());
    assertEquals("Stripe", stripeSource.getName());
    assertEquals("airbyte/source-stripe", stripeSource.getDockerRepository());
    assertEquals("https://docs.airbyte.io/integrations/sources/stripe", stripeSource.getDocumentationUrl());
    assertEquals("stripe.svg", stripeSource.getIcon());
    assertEquals(URI.create("https://docs.airbyte.io/integrations/sources/stripe"), stripeSource.getSpec().getDocumentationUrl());


    // destination
    final String s3DestinationId = "4816b78f-1489-44c1-9060-4b19d5fa9362";
    final StandardDestinationDefinition s3Destination = persistence
        .getConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, s3DestinationId, StandardDestinationDefinition.class);
    assertEquals(s3DestinationId, s3Destination.getDestinationDefinitionId().toString());
    assertEquals("S3", s3Destination.getName());
    assertEquals("airbyte/destination-s3", s3Destination.getDockerRepository());
    assertEquals("https://docs.airbyte.io/integrations/destinations/s3", s3Destination.getDocumentationUrl());
    assertEquals(URI.create("https://docs.airbyte.io/integrations/destinations/s3"), s3Destination.getSpec().getDocumentationUrl());
  }

  @Test
  void testGetInvalidConfig() throws Exception {
    webServer.enqueue(validCatalogResponse);
    persistence = new RemoteConnectorCatalogPersistence(webServer.url("/connector_catalog.json").toString(), Duration.ofSeconds(1));

    assertThrows(
        UnsupportedOperationException.class,
        () -> persistence.getConfig(ConfigSchema.STANDARD_SYNC, "invalid_id", StandardSync.class));
    assertThrows(
        ConfigNotFoundException.class,
        () -> persistence.getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, "invalid_id", StandardWorkspace.class));
  }

  @Test
  void testDumpConfigs() throws Exception {
    webServer.enqueue(validCatalogResponse);
    persistence = new RemoteConnectorCatalogPersistence(webServer.url("/connector_catalog.json").toString(), Duration.ofSeconds(1));

    final Map<String, Stream<JsonNode>> allRemoteConfigs = persistence.dumpConfigs();
    assertEquals(2, allRemoteConfigs.size());
    assertTrue(allRemoteConfigs.get(ConfigSchema.STANDARD_SOURCE_DEFINITION.name()).findAny().isPresent());
    assertTrue(allRemoteConfigs.get(ConfigSchema.STANDARD_DESTINATION_DEFINITION.name()).findAny().isPresent());
  }

  @Test
  void testWriteMethods() throws Exception {
    webServer.enqueue(validCatalogResponse);
    persistence = new RemoteConnectorCatalogPersistence(webServer.url("/connector_catalog.json").toString(), Duration.ofSeconds(1));

    assertThrows(UnsupportedOperationException.class, () -> persistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, "id", new Object()));
    assertThrows(UnsupportedOperationException.class, () -> persistence.replaceAllConfigs(Collections.emptyMap(), false));
  }

  @Test
  void testBadResponseStatus() throws Exception {
    webServer.enqueue(new MockResponse().setResponseCode(404));
    persistence = new RemoteConnectorCatalogPersistence(webServer.url("/connector_catalog.json").toString(), Duration.ofSeconds(1));
    final Map<String, Stream<JsonNode>> allRemoteConfigs = persistence.dumpConfigs();
    assertFalse(allRemoteConfigs.get(ConfigSchema.STANDARD_SOURCE_DEFINITION.name()).findAny().isPresent());
    assertFalse(allRemoteConfigs.get(ConfigSchema.STANDARD_DESTINATION_DEFINITION.name()).findAny().isPresent());
  }

  @Test
  void testNonJson() throws Exception {
    final MockResponse notJson = new MockResponse().setResponseCode(200)
        .addHeader("Content-Type", "application/json; charset=utf-8")
        .addHeader("Cache-Control", "no-cache")
        .setBody("not json");
    webServer.enqueue(notJson);
    persistence = new RemoteConnectorCatalogPersistence(webServer.url("/connector_catalog.json").toString(), Duration.ofSeconds(1));
    final Map<String, Stream<JsonNode>> allRemoteConfigs = persistence.dumpConfigs();
    assertFalse(allRemoteConfigs.get(ConfigSchema.STANDARD_SOURCE_DEFINITION.name()).findAny().isPresent());
    assertFalse(allRemoteConfigs.get(ConfigSchema.STANDARD_DESTINATION_DEFINITION.name()).findAny().isPresent());
  }

  @Test
  void testInvalidCatalogSchema() throws Exception {
    final MockResponse invalidSchema = new MockResponse().setResponseCode(200)
        .addHeader("Content-Type", "application/json; charset=utf-8")
        .addHeader("Cache-Control", "no-cache")
        .setBody("{\"foo\":\"bar\"}");
    webServer.enqueue(invalidSchema);
    persistence = new RemoteConnectorCatalogPersistence(webServer.url("/connector_catalog.json").toString(), Duration.ofSeconds(1));
    final Map<String, Stream<JsonNode>> allRemoteConfigs = persistence.dumpConfigs();
    assertFalse(allRemoteConfigs.get(ConfigSchema.STANDARD_SOURCE_DEFINITION.name()).findAny().isPresent());
    assertFalse(allRemoteConfigs.get(ConfigSchema.STANDARD_DESTINATION_DEFINITION.name()).findAny().isPresent());
  }

  @Test
  void testTimeOut() throws Exception {
    // No request enqueued -> Timeout
    persistence = new RemoteConnectorCatalogPersistence(webServer.url("/connector_catalog.json").toString(), Duration.ofSeconds(1));
    final Map<String, Stream<JsonNode>> allRemoteConfigs = persistence.dumpConfigs();
    assertFalse(allRemoteConfigs.get(ConfigSchema.STANDARD_SOURCE_DEFINITION.name()).findAny().isPresent());
    assertFalse(allRemoteConfigs.get(ConfigSchema.STANDARD_DESTINATION_DEFINITION.name()).findAny().isPresent());
  }

}
