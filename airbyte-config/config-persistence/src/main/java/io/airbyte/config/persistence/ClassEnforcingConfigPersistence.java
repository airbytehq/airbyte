/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.api.client.util.Preconditions;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigWithMetadata;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * Validates that the class of inputs and outputs matches the class specified in the AirbyteConfig
 * enum. Helps avoid type mistakes, which can happen because this iface can't type check at compile
 * time.
 */
public class ClassEnforcingConfigPersistence implements ConfigPersistence {

  private final ConfigPersistence decoratedPersistence;

  public ClassEnforcingConfigPersistence(final ConfigPersistence decoratedPersistence) {
    this.decoratedPersistence = decoratedPersistence;
  }

  @Override
  public <T> T getConfig(final AirbyteConfig configType, final String configId, final Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    Preconditions.checkArgument(configType.getClassName().equals(clazz));
    return decoratedPersistence.getConfig(configType, configId, clazz);
  }

  @Override
  public <T> List<T> listConfigs(final AirbyteConfig configType, final Class<T> clazz) throws JsonValidationException, IOException {
    Preconditions.checkArgument(configType.getClassName().equals(clazz));
    return decoratedPersistence.listConfigs(configType, clazz);
  }

  @Override
  public <T> ConfigWithMetadata<T> getConfigWithMetadata(final AirbyteConfig configType, final String configId, final Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    Preconditions.checkArgument(configType.getClassName().equals(clazz));
    return decoratedPersistence.getConfigWithMetadata(configType, configId, clazz);
  }

  @Override
  public <T> List<ConfigWithMetadata<T>> listConfigsWithMetadata(final AirbyteConfig configType, final Class<T> clazz)
      throws JsonValidationException, IOException {
    Preconditions.checkArgument(configType.getClassName().equals(clazz));
    return decoratedPersistence.listConfigsWithMetadata(configType, clazz);
  }

  @Override
  public <T> void writeConfig(final AirbyteConfig configType, final String configId, final T config) throws JsonValidationException, IOException {
    Preconditions.checkArgument(configType.getClassName().equals(config.getClass()));
    decoratedPersistence.writeConfig(configType, configId, config);
  }

  @Override
  public <T> void writeConfigs(final AirbyteConfig configType, final Map<String, T> configs) throws IOException, JsonValidationException {
    // attempt to check the input type. if it is empty, then there is nothing to check.
    Preconditions.checkArgument(configs.isEmpty() || configType.getClassName().equals(new ArrayList<>(configs.values()).get(0).getClass()));
    decoratedPersistence.writeConfigs(configType, configs);
  }

  @Override
  public void deleteConfig(final AirbyteConfig configType, final String configId) throws ConfigNotFoundException, IOException {
    decoratedPersistence.deleteConfig(configType, configId);
  }

  @Override
  public void replaceAllConfigs(final Map<AirbyteConfig, Stream<?>> configs, final boolean dryRun) throws IOException {
    final Map<AirbyteConfig, Stream<?>> augmentedMap = new HashMap<>(configs).entrySet()
        .stream()
        .collect(Collectors.toMap(
            Entry::getKey,
            entry -> entry.getValue().peek(config -> Preconditions.checkArgument(entry.getKey().getClassName().equals(config.getClass())))));
    decoratedPersistence.replaceAllConfigs(augmentedMap, dryRun);
  }

  @Override
  public Map<String, Stream<JsonNode>> dumpConfigs() throws IOException {
    return decoratedPersistence.dumpConfigs();
  }

  @Override
  public void loadData(final ConfigPersistence seedPersistence) throws IOException {
    decoratedPersistence.loadData(seedPersistence);
  }

}
