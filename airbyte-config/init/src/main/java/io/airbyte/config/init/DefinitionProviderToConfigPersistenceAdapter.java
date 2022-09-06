/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.ConfigWithMetadata;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Stream;

public class DefinitionProviderToConfigPersistenceAdapter implements ConfigPersistence {

  private final DefinitionsProvider definitionsProvider;
  private static final String PERSISTENCE_READ_ONLY_ERROR_MSG = "The remote definitions are read only.";

  public DefinitionProviderToConfigPersistenceAdapter(DefinitionsProvider definitionsProvider) {
    this.definitionsProvider = definitionsProvider;
  }

  @Override
  public <T> T getConfig(AirbyteConfig configType, String configId, Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    if (configType == ConfigSchema.STANDARD_SOURCE_DEFINITION && clazz == StandardSourceDefinition.class) {
      return (T) definitionsProvider.getSourceDefinition(UUID.fromString(configId));
    } else if (configType == ConfigSchema.STANDARD_DESTINATION_DEFINITION && clazz == StandardDestinationDefinition.class) {
      return (T) definitionsProvider.getDestinationDefinition(UUID.fromString(configId));
    } else {
      throw new UnsupportedOperationException("The config type you passed does not match any existing model class.");
    }
  }

  @Override
  public <T> List<T> listConfigs(AirbyteConfig configType, Class<T> clazz) throws JsonValidationException, IOException {
    if (configType == ConfigSchema.STANDARD_SOURCE_DEFINITION && clazz == StandardSourceDefinition.class) {
      return (List<T>) definitionsProvider.getSourceDefinitions();
    } else if (configType == ConfigSchema.STANDARD_DESTINATION_DEFINITION && clazz == StandardDestinationDefinition.class) {
      return (List<T>) definitionsProvider.getDestinationDefinitions();
    } else {
      throw new UnsupportedOperationException("The config type you passed does not match any existing model class.");
    }
  }

  @Override
  public <T> ConfigWithMetadata<T> getConfigWithMetadata(AirbyteConfig configType, String configId, Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    return null;
  }

  @Override
  public <T> List<ConfigWithMetadata<T>> listConfigsWithMetadata(AirbyteConfig configType, Class<T> clazz)
      throws JsonValidationException, IOException {
    throw new UnsupportedOperationException("Definition provider doesn't support metadata");
  }

  @Override
  public <T> void writeConfig(AirbyteConfig configType, String configId, T config) throws JsonValidationException, IOException {
    throw new UnsupportedOperationException(PERSISTENCE_READ_ONLY_ERROR_MSG);

  }

  @Override
  public <T> void writeConfigs(AirbyteConfig configType, Map<String, T> configs) throws IOException, JsonValidationException {
    throw new UnsupportedOperationException(PERSISTENCE_READ_ONLY_ERROR_MSG);

  }

  @Override
  public void deleteConfig(AirbyteConfig configType, String configId) throws ConfigNotFoundException, IOException {
    throw new UnsupportedOperationException(PERSISTENCE_READ_ONLY_ERROR_MSG);

  }

  @Override
  public void replaceAllConfigs(Map<AirbyteConfig, Stream<?>> configs, boolean dryRun) throws IOException {
    throw new UnsupportedOperationException(PERSISTENCE_READ_ONLY_ERROR_MSG);
  }

  @Override
  public Map<String, Stream<JsonNode>> dumpConfigs() throws IOException {
    Stream<JsonNode> jsonSourceDefinitions = definitionsProvider.getSourceDefinitions().stream().map(Jsons::jsonNode);
    Stream<JsonNode> jsonDestinationDefinitions = definitionsProvider.getDestinationDefinitions().stream().map(Jsons::jsonNode);
    return Map.of(SeedType.STANDARD_SOURCE_DEFINITION.name(), jsonSourceDefinitions, SeedType.STANDARD_DESTINATION_DEFINITION.name(),
        jsonDestinationDefinitions);
  }

  @Override
  public void loadData(ConfigPersistence seedPersistence) throws IOException {
    throw new UnsupportedOperationException(PERSISTENCE_READ_ONLY_ERROR_MSG);

  }

}
