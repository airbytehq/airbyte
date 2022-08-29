/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.BooleanNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.AirbyteConfigValidator;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.ConfigWithMetadata;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.validation.json.JsonValidationException;
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
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This config persistence pulls the connector configurations from a remotely hosted catalog. It is
 * read-only.
 */
final public class RemoteConnectorCatalogPersistence implements ConfigPersistence {

  private static final Logger LOGGER = LoggerFactory.getLogger(RemoteConnectorCatalogPersistence.class);
  private static final String PERSISTENCE_READ_ONLY_ERROR_MSG = "The connector catalog is read only.";
  private static final HttpClient httpClient = HttpClient.newHttpClient();

  private static final Map<AirbyteConfig, String> CONFIG_SCHEMA_CONNECTOR_CATALOG_MAP = Map.of(
      ConfigSchema.STANDARD_SOURCE_DEFINITION, "sources",
      ConfigSchema.STANDARD_DESTINATION_DEFINITION, "destinations");

  private final URI remoteConnectorCatalogUrl;
  private static final Duration DEFAULT_TIMEOUT = Duration.ofSeconds(30);
  private final Duration timeout;
  // A mapping from config type to config UUID to config.
  private ImmutableMap<AirbyteConfig, Map<String, JsonNode>> connectorCatalog;

  public RemoteConnectorCatalogPersistence(final String remoteConnectorCatalogUrl) throws InterruptedException {
    this.remoteConnectorCatalogUrl = URI.create(remoteConnectorCatalogUrl);
    this.timeout = DEFAULT_TIMEOUT;
    // TODO remove this call once dependency injection framework manages object creation
    initialize();
  }

  public RemoteConnectorCatalogPersistence(final String remoteConnectorCatalogUrl, final Duration timeout) throws InterruptedException {
    this.remoteConnectorCatalogUrl = URI.create(remoteConnectorCatalogUrl);
    this.timeout = timeout;
    // TODO remove this call once dependency injection framework manages object creation
    initialize();
  }

  // TODO will be called automatically by the dependency injection framework on object creation
  public void initialize() throws InterruptedException {
    try {
      final JsonNode rawConnectorCatalog = getRemoteConnectorCatalog(this.remoteConnectorCatalogUrl, this.timeout);
      this.connectorCatalog = parseConnectorCatalog(rawConnectorCatalog);
    } catch (final IOException e) {
      LOGGER.warn(
          "Unable to retrieve the remote connector catalog. Using the catalog bundled with Airbyte. This warning is expected if this Airbyte cluster does not have internet access.",
          e);
      this.connectorCatalog = ImmutableMap.<AirbyteConfig, Map<String, JsonNode>>builder()
          .put(ConfigSchema.STANDARD_SOURCE_DEFINITION, Collections.emptyMap())
          .put(ConfigSchema.STANDARD_DESTINATION_DEFINITION, Collections.emptyMap())
          .build();
    }
  }

  private static JsonNode getRemoteConnectorCatalog(URI catalogUrl, Duration timeout) throws IOException, InterruptedException {
    final HttpRequest request = HttpRequest.newBuilder(catalogUrl).timeout(timeout).header("accept", "application/json").build();
    final HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
    if (response.statusCode() >= 400) {
      throw new IOException("getRemoteConnectorCatalog request ran into status code error: " + response.statusCode() + "with message: " + response.getClass());
    }
    try {
      return Jsons.deserialize(response.body());
    } catch (final RuntimeException e) {
      throw new IOException("Could not deserialize JSON response: ", e);
    }

  }

  private ImmutableMap<AirbyteConfig, Map<String, JsonNode>> parseConnectorCatalog(JsonNode catalog) {
    return ImmutableMap.<AirbyteConfig, Map<String, JsonNode>>builder()
        .put(ConfigSchema.STANDARD_SOURCE_DEFINITION, parseRemoteConfigs(catalog, ConfigSchema.STANDARD_SOURCE_DEFINITION))
        .put(ConfigSchema.STANDARD_DESTINATION_DEFINITION, parseRemoteConfigs(catalog, ConfigSchema.STANDARD_DESTINATION_DEFINITION))
        .build();

  }

  private static Map<String, JsonNode> parseRemoteConfigs(final JsonNode rawConnectorCatalog, final ConfigSchema configType) {
    final String configKey = CONFIG_SCHEMA_CONNECTOR_CATALOG_MAP.get(configType);
    final JsonNode rawConfigs = rawConnectorCatalog.get(configKey);
    if (rawConfigs == null) {
      return Collections.emptyMap();
    }

    final List<JsonNode> configKeyElements = MoreIterators.toList(rawConfigs.elements());

    final Map<String, JsonNode> configs = configKeyElements.stream().collect(Collectors.toMap(
        json -> json.get(configType.getIdFieldName()).asText(),
        json -> json));
    final Map<String, JsonNode> configsWithMissingField = configs.entrySet().stream()
        .collect(Collectors.toMap(Entry::getKey, e -> {
          final JsonNode output =
              addMissingCustomField(
                  addMissingPublicField(
                      addMissingTombstoneField(e.getValue())));
          AirbyteConfigValidator.AIRBYTE_CONFIG_VALIDATOR.ensureAsRuntime(configType, output);
          return output;
        }));
    return configsWithMissingField;
  }

  private static JsonNode addMissingTombstoneField(final JsonNode definitionJson) {
    final JsonNode currTombstone = definitionJson.get("tombstone");
    if (currTombstone == null || currTombstone.isNull()) {
      ((ObjectNode) definitionJson).set("tombstone", BooleanNode.FALSE);
    }
    return definitionJson;
  }

  private static JsonNode addMissingPublicField(final JsonNode definitionJson) {
    final JsonNode currPublic = definitionJson.get("public");
    if (currPublic == null || currPublic.isNull()) {
      // definitions loaded from the cloud connector catalog are by definition public
      ((ObjectNode) definitionJson).set("public", BooleanNode.TRUE);
    }
    return definitionJson;
  }

  private static JsonNode addMissingCustomField(final JsonNode definitionJson) {
    final JsonNode currCustom = definitionJson.get("custom");
    if (currCustom == null || currCustom.isNull()) {
      // definitions loaded from the cloud connector catalog are by definition not custom
      ((ObjectNode) definitionJson).set("custom", BooleanNode.FALSE);
    }
    return definitionJson;
  }

  @Override
  public <T> T getConfig(final AirbyteConfig configType, final String configId, final Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    final Map<String, JsonNode> configs = connectorCatalog.get(configType);
    if (configs == null) {
      throw new UnsupportedOperationException("There is no config for " + configType.name());
    }
    final JsonNode config = configs.get(configId);
    if (config == null) {
      throw new ConfigNotFoundException(configType, configId);
    }
    return Jsons.object(config, clazz);
  }

  @Override
  public <T> List<T> listConfigs(final AirbyteConfig configType, final Class<T> clazz) {
    final Map<String, JsonNode> configs = connectorCatalog.get(configType);
    if (configs == null) {
      throw new UnsupportedOperationException("There is no config for " + configType.name());
    }
    return configs.values().stream().map(json -> Jsons.object(json, clazz)).collect(Collectors.toList());
  }

  @Override
  public <T> ConfigWithMetadata<T> getConfigWithMetadata(final AirbyteConfig configType, final String configId, final Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    throw new UnsupportedOperationException("Remote catalog config doesn't support metadata");
  }

  @Override
  public <T> List<ConfigWithMetadata<T>> listConfigsWithMetadata(final AirbyteConfig configType, final Class<T> clazz)
      throws JsonValidationException, IOException {
    throw new UnsupportedOperationException("Remote catalog config doesn't support metadata");
  }

  @Override
  public <T> void writeConfig(final AirbyteConfig configType, final String configId, final T config) {
    throw new UnsupportedOperationException(PERSISTENCE_READ_ONLY_ERROR_MSG);
  }

  @Override
  public <T> void writeConfigs(final AirbyteConfig configType, final Map<String, T> configs) {
    throw new UnsupportedOperationException(PERSISTENCE_READ_ONLY_ERROR_MSG);
  }

  @Override
  public void deleteConfig(final AirbyteConfig configType, final String configId) {
    throw new UnsupportedOperationException(PERSISTENCE_READ_ONLY_ERROR_MSG);
  }

  @Override
  public void replaceAllConfigs(final Map<AirbyteConfig, Stream<?>> configs, final boolean dryRun) {
    throw new UnsupportedOperationException(PERSISTENCE_READ_ONLY_ERROR_MSG);
  }

  @Override
  public Map<String, Stream<JsonNode>> dumpConfigs() {
    return connectorCatalog.entrySet().stream().collect(Collectors.toMap(
        e -> e.getKey().name(),
        e -> e.getValue().values().stream()));
  }

  @Override
  public void loadData(final ConfigPersistence seedPersistence) throws IOException {
    throw new UnsupportedOperationException(PERSISTENCE_READ_ONLY_ERROR_MSG);
  }

}
