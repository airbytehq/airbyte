/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.ssh.SshBastionContainer;
import io.airbyte.integrations.base.ssh.SshTunnel;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.Network;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.DockerImageName;

public class PostgresSourceStrictEncryptTest {

  private final PostgresSourceStrictEncrypt source = new PostgresSourceStrictEncrypt();
  private final PostgreSQLContainer<?> postgreSQLContainerNoSSL = new PostgreSQLContainer<>("postgres:13-alpine");
  private final PostgreSQLContainer<?> postgreSQLContainerWithSSL =
      new PostgreSQLContainer<>(DockerImageName.parse("marcosmarxm/postgres-ssl:dev").asCompatibleSubstituteFor("postgres"))
          .withCommand("postgres -c ssl=on -c ssl_cert_file=/var/lib/postgresql/server.crt -c ssl_key_file=/var/lib/postgresql/server.key");
  private static final List<String> NON_STRICT_SSL_MODES = List.of("disable", "allow", "prefer");
  private static final String SSL_MODE_REQUIRE = "require";

  private static final SshBastionContainer bastion = new SshBastionContainer();
  private static final Network network = Network.newNetwork();

  @Test
  void testSSlModesDisableAllowPreferWithTunnelIfServerDoesNotSupportSSL() throws Exception {

    try (PostgreSQLContainer<?> db = postgreSQLContainerNoSSL.withNetwork(network)) {
      bastion.initAndStartBastion(network);
      db.start();

      for (String sslmode : NON_STRICT_SSL_MODES) {
        final AirbyteConnectionStatus connectionStatus = checkWithTunnel(db, sslmode);
        assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, connectionStatus.getStatus());
      }

    } finally {
      bastion.stopAndClose();
    }
  }

  @Test
  void testSSlModesDisableAllowPreferWithTunnelIfServerSupportSSL() throws Exception {
    try (PostgreSQLContainer<?> db = postgreSQLContainerWithSSL.withNetwork(network)) {

      bastion.initAndStartBastion(network);
      db.start();
      for (String sslmode : NON_STRICT_SSL_MODES) {

        final AirbyteConnectionStatus connectionStatus = checkWithTunnel(db, sslmode);
        assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, connectionStatus.getStatus());
      }
    } finally {
      bastion.stopAndClose();
    }
  }

  @Test
  void testSSlModesDisableAllowPreferWithFailedTunnelIfServerSupportSSL() throws Exception {
    try (PostgreSQLContainer<?> db = postgreSQLContainerWithSSL) {

      bastion.initAndStartBastion(network);
      db.start();
      for (String sslmode : NON_STRICT_SSL_MODES) {

        final AirbyteConnectionStatus connectionStatus = checkWithTunnel(db, sslmode);
        assertEquals(AirbyteConnectionStatus.Status.FAILED, connectionStatus.getStatus());
        assertTrue(connectionStatus.getMessage().contains("Connection is not available"));

      }
    } finally {
      bastion.stopAndClose();
    }
  }

  @Test
  void testSSlRequiredWithTunnelIfServerDoesNotSupportSSL() throws Exception {

    try (PostgreSQLContainer<?> db = postgreSQLContainerNoSSL.withNetwork(network)) {
      bastion.initAndStartBastion(network);
      db.start();
      final AirbyteConnectionStatus connectionStatus = checkWithTunnel(db, SSL_MODE_REQUIRE);
      assertEquals(AirbyteConnectionStatus.Status.FAILED, connectionStatus.getStatus());
      assertEquals("State code: 08004; Message: The server does not support SSL.", connectionStatus.getMessage());

    } finally {
      bastion.stopAndClose();
    }
  }

  @Test
  void testSSlRequiredNoTunnelIfServerSupportSSL() throws Exception {

    try (PostgreSQLContainer<?> db = postgreSQLContainerWithSSL) {
      db.start();

      final ImmutableMap<Object, Object> configBuilderWithSSLMode = getDatabaseConfigBuilderWithSSLMode(db, SSL_MODE_REQUIRE).build();
      final JsonNode config = Jsons.jsonNode(configBuilderWithSSLMode);
      addNoTunnel((ObjectNode) config);
      final AirbyteConnectionStatus connectionStatus = source.check(config);
      assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, connectionStatus.getStatus());
    }
  }

  @Test
  void testStrictSSLSecuredWithTunnel() throws Exception {

    try (PostgreSQLContainer<?> db = postgreSQLContainerWithSSL.withNetwork(network)) {

      bastion.initAndStartBastion(network);
      db.start();

      final AirbyteConnectionStatus connectionStatus = checkWithTunnel(db, SSL_MODE_REQUIRE);
      assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, connectionStatus.getStatus());
    } finally {
      bastion.stopAndClose();
    }
  }

  private ImmutableMap.Builder<Object, Object> getDatabaseConfigBuilderWithSSLMode(PostgreSQLContainer<?> db, String sslMode) {
    return ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, Objects.requireNonNull(db.getContainerInfo()
            .getNetworkSettings()
            .getNetworks()
            .entrySet().stream()
            .findFirst()
            .get().getValue().getIpAddress()))
        .put(JdbcUtils.PORT_KEY, db.getExposedPorts().get(0))
        .put(JdbcUtils.DATABASE_KEY, db.getDatabaseName())
        .put(JdbcUtils.SCHEMAS_KEY, List.of("public"))
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
        .put(JdbcUtils.SSL_MODE_KEY, Map.of(JdbcUtils.MODE_KEY, sslMode));
  }

  private JsonNode getMockedSSLConfig(String sslMode) {
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
    for (String sslMode : NON_STRICT_SSL_MODES) {
      final JsonNode config = getMockedSSLConfig(sslMode);
      addNoTunnel((ObjectNode) config);

      final AirbyteConnectionStatus connectionStatus = source.check(config);
      assertEquals(AirbyteConnectionStatus.Status.FAILED, connectionStatus.getStatus());
      assertTrue(connectionStatus.getMessage().contains("Unsecured connection not allowed"));
    }
  }

  private AirbyteConnectionStatus checkWithTunnel(PostgreSQLContainer<?> db, String sslmode) throws Exception {
    final ImmutableMap.Builder<Object, Object> configBuilderWithSSLMode = getDatabaseConfigBuilderWithSSLMode(db, sslmode);
    final JsonNode configWithSSLModeDisable = bastion.getTunnelConfig(SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH, configBuilderWithSSLMode);
    return source.check(configWithSSLModeDisable);
  }

  private static void addNoTunnel(ObjectNode config) {
    config.putIfAbsent("tunnel_method", Jsons.jsonNode(ImmutableMap.builder()
        .put("tunnel_method", "NO_TUNNEL")
        .build()));
  }

}
