/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql;

import static java.lang.System.getProperty;
import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.db.jdbc.JdbcUtils;
import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.shaded.com.google.common.collect.ImmutableMap;

public class MSSQLDestinationTest {

  private Map<String, String> existingProperties;

  private JsonNode createConfig(final String sslMethod) {
    return createConfig(sslMethod, new HashMap<>());
  }

  private JsonNode createConfig(final String sslMethod, final Map<String, String> additionalConfigs) {
    return Jsons.jsonNode(MoreMaps.merge(baseParameters(sslMethod), additionalConfigs));
  }

  private Map<String, String> baseParameters(final String sslMethod) {
    return ImmutableMap.<String, String>builder()
        .put("ssl_method", sslMethod)
        .put(JdbcUtils.HOST_KEY, "localhost")
        .put(JdbcUtils.PORT_KEY, "1773")
        .put(JdbcUtils.DATABASE_KEY, "db")
        .put(JdbcUtils.USERNAME_KEY, "username")
        .put(JdbcUtils.PASSWORD_KEY, "verysecure")
        .build();
  }

  @BeforeEach
  public void setUp() {
    existingProperties = new HashMap<>();
  }

  @AfterEach
  public void tearDown() {
    resetProperties();
  }

  @Test
  public void testNoSsl() {
    final MSSQLDestination destination = new MSSQLDestination();
    final JsonNode config = Jsons.jsonNode(ImmutableMap.of());
    final Map<String, String> properties = destination.getDefaultConnectionProperties(config);
    assertTrue(properties.isEmpty());
  }

  @Test
  public void testUnencrypted() {
    final MSSQLDestination destination = new MSSQLDestination();
    final JsonNode config = createConfig("unencrypted");
    final Map<String, String> properties = destination.getDefaultConnectionProperties(config);
    assertEquals(properties.get("encrypt"), "false");
  }

  @Test
  public void testEncryptedTrustServerCertificate() {
    final MSSQLDestination destination = new MSSQLDestination();
    final JsonNode config = createConfig("encrypted_trust_server_certificate");
    final Map<String, String> properties = destination.getDefaultConnectionProperties(config);
    assertEquals(properties.get("encrypt"), "true");
    assertEquals(properties.get("trustServerCertificate"), "true");
  }

  @Test
  public void testEncryptedVerifyCertificate() {
    final MSSQLDestination destination = new MSSQLDestination();
    final JsonNode config = createConfig("encrypted_verify_certificate");

    final Map<String, String> properties = destination.getDefaultConnectionProperties(config);
    assertEquals(properties.get("encrypt"), "true");

    final String trustStoreLocation = getProperty("java.home") + "/lib/security/cacerts";
    assertEquals(properties.get("trustStore"), trustStoreLocation);
    assertNull(properties.get("trustStorePassword"));
    assertNull(properties.get("hostNameInCertificate")); // TODO: add test with hostname in certificate
  }

  @Test
  public void testInvalidTrustStoreFile() {
    setProperty("javax.net.ssl.trustStore", "/NOT_A_TRUST_STORE");
    final MSSQLDestination destination = new MSSQLDestination();
    final JsonNode config = createConfig("encrypted_verify_certificate");

    assertThrows(RuntimeException.class, () -> destination.getDefaultConnectionProperties(config));
  }

  @Test
  public void testEncryptedVerifyCertificateWithEmptyTrustStorePassword() {
    setProperty("javax.net.ssl.trustStorePassword", "");
    final MSSQLDestination destination = new MSSQLDestination();
    final JsonNode config = createConfig("encrypted_verify_certificate", ImmutableMap.of("trustStorePassword", ""));

    final Map<String, String> properties = destination.getDefaultConnectionProperties(config);
    assertEquals(properties.get("encrypt"), "true");

    final String trustStoreLocation = getProperty("java.home") + "/lib/security/cacerts";
    assertEquals(properties.get("trustStore"), trustStoreLocation);
    assertNull(properties.get("trustStorePassword"));
    assertNull(properties.get("hostNameInCertificate"));
  }

  @Test
  public void testEncryptedVerifyCertificateWithNonEmptyTrustStorePassword() {
    final String TRUST_STORE_PASSWORD = "TRUSTSTOREPASSWORD";
    setProperty("javax.net.ssl.trustStorePassword", TRUST_STORE_PASSWORD);
    final MSSQLDestination destination = new MSSQLDestination();
    final JsonNode config = createConfig("encrypted_verify_certificate", ImmutableMap.of("trustStorePassword", TRUST_STORE_PASSWORD));

    final Map<String, String> properties = destination.getDefaultConnectionProperties(config);
    assertEquals(properties.get("encrypt"), "true");

    final String trustStoreLocation = getProperty("java.home") + "/lib/security/cacerts";
    assertEquals(properties.get("trustStore"), trustStoreLocation);
    assertEquals(properties.get("trustStorePassword"), TRUST_STORE_PASSWORD);
    assertNull(properties.get("hostNameInCertificate"));
  }

  @Test
  public void testEncryptedVerifyCertificateWithHostNameInCertificate() {
    final MSSQLDestination destination = new MSSQLDestination();
    final String HOSTNAME_IN_CERTIFICATE = "HOSTNAME_IN_CERTIFICATE";
    final JsonNode config = createConfig("encrypted_verify_certificate", ImmutableMap.of("hostNameInCertificate", HOSTNAME_IN_CERTIFICATE));

    final Map<String, String> properties = destination.getDefaultConnectionProperties(config);
    assertEquals(properties.get("encrypt"), "true");

    final String trustStoreLocation = getProperty("java.home") + "/lib/security/cacerts";
    assertEquals(properties.get("trustStore"), trustStoreLocation);
    assertNull(properties.get("trustStorePassword"));

    assertEquals(properties.get("hostNameInCertificate"), HOSTNAME_IN_CERTIFICATE);
  }

  private void setProperty(final String key, final String value) {
    existingProperties.put(key, System.getProperty(key));
    System.setProperty(key, value);
  }

  private void resetProperties() {
    existingProperties.forEach((k, v) -> resetProperty(k));
  }

  private void resetProperty(final String key) {
    final String value = existingProperties.get(key);
    if (value != null) {
      System.setProperty(key, value);
    } else {
      System.clearProperty(key);
    }
  }

  @Test
  void testNoExtraParams() {
    final JsonNode config = buildConfigNoJdbcParameters();
    final JsonNode jdbcConfig = new MSSQLDestination().toJdbcConfig(config);
    assertNull(jdbcConfig.get(JdbcUtils.JDBC_URL_PARAMS_KEY));
  }

  @Test
  void testEmptyExtraParams() {
    final String extraParam = "";
    final JsonNode config = buildConfigWithExtraJdbcParameters(extraParam);
    final JsonNode jdbcConfig = new MSSQLDestination().toJdbcConfig(config);
    assertNotNull(jdbcConfig.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText());
    assertEquals(extraParam, jdbcConfig.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText());
  }

  @Test
  void testExtraParams() {
    final String extraParam = "key1=value1&key2=value2&key3=value3";
    final JsonNode config = buildConfigWithExtraJdbcParameters(extraParam);
    final JsonNode jdbcConfig = new MSSQLDestination().toJdbcConfig(config);
    assertNotNull(jdbcConfig.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText());
    assertEquals(extraParam, jdbcConfig.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText());

  }

  private JsonNode buildConfigNoJdbcParameters() {
    return Jsons.jsonNode(com.google.common.collect.ImmutableMap.of(
        "ssl_method", "ssl_method",
        JdbcUtils.HOST_KEY, "localhost",
        JdbcUtils.PORT_KEY, "1773",
        JdbcUtils.DATABASE_KEY, "db",
        JdbcUtils.USERNAME_KEY, "username",
        JdbcUtils.PASSWORD_KEY, "verysecure"));
  }

  private JsonNode buildConfigWithExtraJdbcParameters(final String extraParam) {

    return Jsons.jsonNode(com.google.common.collect.ImmutableMap.of(
        "ssl_method", "ssl_method",
        JdbcUtils.HOST_KEY, "localhost",
        JdbcUtils.PORT_KEY, "1773",
        JdbcUtils.DATABASE_KEY, "db",
        JdbcUtils.USERNAME_KEY, "username",
        JdbcUtils.PASSWORD_KEY, "verysecure",
        JdbcUtils.JDBC_URL_PARAMS_KEY, extraParam));
  }

}
