/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Stream;

public class GoogleSecretsManagerConfigPersistence implements ConfigPersistence {

  public GoogleSecretsManagerConfigPersistence() {}

  public String getVersion() {
    return "secrets-v1";
  }

  // @Override
  public void loadData(ConfigPersistence seedPersistence) throws IOException {
    loadData(seedPersistence, new HashSet<String>());
  }

  public void loadData(ConfigPersistence seedPersistence, Set<String> configsInUse) throws IOException {
    // Don't need to do anything because the seed persistence only contains
    // non-secret configs, which we don't load into the secrets store.
  }

  /**
   * Returns the definition ids for every connector we're storing. Hopefully this can be refactored
   * into not existing once we have secrets as coordinates instead of storing the whole config as a
   * single secret.
   */
  public Set<String> listDefinitionIdsInUseByConnectors() {
    Set<String> definitionIds = new HashSet<String>();
    try {
      List<SourceConnection> sources = listConfigs(ConfigSchema.SOURCE_CONNECTION, SourceConnection.class);
      for (SourceConnection source : sources) {
        definitionIds.add(source.getSourceDefinitionId().toString());
      }
      List<DestinationConnection> destinations = listConfigs(ConfigSchema.DESTINATION_CONNECTION, DestinationConnection.class);
      for (DestinationConnection dest : destinations) {
        definitionIds.add(dest.getDestinationDefinitionId().toString());
      }
      return definitionIds;
    } catch (IOException | JsonValidationException io) {
      throw new RuntimeException(io);
    }
  }

  // @Override
  public Set<String> getRepositoriesFromDefinitionIds(Set<String> usedConnectorDefinitionIds) throws IOException {
    throw new UnsupportedOperationException(
        "Secrets Manager does not store the list of definitions and thus cannot be used to look up docker repositories.");
  }

  /**
   * Determines the secrets manager key name for storing a particular config
   */
  protected <T> String generateKeyNameFromType(AirbyteConfig configType, String configId) {
    return String.format("%s-%s-%s-configuration", getVersion(), configType.getIdFieldName(), configId);
  }

  protected <T> String generateKeyPrefixFromType(AirbyteConfig configType) {
    return String.format("%s-%s-", getVersion(), configType.getIdFieldName());
  }

  @Override
  public <T> T getConfig(AirbyteConfig configType, String configId, Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    String keyName = generateKeyNameFromType(configType, configId);
    return Jsons.deserialize(GoogleSecretsManager.readSecret(keyName), clazz);
  }

  @Override
  public <T> List<T> listConfigs(AirbyteConfig configType, Class<T> clazz) throws JsonValidationException, IOException {
    List<T> configs = new ArrayList<T>();
    for (String keyName : GoogleSecretsManager.listSecretsMatching(generateKeyPrefixFromType(configType))) {
      configs.add(Jsons.deserialize(GoogleSecretsManager.readSecret(keyName), clazz));
    }
    return configs;
  }

  @Override
  public <T> void writeConfig(AirbyteConfig configType, String configId, T config) throws JsonValidationException, IOException {
    String keyName = generateKeyNameFromType(configType, configId);
    System.out.println("keyname " + keyName);
    GoogleSecretsManager.saveSecret(keyName, Jsons.serialize(config));
  }

  @Override
  public void deleteConfig(AirbyteConfig configType, String configId) throws ConfigNotFoundException, IOException {
    String keyName = generateKeyNameFromType(configType, configId);
    GoogleSecretsManager.deleteSecret(keyName);
  }

  @Override
  public void replaceAllConfigs(Map<AirbyteConfig, Stream<?>> configs, boolean dryRun) throws IOException {
    if (dryRun) {
      for (final Map.Entry<AirbyteConfig, Stream<?>> configuration : configs.entrySet()) {
        configuration.getValue().forEach(Jsons::serialize);
      }
      return;
    }
    for (final Map.Entry<AirbyteConfig, Stream<?>> configuration : configs.entrySet()) {
      AirbyteConfig configType = configuration.getKey();
      configuration.getValue().forEach(config -> {
        try {
          GoogleSecretsManager.saveSecret(generateKeyNameFromType(configType, configType.getId(config)), Jsons.serialize(config));
        } catch (IOException e) {
          throw new RuntimeException(e);
        }
      });
    }
  }

  @Override
  public Map<String, Stream<JsonNode>> dumpConfigs() throws IOException {
    final Map<String, Stream<JsonNode>> configs = new HashMap<>();

    for (AirbyteConfig ctype : new ConfigSchema[] {ConfigSchema.SOURCE_CONNECTION, ConfigSchema.DESTINATION_CONNECTION}) {
      List<String> names = GoogleSecretsManager.listSecretsMatching(generateKeyPrefixFromType(ctype));
      final List<JsonNode> configList = new ArrayList<JsonNode>();
      for (String name : names) {
        configList.add(Jsons.deserialize(GoogleSecretsManager.readSecret(name), JsonNode.class));
      }
      configs.put(ctype.name(), configList.stream());
    }

    return configs;
  }

}
