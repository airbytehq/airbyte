package io.airbyte.cdk.db;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import java.nio.file.Path;
import java.util.Collections;
import java.util.Map;

public class AirbyteSourceConfig extends AirbyteConfig<AirbyteSourceConfig>{
  public static class SourceConfigBuilder extends AirbyteConfigBuilder<AirbyteSourceConfig> {
    public SourceConfigBuilder(AirbyteSourceConfig sourceConfig) {
      super(sourceConfig);
    }

    public AirbyteSourceConfig build() {
      return new AirbyteSourceConfig(jsonConfig);
    }

    public SourceConfigBuilder with(String key, String value) {
      jsonConfig.put(key, value);
      return this;
    }

    public SourceConfigBuilder with(String key, boolean value) {
      jsonConfig.put(key, value);
      return this;
    }
  }

  private AirbyteSourceConfig(JsonNode jsonConfig) {
    super(jsonConfig);
  }

  public static AirbyteSourceConfig fromPath(final Path path) {
    return new AirbyteSourceConfig(Jsons.deserialize(IOs.readFile(path)));
  }

  public static AirbyteSourceConfig fromJsonNode(final JsonNode jsonNode) {
    return new AirbyteSourceConfig(jsonNode);
  }

  public static AirbyteSourceConfig fromJsonString(final String jsonString) {
    return new AirbyteSourceConfig(Jsons.deserialize(jsonString));
  }

  public SourceConfigBuilder cloneBuilder() {
    return new SourceConfigBuilder(this);
  }

  public JsonNode asJsonNode() {
    return jsonConfig;
  }

  public static AirbyteSourceConfig of(String k1, Object k2) {
    return new AirbyteSourceConfig(Jsons.jsonNode(Map.of(k1, k2)));
  }

  public static AirbyteSourceConfig of(String k1, Object k2, String k3, Object k4) {
    return new AirbyteSourceConfig(Jsons.jsonNode(Map.of(k1, k2, k3, k4)));
  }

  public static AirbyteSourceConfig of(String k1, Object k2, String k3, Object k4, String k5, Object k6) {
    return new AirbyteSourceConfig(Jsons.jsonNode(Map.of(k1, k2, k3, k4, k5, k6)));
  }

  public static AirbyteSourceConfig fromNothing() {
    return new AirbyteSourceConfig(Jsons.jsonNode(Collections.emptyMap()));
  }
}
