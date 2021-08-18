package io.airbyte.config.persistence;

import io.airbyte.config.Configs;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConfigSeedProvider {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConfigSeedProvider.class);

  public static ConfigPersistence get(Configs configs) {
    if (FileSystemConfigPersistence.hasExistingConfigs(configs.getConfigRoot())) {
      LOGGER.info("There is existing local config directory; seed from the config volume");
      return new FileSystemConfigPersistence(configs.getConfigRoot());
    } else {
      LOGGER.info("There is no existing local config directory; seed from YAML files");
      return YamlSeedConfigPersistence.get();
    }
  }

}
