/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.exasol;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.db.jdbc.JdbcUtils;
import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.shaded.com.google.common.collect.ImmutableMap;

class ExasolDestinationTest {

  private ExasolDestination destination;

  @BeforeEach
  void setup() {
    destination = new ExasolDestination();
  }

  private JsonNode createConfig() {
    return createConfig(new HashMap<>());
  }

  private JsonNode createConfig(final Map<String, Object> additionalConfigs) {
    return Jsons.jsonNode(MoreMaps.merge(baseParameters(), additionalConfigs));
  }

  private Map<String, Object> baseParameters() {
    return ImmutableMap.<String, Object>builder()
        .put(JdbcUtils.HOST_KEY, "localhost")
        .put(JdbcUtils.PORT_KEY, "8563")
        .put(JdbcUtils.USERNAME_KEY, "sys")
        .put(JdbcUtils.SCHEMA_KEY, "mySchema")
        .build();
  }

  @Test
  void toJdbcConfigDefault() {
    var result = destination.toJdbcConfig(createConfig());
    assertAll(
        () -> assertThat(result.size(), equalTo(3)),
        () -> assertThat(result.get(JdbcUtils.USERNAME_KEY).asText(), equalTo("sys")),
        () -> assertThat(result.get(JdbcUtils.JDBC_URL_KEY).asText(), equalTo("jdbc:exa:localhost:8563")),
        () -> assertThat(result.get(JdbcUtils.SCHEMA_KEY).asText(), equalTo("mySchema")));
  }

  @Test
  void toJdbcConfigWithPassword() {
    var result = destination.toJdbcConfig(createConfig(Map.of(JdbcUtils.PASSWORD_KEY, "exasol")));
    assertAll(
        () -> assertThat(result.size(), equalTo(4)),
        () -> assertThat(result.get(JdbcUtils.PASSWORD_KEY).asText(), equalTo("exasol")));
  }

  @Test
  void toJdbcConfigWithJdbcUrlParameters() {
    var result = destination.toJdbcConfig(createConfig(Map.of(JdbcUtils.JDBC_URL_PARAMS_KEY, "param=value")));
    assertAll(
        () -> assertThat(result.size(), equalTo(4)),
        () -> assertThat(result.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText(), equalTo("param=value")));
  }

  @Test
  void getDefaultConnectionProperties() {
    var result = destination.getDefaultConnectionProperties(createConfig());
    assertThat(result, equalTo(Map.of("autocommit", "0")));
  }

  @Test
  void getDefaultConnectionPropertiesWithFingerprint() {
    var result = destination.getDefaultConnectionProperties(createConfig(Map.of("certificateFingerprint", "ABC")));
    assertThat(result, equalTo(Map.of("fingerprint", "ABC", "autocommit", "0")));
  }

}
