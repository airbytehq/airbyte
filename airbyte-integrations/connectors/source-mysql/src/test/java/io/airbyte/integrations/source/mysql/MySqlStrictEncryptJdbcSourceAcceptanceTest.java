/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.MySqlUtils;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.base.ssh.SshBastionContainer;
import io.airbyte.cdk.integrations.base.ssh.SshHelpers;
import io.airbyte.cdk.integrations.base.ssh.SshTunnel;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MySQLContainer;
import org.testcontainers.containers.Network;

class MySqlStrictEncryptJdbcSourceAcceptanceTest extends MySqlSslJdbcSourceAcceptanceTest {

  private static final SshBastionContainer bastion = new SshBastionContainer();
  private static final Network network = Network.newNetwork();

  @BeforeEach
  @Override
  public void setup() throws Exception {
    environmentVariables.set(EnvVariableFeatureFlags.DEPLOYMENT_MODE, "CLOUD");
    super.setup();
  }

  @Override
  public Source getSource() {
    return MySqlSource.sshWrappedSource();
  }

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = source.spec();
    final ConnectorSpecification expected =
        SshHelpers.injectSshIntoSpec(Jsons.deserialize(MoreResources.readResource("expected_cloud_spec.json"), ConnectorSpecification.class));
    assertEquals(expected, actual);
  }

  @Test
  void testStrictSSLUnsecuredNoTunnel() throws Exception {
    final var sslMode = ImmutableMap.builder()
        .put(JdbcUtils.MODE_KEY, "preferred")
        .build();

    final var tunnelMode = ImmutableMap.builder()
        .put("tunnel_method", "NO_TUNNEL")
        .build();
    ((ObjectNode) config)
        .put(JdbcUtils.SSL_KEY, true)
        .putIfAbsent(JdbcUtils.SSL_MODE_KEY, Jsons.jsonNode(sslMode));
    ((ObjectNode) config).putIfAbsent("tunnel_method", Jsons.jsonNode(tunnelMode));

    final AirbyteConnectionStatus actual = source.check(config);
    assertEquals(Status.FAILED, actual.getStatus());
    assertTrue(actual.getMessage().contains("Unsecured connection not allowed"));
  }

  @Test
  void testStrictSSLSecuredNoTunnel() throws Exception {
    final String PASSWORD = "Passw0rd";
    final var certs = MySqlUtils.getCertificate(container, true);
    final var sslMode = ImmutableMap.builder()
        .put(JdbcUtils.MODE_KEY, "verify_ca")
        .put("ca_certificate", certs.getCaCertificate())
        .put("client_certificate", certs.getClientCertificate())
        .put("client_key", certs.getClientKey())
        .put("client_key_password", PASSWORD)
        .build();

    final var tunnelMode = ImmutableMap.builder()
        .put("tunnel_method", "NO_TUNNEL")
        .build();
    ((ObjectNode) config).put(JdbcUtils.PASSWORD_KEY, "fake")
        .put(JdbcUtils.SSL_KEY, true)
        .putIfAbsent(JdbcUtils.SSL_MODE_KEY, Jsons.jsonNode(sslMode));
    ((ObjectNode) config).putIfAbsent("tunnel_method", Jsons.jsonNode(tunnelMode));

    final AirbyteConnectionStatus actual = source.check(config);
    assertEquals(Status.FAILED, actual.getStatus());
    assertFalse(actual.getMessage().contains("Unsecured connection not allowed"));
  }

  @Test
  void testStrictSSLSecuredWithTunnel() throws Exception {
    final String PASSWORD = "Passw0rd";
    final var certs = MySqlUtils.getCertificate(container, true);
    final var sslMode = ImmutableMap.builder()
        .put(JdbcUtils.MODE_KEY, "verify_ca")
        .put("ca_certificate", certs.getCaCertificate())
        .put("client_certificate", certs.getClientCertificate())
        .put("client_key", certs.getClientKey())
        .put("client_key_password", PASSWORD)
        .build();

    final var tunnelMode = ImmutableMap.builder()
        .put("tunnel_method", "SSH_KEY_AUTH")
        .build();
    ((ObjectNode) config).put(JdbcUtils.PASSWORD_KEY, "fake")
        .put(JdbcUtils.SSL_KEY, true)
        .putIfAbsent(JdbcUtils.SSL_MODE_KEY, Jsons.jsonNode(sslMode));
    ((ObjectNode) config).putIfAbsent("tunnel_method", Jsons.jsonNode(tunnelMode));

    final AirbyteConnectionStatus actual = source.check(config);
    assertEquals(Status.FAILED, actual.getStatus());
    assertTrue(actual.getMessage().contains("Could not connect with provided SSH configuration."));
  }

  @Test
  void testStrictSSLUnsecuredWithTunnel() throws Exception {
    final String PASSWORD = "Passw0rd";
    final var certs = MySqlUtils.getCertificate(container, true);
    final var sslMode = ImmutableMap.builder()
        .put(JdbcUtils.MODE_KEY, "preferred")
        .build();

    final var tunnelMode = ImmutableMap.builder()
        .put("tunnel_method", "SSH_KEY_AUTH")
        .build();
    ((ObjectNode) config).put(JdbcUtils.PASSWORD_KEY, "fake")
        .put(JdbcUtils.SSL_KEY, true)
        .putIfAbsent(JdbcUtils.SSL_MODE_KEY, Jsons.jsonNode(sslMode));
    ((ObjectNode) config).putIfAbsent("tunnel_method", Jsons.jsonNode(tunnelMode));

    final AirbyteConnectionStatus actual = source.check(config);
    assertEquals(Status.FAILED, actual.getStatus());
    assertTrue(actual.getMessage().contains("Could not connect with provided SSH configuration."));
  }

  @Test
  void testCheckWithSSlModeDisabled() throws Exception {
    try (final MySQLContainer<?> db = new MySQLContainer<>("mysql:8.0").withNetwork(network)) {
      bastion.initAndStartBastion(network);
      db.start();
      final JsonNode configWithSSLModeDisabled = bastion.getTunnelConfig(SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH, ImmutableMap.builder()
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
          .put(JdbcUtils.SSL_MODE_KEY, Map.of(JdbcUtils.MODE_KEY, "disable")), false);

      final AirbyteConnectionStatus actual = source.check(configWithSSLModeDisabled);
      assertEquals(Status.SUCCEEDED, actual.getStatus());
    } finally {
      bastion.stopAndClose();
    }
  }

}
