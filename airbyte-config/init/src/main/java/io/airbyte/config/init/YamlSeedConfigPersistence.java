/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.BooleanNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.io.Resources;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.ConfigWithMetadata;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * This config persistence contains all seed definitions according to the yaml files. It is
 * read-only.
 */
public class YamlSeedConfigPersistence implements ConfigPersistence {

  public static Class<?> DEFAULT_SEED_DEFINITION_RESOURCE_CLASS = SeedType.class;

  private static final Map<AirbyteConfig, SeedType> CONFIG_SCHEMA_MAP = Map.of(
      ConfigSchema.STANDARD_SOURCE_DEFINITION, SeedType.STANDARD_SOURCE_DEFINITION,
      ConfigSchema.STANDARD_DESTINATION_DEFINITION, SeedType.STANDARD_DESTINATION_DEFINITION);

  // A mapping from seed config type to config UUID to config.
  private final ImmutableMap<SeedType, Map<String, JsonNode>> allSeedConfigs;

  public static YamlSeedConfigPersistence getDefault() throws IOException {
    return new YamlSeedConfigPersistence(DEFAULT_SEED_DEFINITION_RESOURCE_CLASS);
  }

  public static YamlSeedConfigPersistence get(final Class<?> seedDefinitionsResourceClass) throws IOException {
    return new YamlSeedConfigPersistence(seedDefinitionsResourceClass);
  }

  private YamlSeedConfigPersistence(final Class<?> seedResourceClass) throws IOException {
    final Map<String, JsonNode> sourceDefinitionConfigs = getConfigs(seedResourceClass, SeedType.STANDARD_SOURCE_DEFINITION);
    final Map<String, JsonNode> sourceSpecConfigs = getConfigs(seedResourceClass, SeedType.SOURCE_SPEC);
    final Map<String, JsonNode> fullSourceDefinitionConfigs = sourceDefinitionConfigs.entrySet().stream()
        .collect(Collectors.toMap(Entry::getKey, e -> {
          final JsonNode withTombstone = addMissingTombstoneField(e.getValue());
          return mergeSpecIntoDefinition(withTombstone, sourceSpecConfigs);
        }));

    final Map<String, JsonNode> destinationDefinitionConfigs = getConfigs(seedResourceClass, SeedType.STANDARD_DESTINATION_DEFINITION);
    final Map<String, JsonNode> destinationSpecConfigs = getConfigs(seedResourceClass, SeedType.DESTINATION_SPEC);
    final Map<String, JsonNode> fullDestinationDefinitionConfigs = destinationDefinitionConfigs.entrySet().stream()
        .collect(Collectors.toMap(Entry::getKey, e -> {
          final JsonNode withTombstone = addMissingTombstoneField(e.getValue());
          return mergeSpecIntoDefinition(withTombstone, destinationSpecConfigs);
        }));

    this.allSeedConfigs = ImmutableMap.<SeedType, Map<String, JsonNode>>builder()
        .put(SeedType.STANDARD_SOURCE_DEFINITION, fullSourceDefinitionConfigs)
        .put(SeedType.STANDARD_DESTINATION_DEFINITION, fullDestinationDefinitionConfigs).build();
  }

  /**
   * Merges the corresponding spec JSON into the definition JSON. This is necessary because specs are
   * stored in a separate resource file from definitions.
   *
   * @param definitionJson JSON of connector definition that is missing a spec
   * @param specConfigs map of docker image to JSON of docker image/connector spec pair
   * @return JSON of connector definition including the connector spec
   */
  private JsonNode mergeSpecIntoDefinition(final JsonNode definitionJson, final Map<String, JsonNode> specConfigs) {
    final String dockerImage = DockerUtils.getTaggedImageName(
        definitionJson.get("dockerRepository").asText(),
        definitionJson.get("dockerImageTag").asText());
    final JsonNode specConfigJson = specConfigs.get(dockerImage);
    if (specConfigJson == null || specConfigJson.get("spec") == null) {
      throw new UnsupportedOperationException(String.format("There is no seed spec for docker image %s", dockerImage));
    }
    ((ObjectNode) definitionJson).set("spec", specConfigJson.get("spec"));
    return definitionJson;
  }

  private JsonNode addMissingTombstoneField(final JsonNode definitionJson) {
    final JsonNode currTombstone = definitionJson.get("tombstone");
    if (currTombstone == null || currTombstone.isNull()) {
      ((ObjectNode) definitionJson).set("tombstone", BooleanNode.FALSE);
    }
    return definitionJson;
  }

  @SuppressWarnings("UnstableApiUsage")

  private static Map<String, JsonNode> getConfigs(final Class<?> seedDefinitionsResourceClass, final SeedType seedType) throws IOException {
    final URL url = Resources.getResource(seedDefinitionsResourceClass, seedType.getResourcePath());
    final String yamlString = Resources.toString(url, StandardCharsets.UTF_8);
    final JsonNode configList = Yamls.deserialize(yamlString);
    return MoreIterators.toList(configList.elements()).stream().collect(Collectors.toMap(
        json -> json.get(seedType.getIdName()).asText(),
        json -> json));
  }

  @Override
  public <T> T getConfig(final AirbyteConfig configType, final String configId, final Class<T> clazz)
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
  public <T> List<T> listConfigs(final AirbyteConfig configType, final Class<T> clazz) {
    final Map<String, JsonNode> configs = allSeedConfigs.get(CONFIG_SCHEMA_MAP.get(configType));
    if (configs == null) {
      throw new UnsupportedOperationException("There is no seed for " + configType.name());
    }
    return configs.values().stream().map(json -> Jsons.object(json, clazz)).collect(Collectors.toList());
  }

  @Override
  public <T> ConfigWithMetadata<T> getConfigWithMetadata(final AirbyteConfig configType, final String configId, final Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    throw new UnsupportedOperationException("Yaml Seed Config doesn't support metadata");
  }

  @Override
  public <T> List<ConfigWithMetadata<T>> listConfigsWithMetadata(final AirbyteConfig configType, final Class<T> clazz)
      throws JsonValidationException, IOException {
    throw new UnsupportedOperationException("Yaml Seed Config doesn't support metadata");
  }

  @Override
  public <T> void writeConfig(final AirbyteConfig configType, final String configId, final T config) {
    throw new UnsupportedOperationException("The seed config persistence is read only.");
  }

  @Override
  public <T> void writeConfigs(final AirbyteConfig configType, final Map<String, T> configs) {
    throw new UnsupportedOperationException("The seed config persistence is read only.");
  }

  @Override
  public void deleteConfig(final AirbyteConfig configType, final String configId) {
    throw new UnsupportedOperationException("The seed config persistence is read only.");
  }

  @Override
  public void replaceAllConfigs(final Map<AirbyteConfig, Stream<?>> configs, final boolean dryRun) {
    throw new UnsupportedOperationException("The seed config persistence is read only.");
  }

  @Override
  public Map<String, Stream<JsonNode>> dumpConfigs() {
    return allSeedConfigs.entrySet().stream().collect(Collectors.toMap(
        e -> e.getKey().name(),
        e -> e.getValue().values().stream()));
  }

  @Override
  public void loadData(final ConfigPersistence seedPersistence) throws IOException {
    throw new UnsupportedOperationException("The seed config persistence is read only.");
  }

}
