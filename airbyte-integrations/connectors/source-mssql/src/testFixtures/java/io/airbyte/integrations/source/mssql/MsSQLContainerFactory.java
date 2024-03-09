/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import io.airbyte.cdk.testutils.ContainerFactory;
import org.apache.commons.lang3.StringUtils;
import org.testcontainers.containers.MSSQLServerContainer;
import org.testcontainers.containers.Network;
import org.testcontainers.utility.DockerImageName;

public class MsSQLContainerFactory extends ContainerFactory<MSSQLServerContainer<?>> {

  @Override
  protected MSSQLServerContainer<?> createNewContainer(DockerImageName imageName) {
    imageName = imageName.asCompatibleSubstituteFor("mcr.microsoft.com/mssql/server");
    var container = new MSSQLServerContainer<>(imageName).acceptLicense();
    container.addEnv("MSSQL_MEMORY_LIMIT_MB", "384");
    withNetwork(container);
    return container;
  }

  /**
   * Create a new network and bind it to the container.
   */
  public static void withNetwork(MSSQLServerContainer<?> container) {
    container.withNetwork(Network.newNetwork());
  }

  public static void withAgent(MSSQLServerContainer<?> container) {
    container.addEnv("MSSQL_AGENT_ENABLED", "True");
  }

  public static void withSslCertificates(MSSQLServerContainer<?> container) {
    // yes, this is uglier than sin. The reason why I'm doing this is because there's no command to
    // reload a SqlServer config. So I need to create all the necessary files before I start the
    // SQL server. Hence this horror
    String command = StringUtils.replace(
        """
        mkdir /tmp/certs/ &&
        openssl req -nodes -new -x509 -sha256 -keyout /tmp/certs/ca.key -out /tmp/certs/ca.crt -subj "/CN=ca" &&
        openssl req -nodes -new -x509 -sha256 -keyout /tmp/certs/dummy_ca.key -out /tmp/certs/dummy_ca.crt -subj "/CN=ca" &&
        openssl req -nodes -new -sha256 -keyout /tmp/certs/server.key -out /tmp/certs/server.csr -subj "/CN={hostName}" &&
        openssl req -nodes -new -sha256 -keyout /tmp/certs/dummy_server.key -out /tmp/certs/dummy_server.csr -subj "/CN={hostName}" &&

        openssl x509 -req -in /tmp/certs/server.csr -CA /tmp/certs/ca.crt -CAkey /tmp/certs/ca.key -out /tmp/certs/server.crt -days 365 -sha256 &&
        openssl x509 -req -in /tmp/certs/dummy_server.csr -CA /tmp/certs/ca.crt -CAkey /tmp/certs/ca.key -out /tmp/certs/dummy_server.crt -days 365 -sha256 &&
        openssl x509 -req -in /tmp/certs/server.csr -CA /tmp/certs/dummy_ca.crt -CAkey /tmp/certs/dummy_ca.key -out /tmp/certs/server_dummy_ca.crt -days 365 -sha256 &&
        chmod 440 /tmp/certs/* &&
        {
        cat > /var/opt/mssql/mssql.conf <<- EOF
        [network]
          tlscert = /tmp/certs/server.crt
          tlskey = /tmp/certs/server.key
          tlsprotocols = 1.2
          forceencryption = 1
        EOF
        } && /opt/mssql/bin/sqlservr
        """,
        "{hostName}", container.getHost());
    container.withCommand("bash", "-c", command)
        .withUrlParam("trustServerCertificate", "true");
  }

}
