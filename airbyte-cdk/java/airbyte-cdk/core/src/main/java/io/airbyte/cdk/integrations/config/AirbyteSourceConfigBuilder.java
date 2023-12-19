package io.airbyte.cdk.integrations.config;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import java.util.List;

public class AirbyteSourceConfigBuilder {

  private final ObjectNode jsonConfig;

  AirbyteSourceConfigBuilder(JsonNode jsonConfig) {
    this.jsonConfig = (ObjectNode) Jsons.clone(jsonConfig);
  }

  public AirbyteSourceConfig build() {
    return new AirbyteSourceConfig(jsonConfig);
  }

  public AirbyteSourceConfigBuilder with(String key, String value) {
    jsonConfig.put(key, value);
    return this;
  }

  public AirbyteSourceConfigBuilder with(String key, boolean value) {
    jsonConfig.put(key, value);
    return this;
  }

  public void replaceNestedString(List<String> keys, String replacement) {
    Jsons.replaceNestedString(jsonConfig, keys, replacement);
  }

  public void replaceNestedInt(List<String> keys, int replacement) {
    Jsons.replaceNestedInt(jsonConfig, keys, replacement);
  }

}
