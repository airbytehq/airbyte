/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.ssh.SshBastionContainer;
import io.airbyte.integrations.base.ssh.SshTunnel;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.testcontainers.containers.MongoDBContainer;
import org.testcontainers.containers.Network;

public abstract class SshMongoDbDestinationAcceptanceTest extends MongodbDestinationAcceptanceTest {

  private static final Network network = Network.newNetwork();
  private static final SshBastionContainer bastion = new SshBastionContainer();
  private static MongoDBContainer container;
  private static final int DEFAULT_PORT = 27017;

  public abstract SshTunnel.TunnelMethod getTunnelMethod();

  @BeforeAll
  public static void beforeAll() {
    container = new MongoDBContainer(DOCKER_IMAGE_NAME)
        .withNetwork(network)
        .withExposedPorts(DEFAULT_PORT);
    container.start();
    bastion.initAndStartBastion(network);
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return bastion.getTunnelConfig(getTunnelMethod(), ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, container.getHost())
        .put(JdbcUtils.PORT_KEY, container.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, DATABASE_NAME)
        .put(AUTH_TYPE, getAuthTypeConfig()));
  }

  @Override
  protected JsonNode getFailCheckConfig() throws Exception {
    // should result in a failed connection check
    return bastion.getTunnelConfig(getTunnelMethod(), ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, container.getHost())
        .put(JdbcUtils.PORT_KEY, container.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, DATABASE_NAME)
        .put(AUTH_TYPE, Jsons.jsonNode(ImmutableMap.builder()
            .put("authorization", "login/password")
            .put(JdbcUtils.USERNAME_KEY, "user")
            .put(JdbcUtils.PASSWORD_KEY, "invalid_pass")
            .build())));
  }

  @AfterAll
  public static void afterAll() {
    container.close();
    bastion.getContainer().close();
  }

}
