/*
 * Copyright (c) 2020 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.io.Resources;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.init.SeedType;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * This config persistence contains all seed definitions according to the yaml files. It is
 * read-only.
 */
public class YamlSeedConfigPersistence implements ConfigPersistence {

  private static final Map<AirbyteConfig, SeedType> CONFIG_SCHEMA_MAP = Map.of(
      ConfigSchema.STANDARD_SOURCE_DEFINITION, SeedType.STANDARD_SOURCE_DEFINITION,
      ConfigSchema.STANDARD_DESTINATION_DEFINITION, SeedType.STANDARD_DESTINATION_DEFINITION);

  private static final YamlSeedConfigPersistence INSTANCE;
  static {
    try {
      INSTANCE = new YamlSeedConfigPersistence();
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  // A mapping from seed config type to config UUID to config.
  private final ImmutableMap<SeedType, Map<String, JsonNode>> allSeedConfigs;

  private YamlSeedConfigPersistence() throws IOException {
    this.allSeedConfigs = ImmutableMap.<SeedType, Map<String, JsonNode>>builder()
        .put(SeedType.STANDARD_SOURCE_DEFINITION, getConfigs(SeedType.STANDARD_SOURCE_DEFINITION))
        .put(SeedType.STANDARD_DESTINATION_DEFINITION, getConfigs(SeedType.STANDARD_DESTINATION_DEFINITION))
        .build();
  }

  public static YamlSeedConfigPersistence get() {
    return INSTANCE;
  }

  @SuppressWarnings("UnstableApiUsage")
  private static Map<String, JsonNode> getConfigs(SeedType seedType) throws IOException {
    final URL url = Resources.getResource(SeedType.class, seedType.getResourcePath());
    final String yamlString = Resources.toString(url, StandardCharsets.UTF_8);
    final JsonNode configList = Yamls.deserialize(yamlString);
    return MoreIterators.toList(configList.elements()).stream().collect(Collectors.toMap(
        json -> json.get(seedType.getIdName()).asText(),
        json -> json));
  }

  @Override
  public <T> T getConfig(AirbyteConfig configType, String configId, Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    final Map<String, JsonNode> configs = allSeedConfigs.get(CONFIG_SCHEMA_MAP.get(configType));
    if (configs == null) {
      throw new UnsupportedOperationException("There is no seed for " + configType.name());
    }
    final JsonNode config = configs.get(configId);
    if (config == null) {
      throw new ConfigNotFoundException(configType, configId);
    }
    return Jsons.object(config, clazz);
  }

  @Override
  public <T> List<T> listConfigs(AirbyteConfig configType, Class<T> clazz) {
    final Map<String, JsonNode> configs = allSeedConfigs.get(CONFIG_SCHEMA_MAP.get(configType));
    if (configs == null) {
      throw new UnsupportedOperationException("There is no seed for " + configType.name());
    }
    return configs.values().stream().map(json -> Jsons.object(json, clazz)).collect(Collectors.toList());
  }

  @Override
  public <T> void writeConfig(AirbyteConfig configType, String configId, T config) {
    throw new UnsupportedOperationException("The seed config persistence is read only.");
  }

  @Override
  public void deleteConfig(AirbyteConfig configType, String configId) {
    throw new UnsupportedOperationException("The seed config persistence is read only.");
  }

  @Override
  public void replaceAllConfigs(Map<AirbyteConfig, Stream<?>> configs, boolean dryRun) {
    throw new UnsupportedOperationException("The seed config persistence is read only.");
  }

  @Override
  public Map<String, Stream<JsonNode>> dumpConfigs() {
    return allSeedConfigs.entrySet().stream().collect(Collectors.toMap(
        e -> e.getKey().name(),
        e -> e.getValue().values().stream()));
  }

  @Override
  public void loadData(ConfigPersistence seedPersistence) throws IOException {
    throw new UnsupportedOperationException("The seed config persistence is read only.");
  }

}
