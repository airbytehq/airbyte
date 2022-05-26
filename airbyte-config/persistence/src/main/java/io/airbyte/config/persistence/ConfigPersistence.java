/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigWithMetadata;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;

public interface ConfigPersistence {

  <T> T getConfig(AirbyteConfig configType, String configId, Class<T> clazz) throws ConfigNotFoundException, JsonValidationException, IOException;

  <T> List<T> listConfigs(AirbyteConfig configType, Class<T> clazz) throws JsonValidationException, IOException;

  <T> ConfigWithMetadata<T> getConfigWithMetadata(AirbyteConfig configType, String configId, Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException;

  <T> List<ConfigWithMetadata<T>> listConfigsWithMetadata(AirbyteConfig configType, Class<T> clazz) throws JsonValidationException, IOException;

  <T> void writeConfig(AirbyteConfig configType, String configId, T config) throws JsonValidationException, IOException;

  <T> void writeConfigs(AirbyteConfig configType, Map<String, T> configs) throws IOException, JsonValidationException;

  void deleteConfig(AirbyteConfig configType, String configId) throws ConfigNotFoundException, IOException;

  void replaceAllConfigs(Map<AirbyteConfig, Stream<?>> configs, boolean dryRun) throws IOException;

  Map<String, Stream<JsonNode>> dumpConfigs() throws IOException;

  void loadData(ConfigPersistence seedPersistence) throws IOException;

}
