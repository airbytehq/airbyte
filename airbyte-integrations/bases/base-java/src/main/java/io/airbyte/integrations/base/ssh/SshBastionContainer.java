/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.ssh;

import static io.airbyte.integrations.base.ssh.SshTunnel.TunnelMethod.SSH_KEY_AUTH;
import static io.airbyte.integrations.base.ssh.SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.util.Objects;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.JdbcDatabaseContainer;
import org.testcontainers.containers.Network;
import org.testcontainers.images.builder.ImageFromDockerfile;

public class SshBastionContainer {

  private static final String SSH_USER = "sshuser";
  private static final String SSH_PASSWORD = "secret";
  private Network network;
  private GenericContainer bastion;

  public void initAndStartBastion() {
    network = Network.newNetwork();
    bastion = new GenericContainer(
        new ImageFromDockerfile("bastion-test")
            .withFileFromClasspath("Dockerfile", "bastion/Dockerfile"))
                .withNetwork(network)
                .withExposedPorts(22);
    bastion.start();
  }

  public JsonNode getTunnelConfig(SshTunnel.TunnelMethod tunnelMethod, ImmutableMap.Builder<Object, Object> builderWithSchema)
      throws IOException, InterruptedException {

    return Jsons.jsonNode(builderWithSchema
        .put("tunnel_method", Jsons.jsonNode(ImmutableMap.builder()
            .put("tunnel_host",
                Objects.requireNonNull(bastion.getContainerInfo().getNetworkSettings()
                    .getNetworks()
                    .get(((Network.NetworkImpl) network).getName())
                    .getIpAddress()))
            .put("tunnel_method", tunnelMethod)
            .put("tunnel_port", bastion.getExposedPorts().get(0))
            .put("tunnel_user", SSH_USER)
            .put("tunnel_user_password", tunnelMethod.equals(SSH_PASSWORD_AUTH) ? SSH_PASSWORD : "")
            .put("ssh_key", tunnelMethod.equals(SSH_KEY_AUTH) ? bastion.execInContainer("cat", "var/bastion/id_rsa").getStdout() : "")
            .build()))
        .build());
  }

  public ImmutableMap.Builder<Object, Object> getBasicDbConfigBuider(JdbcDatabaseContainer<?> db) {
    return ImmutableMap.builder()
        .put("host", Objects.requireNonNull(db.getContainerInfo().getNetworkSettings()
            .getNetworks()
            .get(((Network.NetworkImpl) getNetWork()).getName())
            .getIpAddress()))
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .put("port", db.getExposedPorts().get(0))
        .put("database", db.getDatabaseName())
        .put("ssl", false);
  }

  public Network getNetWork() {
    return this.network;
  }

  public void stopAndCloseContainers(JdbcDatabaseContainer<?> db) {
    db.stop();
    db.close();
    bastion.stop();
    bastion.close();
    network.close();
  }

}
