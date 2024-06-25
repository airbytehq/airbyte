/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.base.ssh.SshBastionContainer;
import io.airbyte.cdk.integrations.base.ssh.SshHelpers;
import io.airbyte.cdk.integrations.base.ssh.SshTunnel;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlagsWrapper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

public class CloudDeploymentMySqlSslTest {

  private MySQLTestDatabase createTestDatabase(String... containerFactoryMethods) {
    final var container = new MySQLContainerFactory().shared("mysql:8.0", containerFactoryMethods);
    return new MySQLTestDatabase(container)
        .withConnectionProperty("useSSL", "true")
        .withConnectionProperty("requireSSL", "true")
        .initialized();
  }

  private Source source() {
    final var source = new MySqlSource();
    source.setFeatureFlags(FeatureFlagsWrapper.overridingDeploymentMode(new EnvVariableFeatureFlags(), "CLOUD"));
    return MySqlSource.sshWrappedSource(source);
  }

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = source().spec();
    final ConnectorSpecification expected =
        SshHelpers.injectSshIntoSpec(Jsons.deserialize(MoreResources.readResource("expected_cloud_spec.json"), ConnectorSpecification.class));
    assertEquals(expected, actual);
  }

  @Test
  void testStrictSSLUnsecuredNoTunnel() throws Exception {
    try (final var testdb = createTestDatabase()) {
      final var config = testdb.configBuilder()
          .withHostAndPort()
          .withDatabase()
          .with(JdbcUtils.USERNAME_KEY, testdb.getUserName())
          .with(JdbcUtils.PASSWORD_KEY, "fake")
          .with("tunnel_method", ImmutableMap.builder().put("tunnel_method", "NO_TUNNEL").build())
          .withSsl(ImmutableMap.builder()
              .put(JdbcUtils.MODE_KEY, "preferred")
              .build())
          .build();
      final AirbyteConnectionStatus actual = source().check(config);
      assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
      assertTrue(actual.getMessage().contains("Unsecured connection not allowed"), actual.getMessage());
    }
  }

  @Test
  void testStrictSSLSecuredNoTunnel() throws Exception {
    final String PASSWORD = "Passw0rd";
    try (final var testdb = createTestDatabase("withRootAndServerCertificates", "withClientCertificate")) {
      final var config = testdb.testConfigBuilder()
          .with("tunnel_method", ImmutableMap.builder().put("tunnel_method", "NO_TUNNEL").build())
          .withSsl(ImmutableMap.builder()
              .put(JdbcUtils.MODE_KEY, "verify_ca")
              .put("ca_certificate", testdb.getCertificates().caCertificate())
              .put("client_certificate", testdb.getCertificates().clientCertificate())
              .put("client_key", testdb.getCertificates().clientKey())
              .put("client_key_password", PASSWORD)
              .build())
          .build();
      final AirbyteConnectionStatus actual = source().check(config);
      assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
      assertTrue(actual.getMessage().contains("Failed to create keystore for Client certificate"), actual.getMessage());
    }
  }

  @Test
  void testStrictSSLSecuredWithTunnel() throws Exception {
    final String PASSWORD = "Passw0rd";
    try (final var testdb = createTestDatabase("withRootAndServerCertificates", "withClientCertificate")) {
      final var config = testdb.configBuilder()
          .withHostAndPort()
          .withDatabase()
          .with(JdbcUtils.USERNAME_KEY, testdb.getUserName())
          .with(JdbcUtils.PASSWORD_KEY, "fake")
          .withSsl(ImmutableMap.builder()
              .put(JdbcUtils.MODE_KEY, "verify_ca")
              .put("ca_certificate", testdb.getCertificates().caCertificate())
              .put("client_certificate", testdb.getCertificates().clientCertificate())
              .put("client_key", testdb.getCertificates().clientKey())
              .put("client_key_password", PASSWORD)
              .build())
          .with("tunnel_method", ImmutableMap.builder().put("tunnel_method", "SSH_KEY_AUTH").build())
          .build();
      final AirbyteConnectionStatus actual = source().check(config);
      assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
      assertTrue(actual.getMessage().contains("Could not connect with provided SSH configuration."), actual.getMessage());
    }
  }

  @Test
  void testStrictSSLUnsecuredWithTunnel() throws Exception {
    try (final var testdb = createTestDatabase()) {
      final var config = testdb.configBuilder()
          .withHostAndPort()
          .withDatabase()
          .with(JdbcUtils.USERNAME_KEY, testdb.getUserName())
          .with(JdbcUtils.PASSWORD_KEY, "fake")
          .withSsl(ImmutableMap.builder()
              .put(JdbcUtils.MODE_KEY, "preferred")
              .build())
          .with("tunnel_method", ImmutableMap.builder().put("tunnel_method", "SSH_KEY_AUTH").build())
          .build();
      final AirbyteConnectionStatus actual = source().check(config);
      assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
      assertTrue(actual.getMessage().contains("Could not connect with provided SSH configuration."), actual.getMessage());
    }
  }

  @Test
  @Timeout(value = 5,
           unit = TimeUnit.MINUTES)
  void testCheckWithSslModeDisabled() throws Exception {
    try (final var testdb = createTestDatabase("withNetwork")) {
      try (final SshBastionContainer bastion = new SshBastionContainer()) {
        bastion.initAndStartBastion(testdb.getContainer().getNetwork());
        final var config = testdb.integrationTestConfigBuilder()
            .with("tunnel_method", bastion.getTunnelMethod(SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH, false))
            .withoutSsl()
            .build();
        final AirbyteConnectionStatus actual = source().check(config);
        assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, actual.getStatus());
      }
    }
  }

}
