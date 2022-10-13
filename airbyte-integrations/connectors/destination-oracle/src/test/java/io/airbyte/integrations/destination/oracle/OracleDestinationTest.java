/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oracle;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.destination.oracle.OracleDestination.Protocol;
import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.shaded.com.google.common.collect.ImmutableMap;

public class OracleDestinationTest {

  private OracleDestination destination;

  private JsonNode createConfig() {
    return createConfig(new HashMap<>());
  }

  private JsonNode createConfig(final Map<String, Object> additionalConfigs) {
    return Jsons.jsonNode(MoreMaps.merge(baseParameters(), additionalConfigs));
  }

  private Map<String, Object> baseParameters() {
    return ImmutableMap.<String, Object>builder()
        .put(JdbcUtils.HOST_KEY, "localhost")
        .put(JdbcUtils.PORT_KEY, "1773")
        .put(JdbcUtils.DATABASE_KEY, "db")
        .put(JdbcUtils.USERNAME_KEY, "username")
        .put(JdbcUtils.PASSWORD_KEY, "verysecure")
        .build();
  }

  @BeforeEach
  void setUp() {
    destination = new OracleDestination();
  }

  @Test
  void testNoEncryption() {
    final Map<String, String> properties = destination.getDefaultConnectionProperties(createConfig());
    assertNull(properties.get(JdbcUtils.ENCRYPTION_KEY));
    assertNull(properties.get("javax.net.ssl.trustStorePassword"));

    final Protocol protocol = destination.obtainConnectionProtocol(createConfig());
    assertEquals(Protocol.TCP, protocol);
  }

  @Test
  void testUnencrypted() {
    final Map<String, Object> encryptionNode = ImmutableMap.of(OracleDestination.ENCRYPTION_METHOD_KEY, "unencrypted");
    final JsonNode inputConfig = createConfig(ImmutableMap.of(JdbcUtils.ENCRYPTION_KEY, encryptionNode));
    final Map<String, String> properties = destination.getDefaultConnectionProperties(inputConfig);
    assertNull(properties.get(JdbcUtils.ENCRYPTION_KEY));
    assertNull(properties.get("javax.net.ssl.trustStorePassword"));

    final Protocol protocol = destination.obtainConnectionProtocol(inputConfig);
    assertEquals(Protocol.TCP, protocol);
  }

  @Test
  void testClientNne() {
    final String algorithm = "AES256";
    final Map<String, Object> encryptionNode = ImmutableMap.of(
        OracleDestination.ENCRYPTION_METHOD_KEY, "client_nne",
        "encryption_algorithm", algorithm);
    final JsonNode inputConfig = createConfig(ImmutableMap.of(JdbcUtils.ENCRYPTION_KEY, encryptionNode));
    final Map<String, String> properties = destination.getDefaultConnectionProperties(inputConfig);
    assertEquals(properties.get("oracle.net.encryption_client"), "REQUIRED");
    assertEquals(properties.get("oracle.net.encryption_types_client"), String.format("( %s )", algorithm));
    assertNull(properties.get("javax.net.ssl.trustStorePassword"));

    final Protocol protocol = destination.obtainConnectionProtocol(inputConfig);
    assertEquals(Protocol.TCP, protocol);
  }

  @Test
  void testEncryptedVerifyCertificate() {
    final Map<String, Object> encryptionNode = ImmutableMap.of(
        OracleDestination.ENCRYPTION_METHOD_KEY, "encrypted_verify_certificate", "ssl_certificate", "certificate");
    final JsonNode inputConfig = createConfig(ImmutableMap.of(JdbcUtils.ENCRYPTION_KEY, encryptionNode));
    final Map<String, String> properties = destination.getDefaultConnectionProperties(inputConfig);
    assertEquals(properties.get("javax.net.ssl.trustStore"), OracleDestination.KEY_STORE_FILE_PATH);
    assertEquals(properties.get("javax.net.ssl.trustStoreType"), "JKS");
    assertNotNull(properties.get("javax.net.ssl.trustStorePassword"));

    final Protocol protocol = destination.obtainConnectionProtocol(inputConfig);
    assertEquals(Protocol.TCPS, protocol);
  }

  @Test
  void testInvalidEncryptionMethod() {
    final Map<String, Object> encryptionNode = ImmutableMap.of(
        OracleDestination.ENCRYPTION_METHOD_KEY, "invalid_encryption_method");
    final JsonNode inputConfig = createConfig(ImmutableMap.of(JdbcUtils.ENCRYPTION_KEY, encryptionNode));
    assertThrows(RuntimeException.class, () -> destination.getDefaultConnectionProperties(inputConfig));
    assertThrows(RuntimeException.class, () -> destination.obtainConnectionProtocol(inputConfig));
  }

  @Test
  void testEmptyExtraParams() {
    final String extraParam = "";
    JsonNode config = buildConfigWithExtraJdbcParameters(extraParam);
    final JsonNode jdbcConfig = new OracleDestination().toJdbcConfig(config);
    assertNotNull(jdbcConfig.get(OracleDestination.JDBC_URL_PARAMS_KEY).asText());
    assertEquals(extraParam, jdbcConfig.get(OracleDestination.JDBC_URL_PARAMS_KEY).asText());
  }

  @Test
  void testExtraParams() {
    final String extraParam = "key1=value1&key2=value2&key3=value3";
    JsonNode config = buildConfigWithExtraJdbcParameters(extraParam);
    final JsonNode jdbcConfig = new OracleDestination().toJdbcConfig(config);
    assertNotNull(jdbcConfig.get(OracleDestination.JDBC_URL_PARAMS_KEY).asText());
    assertEquals(extraParam, jdbcConfig.get(OracleDestination.JDBC_URL_PARAMS_KEY).asText());

  }

  private JsonNode buildConfigWithExtraJdbcParameters(String extraParam) {

    return Jsons.jsonNode(com.google.common.collect.ImmutableMap.of(
        "host", "localhost",
        "port", 1773,
        "sid", "ORCL",
        "database", "db",
        "username", "username",
        "password", "verysecure",
        "jdbc_url_params", extraParam));
  }

}
