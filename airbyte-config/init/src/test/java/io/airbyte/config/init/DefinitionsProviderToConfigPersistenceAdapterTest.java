/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.io.Resources;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import java.io.IOException;
import java.net.URI;
import java.net.URL;
import java.nio.charset.Charset;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DefinitionsProviderToConfigPersistenceAdapterTest {

  private MockWebServer webServer;
  private static MockResponse validCatalogResponse;
  private static URI catalogUrl;
  private static JsonNode jsonCatalog;

  @BeforeEach
  void setup() throws IOException {
    webServer = new MockWebServer();
    catalogUrl = URI.create(webServer.url("/connector_catalog.json").toString());

    final URL testCatalog = Resources.getResource("connector_catalog.json");
    final String jsonBody = Resources.toString(testCatalog, Charset.defaultCharset());
    jsonCatalog = Jsons.deserialize(jsonBody);
    validCatalogResponse = new MockResponse().setResponseCode(200)
        .addHeader("Content-Type", "application/json; charset=utf-8")
        .addHeader("Cache-Control", "no-cache")
        .setBody(jsonBody);
  }

  @Test
  void testGetConfig() throws Exception {
    webServer.enqueue(validCatalogResponse);
    final RemoteDefinitionsProvider remoteDefinitionsProvider = new RemoteDefinitionsProvider(catalogUrl);
    final DefinitionProviderToConfigPersistenceAdapter adapter = new DefinitionProviderToConfigPersistenceAdapter(remoteDefinitionsProvider);
    // source
    final String stripeSourceId = "e094cb9a-26de-4645-8761-65c0c425d1de";
    final StandardSourceDefinition stripeSource = adapter
        .getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, stripeSourceId, StandardSourceDefinition.class);
    assertEquals(stripeSourceId, stripeSource.getSourceDefinitionId().toString());
    assertEquals("Stripe", stripeSource.getName());
    assertEquals("airbyte/source-stripe", stripeSource.getDockerRepository());
    assertEquals("https://docs.airbyte.io/integrations/sources/stripe", stripeSource.getDocumentationUrl());
    assertEquals("stripe.svg", stripeSource.getIcon());
    assertEquals(URI.create("https://docs.airbyte.io/integrations/sources/stripe"), stripeSource.getSpec().getDocumentationUrl());

    // destination
    final String s3DestinationId = "4816b78f-1489-44c1-9060-4b19d5fa9362";
    final StandardDestinationDefinition s3Destination = adapter
        .getConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, s3DestinationId, StandardDestinationDefinition.class);
    assertEquals(s3DestinationId, s3Destination.getDestinationDefinitionId().toString());
    assertEquals("S3", s3Destination.getName());
    assertEquals("airbyte/destination-s3", s3Destination.getDockerRepository());
    assertEquals("https://docs.airbyte.io/integrations/destinations/s3", s3Destination.getDocumentationUrl());
    assertEquals(URI.create("https://docs.airbyte.io/integrations/destinations/s3"), s3Destination.getSpec().getDocumentationUrl());
    assertThrows(UnsupportedOperationException.class, () -> {
      adapter.getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, s3DestinationId, StandardDestinationDefinition.class);
    });
  }

  // TODO This test can be removed once ConfigRepository gets refactored to use DefinitionsProvider
  // interface
  @Test
  void testListConfig() throws Exception {
    webServer.enqueue(validCatalogResponse);
    final RemoteDefinitionsProvider remoteDefinitionsProvider = new RemoteDefinitionsProvider(catalogUrl);
    final DefinitionProviderToConfigPersistenceAdapter adapter = new DefinitionProviderToConfigPersistenceAdapter(remoteDefinitionsProvider);

    final List<StandardSourceDefinition> sourceDefinitions =
        adapter.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class);
    final int expectedNumberOfSources = MoreIterators.toList(jsonCatalog.get("sources").elements()).size();
    assertEquals(expectedNumberOfSources, sourceDefinitions.size());

    final List<StandardDestinationDefinition> destinationDefinitions =
        adapter.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class);
    final int expectedNumberOfDestinations = MoreIterators.toList(jsonCatalog.get("destinations").elements()).size();
    assertEquals(expectedNumberOfDestinations, destinationDefinitions.size());

    assertThrows(UnsupportedOperationException.class, () -> {
      adapter.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardDestinationDefinition.class);
    });
  }

  // TODO This test can be removed once ConfigRepository gets refactored to use DefinitionsProvider
  // interface
  @Test
  void testDumpConfigs() throws Exception {
    webServer.enqueue(validCatalogResponse);
    final RemoteDefinitionsProvider remoteDefinitionsProvider = new RemoteDefinitionsProvider(catalogUrl, Duration.ofSeconds(1));
    final DefinitionProviderToConfigPersistenceAdapter adapter = new DefinitionProviderToConfigPersistenceAdapter(remoteDefinitionsProvider);

    final Map<String, Stream<JsonNode>> allRemoteConfigs = adapter.dumpConfigs();
    assertEquals(2, allRemoteConfigs.size());
    List<JsonNode> sourceDefinitions = allRemoteConfigs.get(ConfigSchema.STANDARD_SOURCE_DEFINITION.name()).collect(Collectors.toList());
    final int expectedNumberOfSources = MoreIterators.toList(jsonCatalog.get("sources").elements()).size();
    assertEquals(expectedNumberOfSources, sourceDefinitions.size());
    assertEquals(Jsons.object(sourceDefinitions.get(0), StandardSourceDefinition.class), remoteDefinitionsProvider.getSourceDefinitions().get(0));
    List<JsonNode> destinationDefinitions = allRemoteConfigs.get(ConfigSchema.STANDARD_DESTINATION_DEFINITION.name()).collect(Collectors.toList());
    final int expectedNumberOfDestinations = MoreIterators.toList(jsonCatalog.get("destinations").elements()).size();
    assertEquals(expectedNumberOfDestinations, destinationDefinitions.size());
    assertEquals(Jsons.object(destinationDefinitions.get(0), StandardDestinationDefinition.class),
        remoteDefinitionsProvider.getDestinationDefinitions().get(0));
  }

}
