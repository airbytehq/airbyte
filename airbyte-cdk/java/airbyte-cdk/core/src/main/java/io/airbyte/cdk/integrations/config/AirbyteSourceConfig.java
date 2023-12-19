/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.config;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.nio.file.Path;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

public class AirbyteSourceConfig {

  private final JsonNode jsonConfig;

  public static enum AirbyteSourceConfigKey {
    ;

    private final String jsonName;

    private AirbyteSourceConfigKey(String jsonName) {
      this.jsonName = jsonName;
    }

  }

  AirbyteSourceConfig(JsonNode jsonConfig) {
    this.jsonConfig = jsonConfig;
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

  public static AirbyteSourceConfig fromMap(Map<String, Object> map) {
    return new AirbyteSourceConfig(Jsons.jsonNode(map));
  }

  public static AirbyteSourceConfig fromNothing() {
    return new AirbyteSourceConfig(Jsons.jsonNode(Collections.emptyMap()));
  }

  public AirbyteSourceConfigBuilder cloneBuilder() {
    return new AirbyteSourceConfigBuilder(this.jsonConfig);
  }

  public JsonNode asJsonNode() {
    return jsonConfig;
  }

  public final String getStringOrNull(String... keys) {
    return Jsons.getStringOrNull(jsonConfig, keys);
  }

  public final String getStringOrNull(List<String> keys) {
    return Jsons.getStringOrNull(jsonConfig, keys);
  }

  public final int getIntOrZero(String... keys) {
    return Jsons.getIntOrZero(jsonConfig, keys);
  }

  public final int getIntOrZero(List<String> keys) {
    return Jsons.getIntOrZero(jsonConfig, keys);
  }

  public final Optional<JsonNode> getOptional(String... keys) {
    return Jsons.getOptional(jsonConfig, keys);
  }

  public final JsonNode get(String key) {
    return jsonConfig.get(key);
  }

  public final boolean has(String key) {
    return jsonConfig.has(key);
  }

  public final Set<String> validateWith(JsonSchemaValidator validator, JsonNode schemaJson) {
    return validator.validate(schemaJson, this.jsonConfig);
  }

  public final boolean has(String key) {
    return jsonConfig.has(key);
  }

  public final JsonNode get(String key) {
    return jsonConfig.get(key);
  }

}
