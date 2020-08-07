package io.dataline.conduit.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Set;

public interface ConfigPersistence {
  JsonNode getConfig(ConfigType configType, String configId);

  Set<JsonNode> getConfigs(ConfigType configType);

  void updateConfig(ConfigType configType, String configId, JsonNode config);

  void createConfig(ConfigType configType, String configId, JsonNode config);
}
