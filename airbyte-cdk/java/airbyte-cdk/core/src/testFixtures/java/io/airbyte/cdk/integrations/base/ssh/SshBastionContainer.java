/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.base.ssh;

import static io.airbyte.cdk.integrations.base.ssh.SshTunnel.TunnelMethod.SSH_KEY_AUTH;
import static io.airbyte.cdk.integrations.base.ssh.SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.integrations.util.HostPortResolver;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.util.List;
import java.util.Objects;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.testcontainers.containers.Container;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.JdbcDatabaseContainer;
import org.testcontainers.containers.Network;
import org.testcontainers.images.builder.ImageFromDockerfile;

public class SshBastionContainer implements AutoCloseable {

  private static final String SSH_USER = "sshuser";
  private static final String SSH_PASSWORD = "secret";
  private GenericContainer bastion;

  public void initAndStartBastion(final Network network) {
    bastion = new GenericContainer(
        new ImageFromDockerfile("bastion-test")
            .withFileFromClasspath("Dockerfile", "bastion/Dockerfile"))
                .withNetwork(network)
                .withExposedPorts(22);
    bastion.start();
  }

  public JsonNode getTunnelMethod(final SshTunnel.TunnelMethod tunnelMethod,
                                  final boolean innerAddress)
      throws IOException, InterruptedException {
    final var containerAddress = innerAddress ? getInnerContainerAddress(bastion) : getOuterContainerAddress(bastion);
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("tunnel_host",
            Objects.requireNonNull(containerAddress.left))
        .put("tunnel_method", tunnelMethod)
        .put("tunnel_port", containerAddress.right)
        .put("tunnel_user", SSH_USER)
        .put("tunnel_user_password", tunnelMethod.equals(SSH_PASSWORD_AUTH) ? SSH_PASSWORD : "")
        .put("ssh_key", tunnelMethod.equals(SSH_KEY_AUTH) ? bastion.execInContainer("cat", "var/bastion/id_rsa").getStdout() : "")
        .build());
  }

  public JsonNode getTunnelConfig(final SshTunnel.TunnelMethod tunnelMethod,
                                  final ImmutableMap.Builder<Object, Object> builderWithSchema,
                                  final boolean innerAddress)
      throws IOException, InterruptedException {
    return Jsons.jsonNode(builderWithSchema
        .put("tunnel_method", getTunnelMethod(tunnelMethod, innerAddress))
        .build());
  }

  public ImmutableMap.Builder<Object, Object> getBasicDbConfigBuider(final JdbcDatabaseContainer<?> db) {
    return getBasicDbConfigBuider(db, db.getDatabaseName());
  }

  public ImmutableMap.Builder<Object, Object> getBasicDbConfigBuider(final JdbcDatabaseContainer<?> db, final List<String> schemas) {
    return getBasicDbConfigBuider(db, db.getDatabaseName()).put("schemas", schemas);
  }

  public ImmutableMap.Builder<Object, Object> getBasicDbConfigBuider(final JdbcDatabaseContainer<?> db, final String schemaName) {
    return ImmutableMap.builder()
        .put("host", Objects.requireNonNull(HostPortResolver.resolveHost(db)))
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .put("port", HostPortResolver.resolvePort(db))
        .put("database", schemaName)
        .put("ssl", false);
  }

  public void stopAndCloseContainers(final JdbcDatabaseContainer<?> db) {
    bastion.stop();
    bastion.close();
    db.stop();
    db.close();
  }

  public void stopAndClose() {
    bastion.close();
  }

  @Override
  public void close() {
    stopAndClose();
  }

  public GenericContainer getContainer() {
    return bastion;
  }

  /**
   * Returns the inner docker network ip address and port of a container. This can be used to reach a
   * container from another container running on the same network
   *
   * @param container container
   * @return a pair of host and port
   */
  public static ImmutablePair<String, Integer> getInnerContainerAddress(final Container container) {
    return ImmutablePair.of(
        container.getContainerInfo().getNetworkSettings().getNetworks().entrySet().stream().findFirst().get().getValue().getIpAddress(),
        (Integer) container.getExposedPorts().stream().findFirst().get());
  }

  /**
   * Returns the outer docker network ip address and port of a container. This can be used to reach a
   * container from the host machine
   *
   * @param container container
   * @return a pair of host and port
   */
  public static ImmutablePair<String, Integer> getOuterContainerAddress(final Container container) {
    return ImmutablePair.of(
        container.getHost(),
        container.getFirstMappedPort());
  }

}
