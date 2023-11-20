/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.testutils;

import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.PostgresUtils;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.util.HostPortResolver;
import io.airbyte.commons.string.Strings;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.Container.ExecResult;
import org.testcontainers.containers.Network;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.DockerImageName;
import org.testcontainers.utility.MountableFile;

/**
 * {@link PostgresTestDatabase} is a convenience object which allows for efficient use of
 * {@link PostgreSQLContainer} instances in tests. Each test container is shared throughout the
 * whole JVM. Isolation is performed by creating a new database and a new user for each
 * {@link PostgresTestDatabase} instance. These are dropped when the instance is closed.
 */
public class PostgresTestDatabase implements AutoCloseable {

  static private final Logger LOGGER = LoggerFactory.getLogger(PostgresTestDatabase.class);

  public enum PostgresImage {

    POSTGRES_12_BULLSEYE("postgres:12-bullseye"),
    POSTGRES_16_BULLSEYE("postgres:16-bullseye"),
    POSTGRES_16_ALPINE("postgres:16-alpine"),
    POSTGRES_9_ALPINE("postgres:9-alpine"),
    ;

    private final String imageName;

    PostgresImage(String imageName) {
      this.imageName = imageName;
    }

  }

  public enum PostgresImageLayer {

    ASCII(ContainerFactory::withASCII),
    CONF(ContainerFactory::withConf),
    NETWORK(ContainerFactory::withNetwork),
    CERT(ContainerFactory::withCert),
    WAL_LEVEL_LOGICAL(ContainerFactory::withWalLevelLogical),
    ;

    final Consumer<ContainerFactory> method;

    PostgresImageLayer(Consumer<ContainerFactory> method) {
      this.method = method;
    }

  }

  /**
   * Create a new {@link PostgresTestDatabase} instance.
   *
   * @param postgresImage base image to use for the underlying {@link PostgreSQLContainer}.
   * @param methods {@link ContainerFactory} methods that need to be called.
   * @return a new {@link PostgresTestDatabase} instance which may reuse a shared
   *         {@link PostgreSQLContainer}.
   */
  static public PostgresTestDatabase make(PostgresImage postgresImage, PostgresImageLayer... methods) {
    final String imageNamePlusMethods = Stream.concat(
        Stream.of(postgresImage.imageName),
        Stream.of(methods).map(PostgresImageLayer::name))
        .collect(Collectors.joining("+"));
    final ContainerFactory factory = ContainerFactory.LAZY.computeIfAbsent(imageNamePlusMethods, ContainerFactory::new);
    return new PostgresTestDatabase(factory.getOrCreateSharedContainer());
  }

  private PostgresTestDatabase(PostgreSQLContainer<?> sharedContainer) {
    this.container = sharedContainer;
    this.suffix = Strings.addRandomSuffix("", "_", 10);
    this.dbName = "db" + suffix;
    this.userName = "test_user" + suffix;
    this.password = "test_password" + suffix;
    execSQL(
        String.format("CREATE DATABASE %s", dbName),
        String.format("CREATE USER %s PASSWORD '%s'", userName, password),
        String.format("GRANT ALL PRIVILEGES ON DATABASE %s TO %s", dbName, userName),
        String.format("ALTER USER %s WITH SUPERUSER", userName));

    this.jdbcUrl = String.format(
        DatabaseDriver.POSTGRESQL.getUrlFormatString(),
        sharedContainer.getHost(),
        sharedContainer.getFirstMappedPort(),
        dbName);
    this.dslContext = DSLContextFactory.create(
        userName,
        password,
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        jdbcUrl,
        SQLDialect.POSTGRES);
    this.database = new Database(dslContext);

  }

  public final PostgreSQLContainer<?> container;
  public final String suffix, dbName, userName, password, jdbcUrl;
  public final DSLContext dslContext;
  public final Database database;

  /**
   * Convenience method for building identifiers which are unique to this instance.
   */
  public String withSuffix(String str) {
    return str + suffix;
  }

  /**
   * Convenience method for initializing a config builder for use in integration tests.
   */
  public ImmutableMap.Builder<Object, Object> makeConfigBuilder() {
    return ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveHost(container))
        .put(JdbcUtils.PORT_KEY, HostPortResolver.resolvePort(container))
        .put(JdbcUtils.DATABASE_KEY, dbName)
        .put(JdbcUtils.USERNAME_KEY, userName)
        .put(JdbcUtils.PASSWORD_KEY, password);
  }

  /**
   * @return the {@link PostgresUtils.Certificate} for this instance; requires
   *         {@link ContainerFactory#withCert} call.
   */
  public PostgresUtils.Certificate getCertificate() {
    final String caCert, clientKey, clientCert;
    try {
      caCert = container.execInContainer("su", "-c", "cat /var/lib/postgresql/certs/ca.crt").getStdout().trim();
      clientKey = container.execInContainer("su", "-c", "cat /var/lib/postgresql/certs/client.key").getStdout().trim();
      clientCert = container.execInContainer("su", "-c", "cat /var/lib/postgresql/certs/client.crt").getStdout().trim();
    } catch (IOException e) {
      throw new UncheckedIOException(e);
    } catch (InterruptedException e) {
      throw new RuntimeException(e);
    }
    return new PostgresUtils.Certificate(caCert, clientCert, clientKey);
  }

  public void execSQL(String... stmts) {
    final List<String> cmd = Stream.concat(
        Stream.of("psql", "-a", "-d", container.getDatabaseName(), "-U", container.getUsername()),
        Stream.of(stmts).flatMap(stmt -> Stream.of("-c", stmt)))
        .toList();
    try {
      LOGGER.debug("executing {}", Strings.join(cmd, " "));
      final var exec = container.execInContainer(cmd.toArray(new String[0]));
      LOGGER.debug("exit code: {}\nstdout:\n{}\nstderr:\n{}", exec.getExitCode(), exec.getStdout(), exec.getStderr());
    } catch (IOException e) {
      throw new UncheckedIOException(e);
    } catch (InterruptedException e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * Drop the database owned by this instance.
   */
  public void dropDatabase() {
    execSQL(String.format("DROP DATABASE %s", dbName));
  }

  /**
   * Close resources held by this instance. This deliberately avoids dropping the database, which is
   * really expensive in Postgres. This is because a DROP DATABASE in Postgres triggers a CHECKPOINT.
   * Call {@link #dropDatabase} to explicitly drop the database.
   */
  @Override
  public void close() {
    dslContext.close();
  }

  static private class ContainerFactory {

    static private final Logger LOGGER = LoggerFactory.getLogger(ContainerFactory.class);
    static private final ConcurrentHashMap<String, ContainerFactory> LAZY = new ConcurrentHashMap<>();

    final private String imageName;
    final private List<PostgresImageLayer> imageLayers;
    private PostgreSQLContainer<?> sharedContainer;
    private RuntimeException containerCreationError;

    private ContainerFactory(String imageNamePlusMethods) {
      final String[] parts = imageNamePlusMethods.split("\\+");
      this.imageName = parts[0];
      this.imageLayers = Arrays.stream(parts).skip(1).map(PostgresImageLayer::valueOf).toList();
    }

    private synchronized PostgreSQLContainer<?> getOrCreateSharedContainer() {
      if (sharedContainer == null) {
        if (containerCreationError != null) {
          throw new RuntimeException(
              "Error during container creation for imageName=" + imageName + ", methods="
                  + imageLayers.stream().map(PostgresImageLayer::name).toList(),
              containerCreationError);
        }
        LOGGER.info("Creating new shared container based on {} with {}.", imageName, imageLayers.stream().map(PostgresImageLayer::name).toList());
        try {
          final var parsed = DockerImageName.parse(imageName).asCompatibleSubstituteFor("postgres");
          sharedContainer = new PostgreSQLContainer<>(parsed);
          for (PostgresImageLayer imageLayer : imageLayers) {
            LOGGER.info("Calling {} on new shared container based on {}.", imageLayer.name(),
                imageName);
            imageLayer.method.accept(this);
          }
          sharedContainer.start();
        } catch (RuntimeException e) {
          this.sharedContainer = null;
          containerCreationError = e;
          throw e;
        }
      }
      return sharedContainer;
    }

    /**
     * Apply the postgresql.conf file that we've packaged as a resource.
     */
    public void withConf() {
      if (sharedContainer.isRunning()) {
        throw new RuntimeException("the shared container is already running. This call will have no effect!");
      }
      sharedContainer
          .withCopyFileToContainer(
              MountableFile.forClasspathResource("postgresql.conf"),
              "/etc/postgresql/postgresql.conf")
          .withCommand("postgres -c config_file=/etc/postgresql/postgresql.conf");
    }

    /**
     * Create a new network and bind it to the container.
     */
    public void withNetwork() {
      if (sharedContainer.isRunning()) {
        throw new RuntimeException("the shared container is already running. This call will have no effect!");
      }
      sharedContainer.withNetwork(Network.newNetwork());
    }

    /**
     * Configure postgres with wal_level=logical.
     */
    public void withWalLevelLogical() {
      if (sharedContainer.isRunning()) {
        throw new RuntimeException("the shared container is already running. This call will have no effect!");
      }
      sharedContainer.withCommand("postgres -c wal_level=logical");
    }

    /**
     * Generate SSL certificates and tell postgres to enable SSL and use them.
     */
    public void withCert() {
      sharedContainer.start();
      String[] commands = {
        "mkdir /var/lib/postgresql/certs",
        // create the CA key and certificate
        "openssl ecparam -name prime256v1 -genkey -noout -out /var/lib/postgresql/certs/ca.key",
        "openssl req -new -x509 -sha256 -key /var/lib/postgresql/certs/ca.key -out /var/lib/postgresql/certs/ca.crt -subj \"/CN=127.0.0.1\"",
        // create the server key and certificate, certified by the CA above
        "openssl ecparam -name prime256v1 -genkey -noout -out /var/lib/postgresql/certs/server.key",
        "openssl req -new -sha256 -key /var/lib/postgresql/certs/server.key -out /var/lib/postgresql/certs/server.csr -subj \"/CN=localhost\"",
        "openssl x509 -req -in /var/lib/postgresql/certs/server.csr -CA /var/lib/postgresql/certs/ca.crt -CAkey /var/lib/postgresql/certs/ca.key " +
            "-CAcreateserial -out /var/lib/postgresql/certs/server.crt -days 365 -sha256",
        // reconfigure postgres
        "echo \"ssl = on\" >> /var/lib/postgresql/data/postgresql.conf",
        "echo \"ssl_cert_file = '/var/lib/postgresql/certs/server.crt'\" >> /var/lib/postgresql/data/postgresql.conf",
        "echo \"ssl_key_file = '/var/lib/postgresql/certs/server.key'\" >> /var/lib/postgresql/data/postgresql.conf",
        "echo \"ssl_ca_file = '/var/lib/postgresql/certs/ca.crt'\" >> /var/lib/postgresql/data/postgresql.conf",
        // Here, we reset pg_hba to not accept any connection except locals.
        "echo \"local all test all trust\" > /var/lib/postgresql/data/pg_hba.conf",
        // Then we add SSL-only with full certification to the user used by all network connections.
        "echo \"hostssl all " + sharedContainer.getUsername() + " all cert\" >> /var/lib/postgresql/data/pg_hba.conf",
        // finally, create client key and certificate, both verified by the CA
        "openssl ecparam -name prime256v1 -genkey -noout -out /var/lib/postgresql/certs/client.key",
        "openssl req -new -sha256 -key /var/lib/postgresql/certs/client.key -out /var/lib/postgresql/certs/client.csr -subj \"/CN="
            + sharedContainer.getUsername() + "\"",
        "openssl x509 -req -in /var/lib/postgresql/certs/client.csr -CA /var/lib/postgresql/certs/ca.crt -CAkey /var/lib/postgresql/certs/ca.key " +
            "-CAcreateserial -out /var/lib/postgresql/certs/client.crt -days 365 -sha256",
        // make everything accessible by postgres only, as required by the postgres doc at
        // https://www.postgresql.org/docs/16/ssl-tcp.html
        "chmod 0600 /var/lib/postgresql/certs/*",
        "chown postgres:postgres /var/lib/postgresql/certs/*",
        // reload config and pg_hba.
        "psql -U test -c \"SELECT pg_reload_conf();\""
      };
      for (String cmd : commands) {
        try {
          ExecResult res = sharedContainer.execInContainer("su", "-c", cmd);
          if (res.getExitCode() != 0) {
            LOGGER.warn(res.getStdout());
            PostgresTestDatabase.LOGGER.error(res.getStderr());
            throw new RuntimeException("execution failed. CMD = " + cmd);
          }
        } catch (IOException e) {
          throw new UncheckedIOException(e);
        } catch (InterruptedException e) {
          throw new RuntimeException(e);
        }
      }
    }

    /**
     * Configure postgres with client_encoding=sql_ascii.
     */
    public void withASCII() {
      sharedContainer.withCommand("postgres -c client_encoding=sql_ascii");
    }

  }

}
