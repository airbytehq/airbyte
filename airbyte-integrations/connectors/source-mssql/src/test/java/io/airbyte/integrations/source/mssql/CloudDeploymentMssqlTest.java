/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.base.ssh.SshBastionContainer;
import io.airbyte.cdk.integrations.base.ssh.SshTunnel;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlagsWrapper;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.parallel.Execution;
import org.junit.jupiter.api.parallel.ExecutionMode;

@Execution(ExecutionMode.CONCURRENT)
public class CloudDeploymentMssqlTest {

  private MsSQLTestDatabase createTestDatabase(String... containerFactoryMethods) {
    final var container = new MsSQLContainerFactory().shared(
        "mcr.microsoft.com/mssql/server:2022-latest", containerFactoryMethods);
    final var testdb = new MsSQLTestDatabase(container);
    return testdb
        .withConnectionProperty("encrypt", "true")
        .withConnectionProperty("trustServerCertificate", "true")
        .withConnectionProperty("databaseName", testdb.getDatabaseName())
        .initialized();
  }

  private Source source() {
    final var source = new MssqlSource();
    source.setFeatureFlags(FeatureFlagsWrapper.overridingDeploymentMode(new EnvVariableFeatureFlags(), "CLOUD"));
    return MssqlSource.sshWrappedSource(source);
  }

  @Test
  void testStrictSSLUnsecuredNoTunnel() throws Exception {
    try (final var testdb = createTestDatabase()) {
      final var config = testdb.configBuilder()
          .withHostAndPort()
          .withDatabase()
          .with(JdbcUtils.USERNAME_KEY, testdb.getUserName())
          .with(JdbcUtils.PASSWORD_KEY, "fake")
          .withoutSsl()
          .with("tunnel_method", ImmutableMap.builder().put("tunnel_method", "NO_TUNNEL").build())
          .build();
      final AirbyteConnectionStatus actual = source().check(config);
      assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
      assertTrue(actual.getMessage().contains("Unsecured connection not allowed"), actual.getMessage());
    }
  }

  @Test
  void testStrictSSLSecuredNoTunnel() throws Exception {
    try (final var testdb = createTestDatabase()) {
      final var config = testdb.testConfigBuilder()
          .withEncrytedTrustServerCertificate()
          .with("tunnel_method", ImmutableMap.builder().put("tunnel_method", "NO_TUNNEL").build())
          .build();
      final AirbyteConnectionStatus actual = source().check(config);
      assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, actual.getStatus());
    }
  }

  @Test
  void testStrictSSLSecuredWithTunnel() throws Exception {
    try (final var testdb = createTestDatabase()) {
      final var config = testdb.configBuilder()
          .withHostAndPort()
          .withDatabase()
          .with(JdbcUtils.USERNAME_KEY, testdb.getUserName())
          .with(JdbcUtils.PASSWORD_KEY, "fake")
          .withEncrytedTrustServerCertificate()
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
          .withEncrytedTrustServerCertificate()
          .with("tunnel_method", ImmutableMap.builder().put("tunnel_method", "SSH_KEY_AUTH").build())
          .build();
      final AirbyteConnectionStatus actual = source().check(config);
      assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
      assertTrue(actual.getMessage().contains("Could not connect with provided SSH configuration."), actual.getMessage());
    }
  }

  @Test
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
