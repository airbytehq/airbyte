/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import io.airbyte.cdk.testutils.ContainerFactory;
import java.io.IOException;
import java.io.UncheckedIOException;
import org.testcontainers.containers.Network;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.DockerImageName;
import org.testcontainers.utility.MountableFile;

/**
 * TODO: This class is a copy from source-postgres:testFixtures. Eventually merge into a common
 * fixtures module.
 */
public class PostgresContainerFactory extends ContainerFactory<PostgreSQLContainer<?>> {

  @Override
  protected PostgreSQLContainer<?> createNewContainer(DockerImageName imageName) {
    return new PostgreSQLContainer<>(imageName.asCompatibleSubstituteFor("postgres"));
  }

  /**
   * Apply the postgresql.conf file that we've packaged as a resource.
   */
  public static void withConf(PostgreSQLContainer<?> container) {
    container
        .withCopyFileToContainer(
            MountableFile.forClasspathResource("postgresql.conf"),
            "/etc/postgresql/postgresql.conf")
        .withCommand("postgres -c config_file=/etc/postgresql/postgresql.conf");
  }

  /**
   * Create a new network and bind it to the container.
   */
  public static void withNetwork(PostgreSQLContainer<?> container) {
    container.withNetwork(Network.newNetwork());
  }

  /**
   * Generate SSL certificates and tell postgres to enable SSL and use them.
   */
  public static void withCert(PostgreSQLContainer<?> container) {
    container.start();
    String[] commands = {
      "psql -U test -c \"CREATE USER postgres WITH PASSWORD 'postgres';\"",
      "psql -U test -c \"GRANT CONNECT ON DATABASE \"test\" TO postgres;\"",
      "psql -U test -c \"ALTER USER postgres WITH SUPERUSER;\"",
      "openssl ecparam -name prime256v1 -genkey -noout -out ca.key",
      "openssl req -new -x509 -sha256 -key ca.key -out ca.crt -subj \"/CN=127.0.0.1\"",
      "openssl ecparam -name prime256v1 -genkey -noout -out server.key",
      "openssl req -new -sha256 -key server.key -out server.csr -subj \"/CN=localhost\"",
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
      "mkdir root/.postgresql",
      "echo \"hostssl    all    all    127.0.0.1/32    cert clientcert=verify-full\" >> /var/lib/postgresql/data/pg_hba.conf",
      "openssl ecparam -name prime256v1 -genkey -noout -out client.key",
      "openssl req -new -sha256 -key client.key -out client.csr -subj \"/CN=postgres\"",
      "openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365 -sha256",
      "cp client.crt ~/.postgresql/postgresql.crt",
      "cp client.key ~/.postgresql/postgresql.key",
      "chmod 0600 ~/.postgresql/postgresql.crt ~/.postgresql/postgresql.key",
      "cp ca.crt root/.postgresql/ca.crt",
      "chown postgres:postgres ~/.postgresql/ca.crt",
      "psql -U test -c \"SELECT pg_reload_conf();\"",
    };
    for (String cmd : commands) {
      try {
        container.execInContainer("su", "-c", cmd);
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
  public static void withSSL(PostgreSQLContainer<?> container) {
    container.withCommand("postgres " +
        "-c ssl=on " +
        "-c ssl_cert_file=/var/lib/postgresql/server.crt " +
        "-c ssl_key_file=/var/lib/postgresql/server.key");
  }

  /**
   * Configure postgres with client_encoding=sql_ascii.
   */
  public static void withASCII(PostgreSQLContainer<?> container) {
    container.withCommand("postgres -c client_encoding=sql_ascii");
  }

}
