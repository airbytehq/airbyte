/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigWithMetadata;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.Map;

/**
 * We are moving migrating away from this interface entirely. Use ConfigRepository instead.
 */
@Deprecated(forRemoval = true)
public interface ConfigPersistence {

  <T> T getConfig(AirbyteConfig configType, String configId, Class<T> clazz) throws ConfigNotFoundException, JsonValidationException, IOException;

  <T> List<T> listConfigs(AirbyteConfig configType, Class<T> clazz) throws JsonValidationException, IOException;

  <T> ConfigWithMetadata<T> getConfigWithMetadata(AirbyteConfig configType, String configId, Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException;

  <T> List<ConfigWithMetadata<T>> listConfigsWithMetadata(AirbyteConfig configType, Class<T> clazz) throws JsonValidationException, IOException;

  <T> void writeConfig(AirbyteConfig configType, String configId, T config) throws JsonValidationException, IOException;

  <T> void writeConfigs(AirbyteConfig configType, Map<String, T> configs) throws IOException, JsonValidationException;

  void deleteConfig(AirbyteConfig configType, String configId) throws ConfigNotFoundException, IOException;

}
