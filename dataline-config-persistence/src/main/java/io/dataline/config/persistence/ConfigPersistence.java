package io.dataline.config.persistence;

import java.util.Set;

public interface ConfigPersistence {
  <T> T getConfig(PersistenceConfigType persistenceConfigType, String configId, Class<T> clazz);

  <T> Set<T> getConfigs(PersistenceConfigType persistenceConfigType, Class<T> clazz);

  <T> void writeConfig(
      PersistenceConfigType persistenceConfigType, String configId, T config, Class<T> clazz);
}
