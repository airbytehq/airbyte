package io.dataline.conduit.persistence;

import java.util.Set;

public interface ConfigPersistence {
  <T> T getStandardConfig(
      PersistenceConfigType persistenceConfigType, String configId, Class<T> clazz);

  <T> Set<T> getStandardConfigs(PersistenceConfigType persistenceConfigType, Class<T> clazz);

  <T> void writeStandardConfig(
      PersistenceConfigType persistenceConfigType, String configId, T config, Class<T> clazz);
}
