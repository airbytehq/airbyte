/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.base.ssh;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.JdbcDatabaseContainer;
import org.testcontainers.containers.Network;
import org.testcontainers.images.builder.ImageFromDockerfile;

import java.io.IOException;
import java.util.Objects;

import static io.airbyte.integrations.base.ssh.SshTunnel.TunnelMethod.SSH_KEY_AUTH;
import static io.airbyte.integrations.base.ssh.SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH;

public class SshBastion {

    private static final String SSH_USER = "sshuser";
    private static final String SSH_PASSWORD = "secret";
    private static Network network;
    private static GenericContainer bastion;

    public static void initAndStartBastion() {
        network = Network.newNetwork();
        bastion = new GenericContainer(
                new ImageFromDockerfile("bastion-test")
                        .withFileFromClasspath("Dockerfile", "bastion/Dockerfile"))
                .withNetwork(network)
                .withExposedPorts(22);
        bastion.start();
    }

    public static JsonNode getTunnelConfig(SshTunnel.TunnelMethod tunnelMethod, ImmutableMap.Builder<Object, Object> builderWithSchema)
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

    public static ImmutableMap.Builder<Object, Object> getBasicDbConfigBuider(JdbcDatabaseContainer<?> db) {
        return ImmutableMap.builder()
                .put("host", Objects.requireNonNull(db.getContainerInfo().getNetworkSettings()
                        .getNetworks()
                        .get(((Network.NetworkImpl) network).getName())
                        .getIpAddress()))
                .put("username", db.getUsername())
                .put("password", db.getPassword())
                .put("port", db.getExposedPorts().get(0))
                .put("database", db.getDatabaseName())
                .put("ssl", false);
    }

    public static Network getNetWork() {
        return network;
    }

    public static void stopAndCloseContainers(JdbcDatabaseContainer<?> db) {
        db.stop();
        db.close();
        bastion.stop();
        bastion.close();
        network.close();
    }

}
