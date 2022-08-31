/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.BooleanNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpTimeoutException;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This config persistence pulls the definition configurations from a remotely hosted catalog. It is
 * read-only.
 */
final public class RemoteDefinitionsProvider implements DefinitionsProvider {

  private Map<UUID, StandardSourceDefinition> sourceDefinitions;
  private Map<UUID, StandardDestinationDefinition> destinationDefinitions;

  private static final Logger LOGGER = LoggerFactory.getLogger(RemoteDefinitionsProvider.class);
  private static final HttpClient httpClient = HttpClient.newHttpClient();
  private final URI remoteDefinitionCatalogUrl;
  private static final Duration DEFAULT_TIMEOUT = Duration.ofSeconds(30);
  private final Duration timeout;

  public RemoteDefinitionsProvider(final String remoteDefinitionCatalogUrl) throws InterruptedException, IOException {
    this.remoteDefinitionCatalogUrl = URI.create(remoteDefinitionCatalogUrl);
    this.timeout = DEFAULT_TIMEOUT;
    // TODO remove this call once dependency injection framework manages object creation
    initialize();
  }

  public RemoteDefinitionsProvider(final String remoteDefinitionCatalogUrl, final Duration timeout) throws InterruptedException, IOException {
    this.remoteDefinitionCatalogUrl = URI.create(remoteDefinitionCatalogUrl);
    this.timeout = timeout;
    // TODO remove this call once dependency injection framework manages object creation
    initialize();
  }

  // TODO will be called automatically by the dependency injection framework on object creation
  public void initialize() throws InterruptedException, IOException {
    try {
      final JsonNode catalog = getRemoteDefinitionCatalog(this.remoteDefinitionCatalogUrl, this.timeout);
      this.sourceDefinitions =
          parseCatalogElement(catalog, "sources", StandardSourceDefinition.class, SeedType.STANDARD_SOURCE_DEFINITION.getIdName());
      this.destinationDefinitions =
          parseCatalogElement(catalog, "destinations", StandardDestinationDefinition.class, SeedType.STANDARD_DESTINATION_DEFINITION.getIdName());
    } catch (final HttpTimeoutException e) {
      LOGGER.warn(
          "Unable to retrieve the remote definition catalog. Using the catalog bundled with Airbyte. This warning is expected if this Airbyte cluster does not have internet access.",
          e);
      this.sourceDefinitions = Collections.emptyMap();
      this.destinationDefinitions = Collections.emptyMap();
    }

  }

  private static JsonNode getRemoteDefinitionCatalog(URI catalogUrl, Duration timeout) throws IOException, InterruptedException {
    final HttpRequest request = HttpRequest.newBuilder(catalogUrl).timeout(timeout).header("accept", "application/json").build();

    final HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
    if (response.statusCode() >= 400) {
      throw new IOException(
          "getRemoteDefinitionCatalog request ran into status code error: " + response.statusCode() + " with message: " + response.getClass());
    }
    try {
      return Jsons.deserialize(response.body());
    } catch (final RuntimeException e) {
      throw new IOException("Could not deserialize JSON response: ", e);
    }

  }

  private static <T> Map<UUID, T> parseCatalogElement(final JsonNode catalog,
                                                      final String catalogKey,
                                                      final Class<T> outputModel,
                                                      final String definitionIdField)
      throws IOException {
    final JsonNode catalogElementNode = catalog.get(catalogKey);
    if (catalogElementNode == null) {
      throw new IOException("The catalog schema is invalid: Missing \"" + catalogKey + "\" key");
    }
    final List<JsonNode> catalogElements = MoreIterators.toList(catalogElementNode.elements());
    return catalogElements.stream().collect(Collectors.toMap(
        json -> UUID.fromString(json.get(definitionIdField).asText()),
        json -> Jsons.object(patchElement(json), outputModel)));
  }

  private static JsonNode patchElement(JsonNode element) {
    return addMissingTombstoneField(element);
  }

  private static JsonNode addMissingTombstoneField(final JsonNode definition) {
    final JsonNode currTombstone = definition.get("tombstone");
    if (currTombstone == null || currTombstone.isNull()) {
      ((ObjectNode) definition).set("tombstone", BooleanNode.FALSE);
    }
    return definition;
  }

  @Override
  public StandardSourceDefinition getSourceDefinition(final UUID definitionId) throws ConfigNotFoundException {
    StandardSourceDefinition definition = this.sourceDefinitions.get(definitionId);
    if (definition == null) {
      throw new ConfigNotFoundException(SeedType.STANDARD_SOURCE_DEFINITION.name(), definitionId.toString());
    }
    return definition;
  }

  @Override
  public List<StandardSourceDefinition> getSourceDefinitions() {
    return new ArrayList<>(this.sourceDefinitions.values());
  }

  @Override
  public StandardDestinationDefinition getDestinationDefinition(final UUID definitionId) throws ConfigNotFoundException {
    StandardDestinationDefinition definition = this.destinationDefinitions.get(definitionId);
    if (definition == null) {
      throw new ConfigNotFoundException(SeedType.STANDARD_DESTINATION_DEFINITION.name(), definitionId.toString());
    }
    return definition;
  }

  @Override
  public List<StandardDestinationDefinition> getDestinationDefinitions() {
    return new ArrayList<>(this.destinationDefinitions.values());
  }

}
