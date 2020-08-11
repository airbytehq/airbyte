package io.dataline.config.persistence;

import java.util.Set;

public interface ConfigPersistence {
  <T> T getConfig(PersistenceConfigType persistenceConfigType, String configId, Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException;

  <T> Set<T> getConfigs(PersistenceConfigType persistenceConfigType, Class<T> clazz)
      throws JsonValidationException;

  <T> void writeConfig(PersistenceConfigType persistenceConfigType, String configId, T config);
}
