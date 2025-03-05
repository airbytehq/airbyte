/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.integrations.destination.teradata.util.TeradataConstants;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class TeradataDestinationTest {

  private JsonNode config;
  final TeradataDestination destination = new TeradataDestination();

  private final String EXPECTED_JDBC_URL = "jdbc:teradata://localhost/";

  private final String EXTRA_JDBC_PARAMS = "key1=value1&key2=value2&key3=value3";

  private String getUserName() {
    return config.get(JdbcUtils.USERNAME_KEY).asText();
  }

  private String getPassword() {
    return config.get(JdbcUtils.PASSWORD_KEY).asText();
  }

  private String getHostName() {
    return config.get(JdbcUtils.HOST_KEY).asText();
  }

  private String getSchemaName() {
    return config.get(JdbcUtils.SCHEMA_KEY).asText();
  }

  @BeforeEach
  void setup() {
    this.config = createConfig();
  }

  private JsonNode createConfig() {
    return Jsons.jsonNode(baseParameters());
  }

  private JsonNode createConfig(boolean sslEnable) {
    JsonNode jsonNode;
    if (sslEnable) {
      jsonNode = Jsons.jsonNode(sslBaseParameters());
    } else {
      jsonNode = createConfig();
    }
    return jsonNode;
  }

  private JsonNode createConfig(final String sslMethod) {
    Map<String, Object> additionalParameters = getAdditionalParams(sslMethod);
    return Jsons.jsonNode(MoreMaps.merge(sslBaseParameters(), additionalParameters));
  }

  private Map<String, Object> getAdditionalParams(final String sslMethod) {
    Map<String, Object> additionalParameters;
    switch (sslMethod) {
      case "verify-ca", "verify-full" -> {
        additionalParameters = ImmutableMap.of(
            TeradataConstants.PARAM_SSL_MODE, Jsons.jsonNode(ImmutableMap.of(
                TeradataConstants.PARAM_MODE, sslMethod,
                TeradataConstants.CA_CERT_KEY, "dummycertificatecontent")));
      }
      default -> {
        additionalParameters = ImmutableMap.of(
            TeradataConstants.PARAM_SSL_MODE, Jsons.jsonNode(ImmutableMap.of(
                TeradataConstants.PARAM_MODE, sslMethod)));
      }
    }
    return additionalParameters;
  }

  private Map<String, Object> baseParameters() {
    return ImmutableMap.<String, Object>builder()
        .put(JdbcUtils.HOST_KEY, "localhost")
        .put(JdbcUtils.SCHEMA_KEY, "db")
        .put(JdbcUtils.USERNAME_KEY, "username")
        .put(JdbcUtils.PASSWORD_KEY, "verysecure")
        .build();
  }

  private Map<String, Object> sslBaseParameters() {
    return ImmutableMap.<String, Object>builder()
        .put(TeradataConstants.PARAM_SSL, "true")
        .put(JdbcUtils.HOST_KEY, getHostName())
        .put(JdbcUtils.SCHEMA_KEY, getSchemaName())
        .put(JdbcUtils.USERNAME_KEY, getUserName())
        .put(JdbcUtils.PASSWORD_KEY, getPassword())
        .build();
  }

  private JsonNode buildConfigNoJdbcParameters() {
    return Jsons.jsonNode(baseParameters());
  }

  private JsonNode buildConfigDefaultSchema() {
    return Jsons.jsonNode(ImmutableMap.of(
        JdbcUtils.HOST_KEY, getHostName(),
        JdbcUtils.USERNAME_KEY, getUserName(),
        JdbcUtils.PASSWORD_KEY, getPassword()));
  }

  private JsonNode buildConfigWithExtraJdbcParameters(final String extraParam) {
    return Jsons.jsonNode(ImmutableMap.of(
        JdbcUtils.HOST_KEY, getHostName(),
        JdbcUtils.USERNAME_KEY, getUserName(),
        JdbcUtils.PASSWORD_KEY, getPassword(),
        JdbcUtils.SCHEMA_KEY, getSchemaName(),
        JdbcUtils.JDBC_URL_PARAMS_KEY, extraParam));
  }

  @Test
  void testJdbcUrlAndConfigNoExtraParams() {
    final JsonNode jdbcConfig = destination.toJdbcConfig(buildConfigNoJdbcParameters());
    assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
    assertEquals("username", jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText());
    assertEquals("db", jdbcConfig.get(JdbcUtils.SCHEMA_KEY).asText());
    assertEquals("verysecure", jdbcConfig.get(JdbcUtils.PASSWORD_KEY).asText());
  }

  @Test
  void testJdbcUrlEmptyExtraParams() {
    final JsonNode jdbcConfig = destination.toJdbcConfig(buildConfigWithExtraJdbcParameters(""));
    assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
    assertEquals("username", jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText());
    assertEquals("db", jdbcConfig.get(JdbcUtils.SCHEMA_KEY).asText());
    assertEquals("", jdbcConfig.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText());
  }

  @Test
  void testJdbcUrlExtraParams() {

    final JsonNode jdbcConfig = destination.toJdbcConfig(buildConfigWithExtraJdbcParameters(EXTRA_JDBC_PARAMS));
    assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
    assertEquals("username", jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText());
    assertEquals("db", jdbcConfig.get(JdbcUtils.SCHEMA_KEY).asText());
    assertEquals(EXTRA_JDBC_PARAMS, jdbcConfig.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText());
  }

  @Test
  void testDefaultSchemaName() {
    final JsonNode jdbcConfig = destination.toJdbcConfig(buildConfigDefaultSchema());
    assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
    assertEquals(TeradataConstants.DEFAULT_SCHEMA_NAME, jdbcConfig.get(JdbcUtils.SCHEMA_KEY).asText());
  }

  @Test
  void testSSLDisable() {
    final JsonNode jdbcConfig = createConfig(false);
    final Map<String, String> properties = destination.getDefaultConnectionProperties(jdbcConfig);
    assertNull(properties.get(TeradataConstants.PARAM_SSLMODE));
  }

  @Test
  void testSSLDefaultMode() {
    final JsonNode jdbcConfig = createConfig(true);
    final Map<String, String> properties = destination.getDefaultConnectionProperties(jdbcConfig);
    assertEquals(TeradataConstants.REQUIRE, properties.get(TeradataConstants.PARAM_SSLMODE).toString());
  }

  @Test
  void testSSLAllowMode() {
    final JsonNode jdbcConfig = createConfig(TeradataConstants.ALLOW);
    final Map<String, String> properties = destination.getDefaultConnectionProperties(jdbcConfig);
    assertEquals(TeradataConstants.ALLOW, properties.get(TeradataConstants.PARAM_SSLMODE).toString());
  }

  @Test
  void testSSLVerfifyCAMode() {
    final JsonNode jdbcConfig = createConfig(TeradataConstants.VERIFY_CA);
    final Map<String, String> properties = destination.getDefaultConnectionProperties(jdbcConfig);
    assertEquals(TeradataConstants.VERIFY_CA, properties.get(TeradataConstants.PARAM_SSLMODE).toString());
    assertNotNull(properties.get(TeradataConstants.PARAM_SSLCA).toString());
  }

  @Test
  void testSSLVerfifyFullMode() {
    final JsonNode jdbcConfig = createConfig(TeradataConstants.VERIFY_FULL);
    final Map<String, String> properties = destination.getDefaultConnectionProperties(jdbcConfig);
    assertEquals(TeradataConstants.VERIFY_FULL, properties.get(TeradataConstants.PARAM_SSLMODE).toString());
    assertNotNull(properties.get(TeradataConstants.PARAM_SSLCA).toString());
  }

}
