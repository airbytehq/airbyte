/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import io.airbyte.cdk.testutils.ContainerFactory;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.BaseImage;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;
import org.apache.commons.lang3.StringUtils;
import org.testcontainers.containers.MSSQLServerContainer;
import org.testcontainers.containers.Network;
import org.testcontainers.utility.DockerImageName;

public class MsSQLContainerFactory extends ContainerFactory<MSSQLServerContainer<?>> {

  private static final class MsSqlContainer extends MSSQLServerContainer<MsSqlContainer> {

    MsSqlContainer(DockerImageName imageName) {
      super(imageName);
    }

    protected void waitUntilContainerStarted() {
      long start = System.currentTimeMillis();
      super.waitUntilContainerStarted();
      @SuppressWarnings("deprecation")
      long startupTimeoutSeconds = getStartupTimeoutSeconds();
      Exception lastConnectionException = null;
      int tryCount = 1;
      while (System.currentTimeMillis() < start + (1000 * startupTimeoutSeconds)) {
        try (Connection connection = createConnection(""); Statement statement = connection.createStatement()) {
          Thread.sleep(100L);
          execInContainer("bash", "-c", "echo \"SGX `date` checking agent status (try" + tryCount + ")...\" >> /var/opt/mssql/log/sqlagent.out");
          ResultSet rs = statement.executeQuery("EXEC master.dbo.xp_servicecontrol 'QueryState', N'SQLServerAGENT';");
          if (!rs.next()) {
            execInContainer("bash", "-c",
                "echo \"SGX `date` no agent status in DB(try" + tryCount + "). Retrying in 1sec\" >> /var/opt/mssql/log/sqlagent.out");
          } else {
            String agentStatus = rs.getString(1);
            execInContainer("bash", "-c",
                "echo \"SGX `date` agent status was " + agentStatus + "(try" + tryCount + ")\" >> /var/opt/mssql/log/sqlagent.out");
            if ("Running.".equals(agentStatus)) {
              return;
            }
          }
          tryCount++;
        } catch (Exception e) {
          lastConnectionException = e;
          // ignore so that we can try again
          logger().debug("Failure when trying test query", e);
          try {
            execInContainer("bash", "-c",
                "echo \"SGX  `date` error :  " + e.getMessage() + "\" >> /var/opt/mssql/log/sqlagent.out");
          } catch (Exception e2) {
            // ignore
          }
        }
      }

      throw new IllegalStateException(
          String.format(
              "Container is started, but cannot be accessed by (JDBC URL: %s), please check container logs",
              this.getJdbcUrl()),
          lastConnectionException);
    }

  }

  MSSQLServerContainer<?> shared(BaseImage image) {
    return shared(image.reference);
  }

  @Override
  public MSSQLServerContainer<?> createNewContainer(DockerImageName imageName) {
    MsSqlContainer container =
        new MsSqlContainer(imageName.asCompatibleSubstituteFor("mcr.microsoft.com/mssql/server")).acceptLicense();
    container.addEnv("MSSQL_AGENT_ENABLED", "True");
    container.withNetwork(Network.newNetwork());
    withSslCertificates(container);
    return container;
  }

  public void withSslCertificates(MSSQLServerContainer<?> container) {
    // yes, this is uglier than sin. The reason why I'm doing this is because there's no command to
    // reload a SqlServer config. So I need to create all the necessary files before I start the
    // SQL server. Hence this horror
    String command = StringUtils.replace(
        """
        mkdir -p /var/opt/mssql/log && touch  /var/opt/mssql/log/sqlagent.out
        { tail -F /var/opt/mssql/log/sqlagent.out | sed 's/[^[:print:]]//g' | sed 's/^/agentLog:/' & } &&
        { while [ 1 ]; do sleep 1 && echo "`date` heartbeat" >> /var/opt/mssql/log/sqlagent.out ; done & } &&
        mkdir /tmp/certs/ &&
        openssl req -nodes -new -x509 -sha256 -keyout /tmp/certs/ca.key -out /tmp/certs/ca.crt -subj "/CN=ca" &&
        openssl req -nodes -new -x509 -sha256 -keyout /tmp/certs/dummy_ca.key -out /tmp/certs/dummy_ca.crt -subj "/CN=ca" &&
        openssl req -nodes -new -sha256 -keyout /tmp/certs/server.key -out /tmp/certs/server.csr -subj "/CN={hostName}" &&
        openssl req -nodes -new -sha256 -keyout /tmp/certs/dummy_server.key -out /tmp/certs/dummy_server.csr -subj "/CN={hostName}" &&

        openssl x509 -req -in /tmp/certs/server.csr -CA /tmp/certs/ca.crt -CAserial /tmp/certs/ca.srl -CAcreateserial -CAkey /tmp/certs/ca.key -out /tmp/certs/server.crt -days 365 -sha256 &&
        openssl x509 -req -in /tmp/certs/dummy_server.csr -CA /tmp/certs/ca.crt -CAserial /tmp/certs/ca.srl -CAcreateserial -CAkey /tmp/certs/ca.key -out /tmp/certs/dummy_server.crt -days 365 -sha256 &&
        openssl x509 -req -in /tmp/certs/server.csr -CA /tmp/certs/dummy_ca.crt -CAserial /tmp/certs/ca.srl -CAcreateserial -CAkey /tmp/certs/dummy_ca.key -out /tmp/certs/server_dummy_ca.crt -days 365 -sha256 &&
        chmod 440 /tmp/certs/* &&
        {
        cat > /var/opt/mssql/mssql.conf <<- EOF
        [network]
          tlscert = /tmp/certs/server.crt
          tlskey = /tmp/certs/server.key
          tlsprotocols = 1.2
          forceencryption = 1
        EOF
        } &&
        /opt/mssql/bin/sqlservr
        """,
        "{hostName}", container.getHost());
    container.withCommand("bash", "-c", command)
        .withUrlParam("trustServerCertificate", "true");
  }

}
