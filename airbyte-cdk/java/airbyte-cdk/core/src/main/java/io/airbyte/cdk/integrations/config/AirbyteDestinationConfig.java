package io.airbyte.cdk.db;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.AirbyteSourceConfig.SourceConfigBuilder;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import java.nio.file.Path;
import java.util.Map;

public class AirbyteDestinationConfig extends AirbyteConfig<AirbyteDestinationConfig> {
  public static class DestinationConfigBuilder extends AirbyteConfigBuilder<AirbyteDestinationConfig> {
    public DestinationConfigBuilder(AirbyteDestinationConfig sourceConfig) {
      super(sourceConfig);
    }

    public DestinationConfigBuilder with(String key, String value) {
      jsonConfig.put(key, value);
      return this;
    }

    public DestinationConfigBuilder with(String key, boolean value) {
      jsonConfig.put(key, value);
      return this;
    }

    public DestinationConfigBuilder with(String key, JsonNode value) {
      jsonConfig.put(key, value);
      return this;
    }

    public AirbyteDestinationConfig build() {
      return new AirbyteDestinationConfig(jsonConfig);
    }
  }

  private AirbyteDestinationConfig(JsonNode jsonConfig) {
    super(jsonConfig);
  }

  public static AirbyteDestinationConfig fromPath(final Path path) {
    return new AirbyteDestinationConfig(Jsons.deserialize(IOs.readFile(path)));
  }

  public static AirbyteDestinationConfig fromNothing() {
    return new AirbyteDestinationConfig(Jsons.emptyObject());
  }

  public static AirbyteDestinationConfig fromJsonString(String jsonString) {
    return new AirbyteDestinationConfig(Jsons.deserialize(jsonString));
  }

  public static AirbyteDestinationConfig fromJsonNode(JsonNode jsonNode) {
    return new AirbyteDestinationConfig(jsonNode);
  }

  public static<K, V> AirbyteDestinationConfig of(K k1, V v1) {
    return new AirbyteDestinationConfig(Jsons.jsonNode(Map.of(k1, v1)));
  }

  public static<K, V> AirbyteDestinationConfig of(K k1, V v1, K k2, V v2) {
    return new AirbyteDestinationConfig(Jsons.jsonNode(Map.of(k1, v1, k2, v2)));
  }

  public static<K, V> AirbyteDestinationConfig of(K k1, V v1, K k2, V v2, K k3, V v3) {
    return new AirbyteDestinationConfig(Jsons.jsonNode(Map.of(k1, v1, k2, v2, k3, v3)));
  }

  public static<K, V> AirbyteDestinationConfig of(K k1, V v1, K k2, V v2, K k3, V v3, K k4, V v4) {
    return new AirbyteDestinationConfig(Jsons.jsonNode(Map.of(k1, v1, k2, v2, k3, v3, k4, v4)));
  }

  public static<K, V> AirbyteDestinationConfig of(K k1, V v1, K k2, V v2, K k3, V v3, K k4, V v4, K k5, V v5) {
    return new AirbyteDestinationConfig(Jsons.jsonNode(Map.of(k1, v1, k2, v2, k3, v3, k4, v4, k5, v5)));
  }

  public DestinationConfigBuilder cloneBuilder() {
    return new DestinationConfigBuilder(this);
  }

  public JsonNode asJsonNode() {
    return jsonConfig;
  }
}
