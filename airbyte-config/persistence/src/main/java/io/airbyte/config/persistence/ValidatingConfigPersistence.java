/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigWithMetadata;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;

// we force all interaction with disk storage to be effectively single threaded.
public class ValidatingConfigPersistence implements ConfigPersistence {

  private final JsonSchemaValidator schemaValidator;
  private final ConfigPersistence decoratedPersistence;

  public ValidatingConfigPersistence(final ConfigPersistence decoratedPersistence) {
    this(decoratedPersistence, new JsonSchemaValidator());
  }

  public ValidatingConfigPersistence(final ConfigPersistence decoratedPersistence, final JsonSchemaValidator schemaValidator) {
    this.decoratedPersistence = decoratedPersistence;
    this.schemaValidator = schemaValidator;
  }

  @Override
  public <T> T getConfig(final AirbyteConfig configType, final String configId, final Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    final T config = decoratedPersistence.getConfig(configType, configId, clazz);
    validateJson(config, configType);
    return config;
  }

  @Override
  public <T> List<T> listConfigs(final AirbyteConfig configType, final Class<T> clazz) throws JsonValidationException, IOException {
    final List<T> configs = decoratedPersistence.listConfigs(configType, clazz);
    for (final T config : configs) {
      validateJson(config, configType);
    }
    return configs;
  }

  @Override
  public <T> List<ConfigWithMetadata<T>> listConfigsWithMetadata(final AirbyteConfig configType, final Class<T> clazz)
      throws JsonValidationException, IOException {
    final List<ConfigWithMetadata<T>> configs = decoratedPersistence.listConfigsWithMetadata(configType, clazz);
    for (final ConfigWithMetadata<T> config : configs) {
      validateJson(config.getConfig(), configType);
    }
    return configs;
  }

  @Override
  public <T> void writeConfig(final AirbyteConfig configType, final String configId, final T config) throws JsonValidationException, IOException {

    final Map<String, T> configIdToConfig = new HashMap<>() {

      {
        put(configId, config);
      }

    };

    writeConfigs(configType, configIdToConfig);
  }

  @Override
  public <T> void writeConfigs(final AirbyteConfig configType, final Map<String, T> configs)
      throws IOException, JsonValidationException {
    for (final Map.Entry<String, T> config : configs.entrySet()) {
      validateJson(Jsons.jsonNode(config.getValue()), configType);
    }
    decoratedPersistence.writeConfigs(configType, configs);
  }

  @Override
  public void deleteConfig(final AirbyteConfig configType, final String configId) throws ConfigNotFoundException, IOException {
    decoratedPersistence.deleteConfig(configType, configId);
  }

  @Override
  public void replaceAllConfigs(final Map<AirbyteConfig, Stream<?>> configs, final boolean dryRun) throws IOException {
    // todo (cgardens) need to do validation here.
    decoratedPersistence.replaceAllConfigs(configs, dryRun);
  }

  @Override
  public Map<String, Stream<JsonNode>> dumpConfigs() throws IOException {
    return decoratedPersistence.dumpConfigs();
  }

  @Override
  public void loadData(final ConfigPersistence seedPersistence) throws IOException {
    decoratedPersistence.loadData(seedPersistence);
  }

  private <T> void validateJson(final T config, final AirbyteConfig configType) throws JsonValidationException {
    final JsonNode schema = JsonSchemaValidator.getSchema(configType.getConfigSchemaFile());
    schemaValidator.ensure(schema, Jsons.jsonNode(config));
  }

}
