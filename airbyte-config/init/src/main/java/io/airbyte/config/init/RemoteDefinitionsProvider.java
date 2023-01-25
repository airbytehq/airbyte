/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.AirbyteProtocolVersion;
import io.airbyte.config.CombinedConnectorCatalog;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.micronaut.cache.annotation.CacheConfig;
import io.micronaut.cache.annotation.Cacheable;
import io.micronaut.context.annotation.Primary;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.annotation.Value;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;

/**
 * This provider pulls the definitions from a remotely hosted catalog.
 */
@Singleton
@Primary
@Requires(property = "airbyte.platform.remote-connector-catalog.url",
          notEquals = "")
@CacheConfig("remote-definitions-provider")
@Slf4j
public class RemoteDefinitionsProvider implements DefinitionsProvider {

  private static final HttpClient httpClient = HttpClient.newHttpClient();
  private final URI remoteDefinitionCatalogUrl;
  private final Duration timeout;

  public RemoteDefinitionsProvider(@Value("${airbyte.platform.remote-connector-catalog.url}") final String remoteCatalogUrl,
                                   @Value("${airbyte.platform.remote-connector-catalog.timeout-ms}") final long remoteCatalogTimeoutMs)
      throws URISyntaxException {
    log.info("Creating remote definitions provider for URL '{}'...", remoteCatalogUrl);
    this.remoteDefinitionCatalogUrl = new URI(remoteCatalogUrl);
    this.timeout = Duration.ofMillis(remoteCatalogTimeoutMs);
  }

  private Map<UUID, StandardSourceDefinition> getSourceDefinitionsMap() {
    final CombinedConnectorCatalog catalog = getRemoteDefinitionCatalog();
    return catalog.getSources().stream().collect(Collectors.toMap(
        StandardSourceDefinition::getSourceDefinitionId,
        source -> source.withProtocolVersion(
            AirbyteProtocolVersion.getWithDefault(source.getSpec() != null ? source.getSpec().getProtocolVersion() : null).serialize())));
  }

  private Map<UUID, StandardDestinationDefinition> getDestinationDefinitionsMap() {
    final CombinedConnectorCatalog catalog = getRemoteDefinitionCatalog();
    return catalog.getDestinations().stream().collect(Collectors.toMap(
        StandardDestinationDefinition::getDestinationDefinitionId,
        destination -> destination.withProtocolVersion(
            AirbyteProtocolVersion.getWithDefault(destination.getSpec() != null ? destination.getSpec().getProtocolVersion() : null).serialize())));
  }

  @Override
  public StandardSourceDefinition getSourceDefinition(final UUID definitionId) throws ConfigNotFoundException {
    final StandardSourceDefinition definition = getSourceDefinitionsMap().get(definitionId);
    if (definition == null) {
      throw new ConfigNotFoundException(SeedType.STANDARD_SOURCE_DEFINITION.name(), definitionId.toString());
    }
    return definition;
  }

  @Override
  public List<StandardSourceDefinition> getSourceDefinitions() {
    return new ArrayList<>(getSourceDefinitionsMap().values());
  }

  @Override
  public StandardDestinationDefinition getDestinationDefinition(final UUID definitionId) throws ConfigNotFoundException {
    final StandardDestinationDefinition definition = getDestinationDefinitionsMap().get(definitionId);
    if (definition == null) {
      throw new ConfigNotFoundException(SeedType.STANDARD_DESTINATION_DEFINITION.name(), definitionId.toString());
    }
    return definition;
  }

  @Override
  public List<StandardDestinationDefinition> getDestinationDefinitions() {
    return new ArrayList<>(getDestinationDefinitionsMap().values());
  }

  @Cacheable
  public CombinedConnectorCatalog getRemoteDefinitionCatalog() {
    try {
      final HttpRequest request = HttpRequest.newBuilder(remoteDefinitionCatalogUrl).timeout(timeout).header("accept", "application/json").build();

      final HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
      if (errorStatusCode(response)) {
        throw new IOException(
            "getRemoteDefinitionCatalog request ran into status code error: " + response.statusCode() + " with message: " + response.getClass());
      }

      log.info("Fetched latest remote definitions ({})", response.body().hashCode());
      return Jsons.deserialize(response.body(), CombinedConnectorCatalog.class);
    } catch (final Exception e) {
      throw new RuntimeException("Failed to fetch remote definitions", e);
    }
  }

  private static Boolean errorStatusCode(final HttpResponse<String> response) {
    return response.statusCode() >= 400;
  }

}
