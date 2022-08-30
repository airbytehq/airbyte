/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.config.AirbyteConfigValidator;
import io.airbyte.config.ConfigSchema;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This config persistence pulls the connector configurations from a remotely hosted catalog. It is
 * read-only.
 */
final public class RemoteResource extends ConnectorDefinitionsProvider {

  private static final Logger LOGGER = LoggerFactory.getLogger(RemoteResource.class);
  private static final HttpClient httpClient = HttpClient.newHttpClient();

  private static final Map<ConfigSchema, String> CONFIG_TYPE_CONNECTOR_CATALOG_MAP = Map.of(
      ConfigSchema.STANDARD_SOURCE_DEFINITION, "sources",
      ConfigSchema.STANDARD_DESTINATION_DEFINITION, "destinations");

  private final URI remoteConnectorCatalogUrl;
  private static final Duration DEFAULT_TIMEOUT = Duration.ofSeconds(30);
  private final Duration timeout;

  public RemoteResource(final String remoteConnectorCatalogUrl) throws InterruptedException {
    this.remoteConnectorCatalogUrl = URI.create(remoteConnectorCatalogUrl);
    this.timeout = DEFAULT_TIMEOUT;
    // TODO remove this call once dependency injection framework manages object creation
    initialize();
  }

  public RemoteResource(final String remoteConnectorCatalogUrl, final Duration timeout) throws InterruptedException {
    this.remoteConnectorCatalogUrl = URI.create(remoteConnectorCatalogUrl);
    this.timeout = timeout;
    // TODO remove this call once dependency injection framework manages object creation
    initialize();
  }

  // TODO will be called automatically by the dependency injection framework on object creation
  @Override
  public void initialize() throws InterruptedException {
    try {
      final JsonNode rawConnectorCatalog = getRemoteConnectorCatalog(this.remoteConnectorCatalogUrl, this.timeout);
      setAllDefinitions(parseConnectorCatalog(rawConnectorCatalog));
    } catch (final IOException e) {
      LOGGER.warn(
          "Unable to retrieve the remote connector catalog. Using the catalog bundled with Airbyte. This warning is expected if this Airbyte cluster does not have internet access.",
          e);
      setAllDefinitions(emptyDefinitions);
    }
  }

  private static JsonNode getRemoteConnectorCatalog(URI catalogUrl, Duration timeout) throws IOException, InterruptedException {
    final HttpRequest request = HttpRequest.newBuilder(catalogUrl).timeout(timeout).header("accept", "application/json").build();
    final HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
    if (response.statusCode() >= 400) {
      throw new IOException(
          "getRemoteConnectorCatalog request ran into status code error: " + response.statusCode() + "with message: " + response.getClass());
    }
    try {
      return Jsons.deserialize(response.body());
    } catch (final RuntimeException e) {
      throw new IOException("Could not deserialize JSON response: ", e);
    }

  }

  private ImmutableMap<ConfigSchema, Map<String, JsonNode>> parseConnectorCatalog(JsonNode catalog) {
    return ImmutableMap.<ConfigSchema, Map<String, JsonNode>>builder()
        .put(ConfigSchema.STANDARD_SOURCE_DEFINITION, parseRemoteConfigs(catalog, ConfigSchema.STANDARD_SOURCE_DEFINITION))
        .put(ConfigSchema.STANDARD_DESTINATION_DEFINITION, parseRemoteConfigs(catalog, ConfigSchema.STANDARD_DESTINATION_DEFINITION))
        .build();

  }

  private static Map<String, JsonNode> parseRemoteConfigs(final JsonNode rawConnectorCatalog, final ConfigSchema configType) {
    final String definitionKey = CONFIG_TYPE_CONNECTOR_CATALOG_MAP.get(configType);
    final JsonNode rawDefinitions = rawConnectorCatalog.get(definitionKey);
    if (rawDefinitions == null) {
      return Collections.emptyMap();
    }

    final List<JsonNode> configKeyElements = MoreIterators.toList(rawDefinitions.elements());

    final Map<String, JsonNode> configs = configKeyElements.stream().collect(Collectors.toMap(
        json -> json.get(configType.getIdFieldName()).asText(),
        json -> json));
    return configs.entrySet().stream()
        .collect(Collectors.toMap(Entry::getKey, e -> {
          final JsonNode output = addMissingTombstoneField(e.getValue());
          AirbyteConfigValidator.AIRBYTE_CONFIG_VALIDATOR.ensureAsRuntime(configType, output);
          return output;
        }));
  }

}
