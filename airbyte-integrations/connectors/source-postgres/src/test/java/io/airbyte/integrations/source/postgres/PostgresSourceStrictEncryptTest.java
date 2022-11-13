/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.ssh.SshBastionContainer;
import io.airbyte.integrations.base.ssh.SshTunnel;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.Network;
import org.testcontainers.containers.PostgreSQLContainer;

public class PostgresSourceStrictEncryptTest {

  private static final SshBastionContainer bastion = new SshBastionContainer();
  private static final Network network = Network.newNetwork();

  @Test
  void testCheckWithSSlModeDisable() throws Exception {

    try (PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:13-alpine").withNetwork(network)) {
      bastion.initAndStartBastion(network);
      db.start();

      // stop to enforce ssl for ssl_mode disable
      final ImmutableMap.Builder<Object, Object> builderWithSSLModeDisable = getDatabaseConfigBuilderWithSSLMode(db, "disable");
      final JsonNode configWithSSLModeDisable = bastion.getTunnelConfig(SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH, builderWithSSLModeDisable);
      final AirbyteConnectionStatus connectionStatusForDisabledMode = new PostgresSourceStrictEncrypt().check(configWithSSLModeDisable);
      assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, connectionStatusForDisabledMode.getStatus());

    } finally {
      bastion.stopAndClose();
    }
  }

  @Test
  void testCheckWithSSlModePrefer() throws Exception {

    try (PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:13-alpine").withNetwork(network)) {
      bastion.initAndStartBastion(network);
      db.start();
      // continue to enforce ssl because ssl mode is prefer
      final ImmutableMap.Builder<Object, Object> builderWithSSLModePrefer = getDatabaseConfigBuilderWithSSLMode(db, "prefer");
      final JsonNode configWithSSLModePrefer = bastion.getTunnelConfig(SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH, builderWithSSLModePrefer);
      final AirbyteConnectionStatus connectionStatusForPreferredMode = new PostgresSourceStrictEncrypt().check(configWithSSLModePrefer);
      assertEquals(AirbyteConnectionStatus.Status.FAILED, connectionStatusForPreferredMode.getStatus());
      assertEquals("State code: 08004; Message: The server does not support SSL.", connectionStatusForPreferredMode.getMessage());

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

}
