/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import io.airbyte.cdk.integrations.util.HostPortResolver;
import io.airbyte.cdk.testutils.ContainerFactory;
import java.io.IOException;
import java.io.UncheckedIOException;
import org.apache.commons.lang3.StringUtils;
import org.testcontainers.containers.Container.ExecResult;
import org.testcontainers.containers.Network;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.DockerImageName;
import org.testcontainers.utility.MountableFile;

public class PostgresContainerFactory implements ContainerFactory<PostgreSQLContainer<?>> {

  @Override
  public PostgreSQLContainer<?> createNewContainer(DockerImageName imageName) {
    return new PostgreSQLContainer<>(imageName.asCompatibleSubstituteFor("postgres"));

  }

  @Override
  public Class<?> getContainerClass() {
    return PostgreSQLContainer.class;
  }

  /**
   * Apply the postgresql.conf file that we've packaged as a resource.
   */
  public void withConf(PostgreSQLContainer<?> container) {
    container
        .withCopyFileToContainer(
            MountableFile.forClasspathResource("postgresql.conf"),
            "/etc/postgresql/postgresql.conf")
        .withCommand("postgres -c config_file=/etc/postgresql/postgresql.conf");
  }

  /**
   * Create a new network and bind it to the container.
   */
  public void withNetwork(PostgreSQLContainer<?> container) {
    container.withNetwork(Network.newNetwork());
  }

  /**
   * Configure postgres with wal_level=logical.
   */
  public void withWalLevelLogical(PostgreSQLContainer<?> container) {
    container.withCommand("postgres -c wal_level=logical");
  }

  /**
   * Generate SSL certificates and tell postgres to enable SSL and use them.
   */
  public void withCert(PostgreSQLContainer<?> container) {
    container.start();
    String[] commands = {
      "psql -U test -c \"CREATE USER postgres WITH PASSWORD 'postgres';\"",
      "psql -U test -c \"GRANT CONNECT ON DATABASE \"test\" TO postgres;\"",
      "psql -U test -c \"ALTER USER postgres WITH SUPERUSER;\"",
      "openssl ecparam -name prime256v1 -genkey -noout -out ca.key",
      "openssl req -new -x509 -sha256 -key ca.key -out ca.crt -subj \"/CN=127.0.0.1\"",
      "openssl ecparam -name prime256v1 -genkey -noout -out server.key",
      StringUtils.replace("openssl req -new -sha256 -key server.key -out server.csr -subj \"/CN={hostName}\"", "{hostName}", HostPortResolver.resolveHost(container)),
      "openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365 -sha256",
      "cp server.key /etc/ssl/private/",
      "cp server.crt /etc/ssl/private/",
      "cp ca.crt /etc/ssl/private/",
      "chmod og-rwx /etc/ssl/private/server.* /etc/ssl/private/ca.*",
      "chown postgres:postgres /etc/ssl/private/server.crt /etc/ssl/private/server.key /etc/ssl/private/ca.crt",
      "echo \"ssl = on\" >> /var/lib/postgresql/data/postgresql.conf",
      "echo \"ssl_cert_file = '/etc/ssl/private/server.crt'\" >> /var/lib/postgresql/data/postgresql.conf",
      "echo \"ssl_key_file = '/etc/ssl/private/server.key'\" >> /var/lib/postgresql/data/postgresql.conf",
      "echo \"ssl_ca_file = '/etc/ssl/private/ca.crt'\" >> /var/lib/postgresql/data/postgresql.conf",
      "rm /var/lib/postgresql/data/pg_hba.conf",
      "echo \"local      all    test                   trust\" >> /var/lib/postgresql/data/pg_hba.conf",
      "echo \"host       all    test   all             trust\" >> /var/lib/postgresql/data/pg_hba.conf",
      "echo \"hostssl    all    all    all             cert clientcert=verify-full\" >> /var/lib/postgresql/data/pg_hba.conf",
      "psql -U test -c \"SELECT pg_reload_conf();\""
    };
    for (String cmd : commands) {
      try {
        ExecResult execResult = container.execInContainer("su", "-c", cmd);
        if (execResult.getExitCode() != 0) {
          throw new RuntimeException ("Command '" + cmd + "' returned result code " + execResult.getExitCode() + ". stderr was:\n" + execResult.getStderr());
        }
      } catch (IOException e) {
        throw new UncheckedIOException(e);
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }
    }
  }

  /**
   * Tell postgres to enable SSL.
   */
  public void withSSL(PostgreSQLContainer<?> container) {
    container.withCommand("postgres " +
        "-c ssl=on " +
        "-c ssl_cert_file=/var/lib/postgresql/server.crt " +
        "-c ssl_key_file=/var/lib/postgresql/server.key");
  }

  /**
   * Configure postgres with client_encoding=sql_ascii.
   */
  public void withASCII(PostgreSQLContainer<?> container) {
    container.withCommand("postgres -c client_encoding=sql_ascii");
  }

}
