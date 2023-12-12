/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.base.adaptive.AdaptiveSourceRunner;
import io.airbyte.cdk.integrations.base.ssh.SshBastionContainer;
import io.airbyte.cdk.integrations.base.ssh.SshHelpers;
import io.airbyte.cdk.integrations.base.ssh.SshTunnel;
import io.airbyte.cdk.testutils.PostgresTestDatabase;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlagsWrapper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.Network;

public class CloudDeploymentPostgresSourceTest {

  static PostgresTestDatabase DB_NO_SSL_WITH_NETWORK, DB_WITH_SSL, DB_WITH_SSL_WITH_NETWORK;
  static SshBastionContainer BASTION_NO_SSL, BASTION_WITH_SSL;
  static Network NETWORK_NO_SSL, NETWORK_WITH_SSL;

  @BeforeAll
  static void setupContainers() {
    DB_NO_SSL_WITH_NETWORK = PostgresTestDatabase.make("postgres:16-bullseye", "withNetwork");
    NETWORK_NO_SSL = DB_NO_SSL_WITH_NETWORK.container.getNetwork();
    BASTION_NO_SSL = new SshBastionContainer();
    BASTION_NO_SSL.initAndStartBastion(NETWORK_NO_SSL);

    DB_WITH_SSL = PostgresTestDatabase.make("marcosmarxm/postgres-ssl:dev", "withSSL");

    DB_WITH_SSL_WITH_NETWORK = PostgresTestDatabase.make("marcosmarxm/postgres-ssl:dev", "withSSL", "withNetwork");
    NETWORK_WITH_SSL = DB_WITH_SSL_WITH_NETWORK.container.getNetwork();
    BASTION_WITH_SSL = new SshBastionContainer();
    BASTION_WITH_SSL.initAndStartBastion(NETWORK_WITH_SSL);
  }

  @AfterAll
  static void tearDownContainers() {
    BASTION_NO_SSL.stopAndClose();
    BASTION_WITH_SSL.stopAndClose();
    DB_NO_SSL_WITH_NETWORK.close();
    DB_WITH_SSL_WITH_NETWORK.close();
    DB_WITH_SSL.close();
  }

  private static final List<String> NON_STRICT_SSL_MODES = List.of("disable", "allow", "prefer");
  private static final String SSL_MODE_REQUIRE = "require";

  private Source source() {
    PostgresSource source = new PostgresSource();
    source.setFeatureFlags(
        FeatureFlagsWrapper.overridingDeploymentMode(
            FeatureFlagsWrapper.overridingUseStreamCapableState(
                new EnvVariableFeatureFlags(),
                true),
            AdaptiveSourceRunner.CLOUD_MODE));
    return PostgresSource.sshWrappedSource(source);
  }

  @Test
  void testSSlModesDisableAllowPreferWithTunnelIfServerDoesNotSupportSSL() throws Exception {
    for (final String sslmode : NON_STRICT_SSL_MODES) {
      final AirbyteConnectionStatus connectionStatus = checkWithTunnel(DB_NO_SSL_WITH_NETWORK, BASTION_NO_SSL, sslmode);
      assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, connectionStatus.getStatus());
    }
  }

  @Test
  void testSSlModesDisableAllowPreferWithTunnelIfServerSupportSSL() throws Exception {
    for (final String sslmode : NON_STRICT_SSL_MODES) {
      final AirbyteConnectionStatus connectionStatus = checkWithTunnel(DB_WITH_SSL_WITH_NETWORK, BASTION_WITH_SSL, sslmode);
      assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, connectionStatus.getStatus());
    }
  }

  @Test
  void testSSlModesDisableAllowPreferWithFailedTunnelIfServerSupportSSL() throws Exception {
    for (final String sslmode : NON_STRICT_SSL_MODES) {
      final AirbyteConnectionStatus connectionStatus = checkWithTunnel(DB_WITH_SSL, BASTION_WITH_SSL, sslmode);
      assertEquals(AirbyteConnectionStatus.Status.FAILED, connectionStatus.getStatus());
      final String msg = connectionStatus.getMessage();
      assertTrue(msg.matches(".*Connection is not available.*|.*The connection attempt failed.*"), msg);
    }
  }

  @Test
  void testSSlRequiredWithTunnelIfServerDoesNotSupportSSL() throws Exception {
    final AirbyteConnectionStatus connectionStatus = checkWithTunnel(DB_NO_SSL_WITH_NETWORK, BASTION_NO_SSL, SSL_MODE_REQUIRE);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, connectionStatus.getStatus());
    assertEquals("State code: 08004; Message: The server does not support SSL.", connectionStatus.getMessage());
  }

  @Test
  void testSSlRequiredNoTunnelIfServerSupportSSL() throws Exception {
    final ImmutableMap<Object, Object> configBuilderWithSSLMode = getDatabaseConfigBuilderWithSSLMode(
        DB_WITH_SSL, SSL_MODE_REQUIRE, false).build();
    final JsonNode config = Jsons.jsonNode(configBuilderWithSSLMode);
    addNoTunnel((ObjectNode) config);
    final AirbyteConnectionStatus connectionStatus = source().check(config);
    assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, connectionStatus.getStatus());
  }

  @Test
  void testStrictSSLSecuredWithTunnel() throws Exception {
    final AirbyteConnectionStatus connectionStatus = checkWithTunnel(DB_WITH_SSL_WITH_NETWORK, BASTION_WITH_SSL, SSL_MODE_REQUIRE);
    assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, connectionStatus.getStatus());
  }

  private ImmutableMap.Builder<Object, Object> getDatabaseConfigBuilderWithSSLMode(final PostgresTestDatabase db,
                                                                                   final String sslMode,
                                                                                   final boolean innerAddress) {
    final var containerAddress = innerAddress
        ? SshHelpers.getInnerContainerAddress(db.container)
        : SshHelpers.getOuterContainerAddress(db.container);
    return ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, Objects.requireNonNull(containerAddress.left))
        .put(JdbcUtils.PORT_KEY, containerAddress.right)
        .put(JdbcUtils.DATABASE_KEY, db.dbName)
        .put(JdbcUtils.SCHEMAS_KEY, List.of("public"))
        .put(JdbcUtils.USERNAME_KEY, db.userName)
        .put(JdbcUtils.PASSWORD_KEY, db.password)
        .put(JdbcUtils.SSL_MODE_KEY, Map.of(JdbcUtils.MODE_KEY, sslMode));
  }

  private JsonNode getMockedSSLConfig(final String sslMode) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, "test_host")
        .put(JdbcUtils.PORT_KEY, 777)
        .put(JdbcUtils.DATABASE_KEY, "test_db")
        .put(JdbcUtils.USERNAME_KEY, "test_user")
        .put(JdbcUtils.PASSWORD_KEY, "test_password")
        .put(JdbcUtils.SSL_KEY, true)
        .put(JdbcUtils.SSL_MODE_KEY, Map.of(JdbcUtils.MODE_KEY, sslMode))
        .build());
  }

  @Test
  void testSslModesUnsecuredNoTunnel() throws Exception {
    for (final String sslMode : NON_STRICT_SSL_MODES) {
      final JsonNode config = getMockedSSLConfig(sslMode);
      addNoTunnel((ObjectNode) config);

      final AirbyteConnectionStatus connectionStatus = source().check(config);
      assertEquals(AirbyteConnectionStatus.Status.FAILED, connectionStatus.getStatus());
      assertTrue(connectionStatus.getMessage().contains("Unsecured connection not allowed"), connectionStatus.getMessage());
    }
  }

  private AirbyteConnectionStatus checkWithTunnel(final PostgresTestDatabase db, SshBastionContainer bastion, final String sslmode) throws Exception {
    final var configBuilderWithSSLMode = getDatabaseConfigBuilderWithSSLMode(db, sslmode, true);
    final JsonNode configWithSSLModeDisable =
        bastion.getTunnelConfig(SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH, configBuilderWithSSLMode, false);
    ((ObjectNode) configWithSSLModeDisable).put(JdbcUtils.JDBC_URL_PARAMS_KEY, "connectTimeout=1");
    return source().check(configWithSSLModeDisable);
  }

  private static void addNoTunnel(final ObjectNode config) {
    config.putIfAbsent("tunnel_method", Jsons.jsonNode(ImmutableMap.builder()
        .put("tunnel_method", "NO_TUNNEL")
        .build()));
  }

}
