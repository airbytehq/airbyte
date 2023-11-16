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
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
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

  /**
   * Create a new {@link PostgresTestDatabase} instance.
   *
   * @param imageName base image to use for the underlying {@link PostgreSQLContainer}.
   * @param methods {@link ContainerFactory} methods that need to be called.
   * @return a new {@link PostgresTestDatabase} instance which may reuse a shared
   *         {@link PostgreSQLContainer}.
   */
  static public PostgresTestDatabase make(String imageName, String... methods) {
    final String imageNamePlusMethods = Stream.concat(
        Stream.of(imageName),
        Stream.of(methods))
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
      caCert = container.execInContainer("su", "-c", "cat ca.crt").getStdout().trim();
      clientKey = container.execInContainer("su", "-c", "cat client.key").getStdout().trim();
      clientCert = container.execInContainer("su", "-c", "cat client.crt").getStdout().trim();
    } catch (IOException e) {
      throw new UncheckedIOException(e);
    } catch (InterruptedException e) {
      throw new RuntimeException(e);
    }
    return new PostgresUtils.Certificate(caCert, clientCert, clientKey);
  }

  private void execSQL(String... stmts) {
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
    execSQL(String.format("DROP USER %s", userName));
  }

  static private class ContainerFactory {

    static private final Logger LOGGER = LoggerFactory.getLogger(ContainerFactory.class);
    static private final ConcurrentHashMap<String, ContainerFactory> LAZY = new ConcurrentHashMap<>();

    final private String imageName;
    final private List<Method> methods;
    private PostgreSQLContainer<?> sharedContainer;
    private RuntimeException containerCreationError;

    private ContainerFactory(String imageNamePlusMethods) {
      final String[] parts = imageNamePlusMethods.split("\\+");
      this.imageName = parts[0];
      this.methods = Arrays.stream(parts).skip(1).map(methodName -> {
        try {
          return ContainerFactory.class.getMethod(methodName);
        } catch (NoSuchMethodException e) {
          throw new RuntimeException(e);
        }
      }).toList();
    }

    private synchronized PostgreSQLContainer<?> getOrCreateSharedContainer() {
      if (sharedContainer == null) {
        if (containerCreationError != null) {
          throw new RuntimeException(
              "Error during container creation for imageName=" + imageName + ", methods=" + methods.stream().map(Method::getName).toList(),
              containerCreationError);
        }
        LOGGER.info("Creating new shared container based on {} with {}.", imageName, methods.stream().map(Method::getName).toList());
        try {
          final var parsed = DockerImageName.parse(imageName).asCompatibleSubstituteFor("postgres");
          sharedContainer = new PostgreSQLContainer<>(parsed);
          for (Method method : methods) {
            LOGGER.info("Calling {} on new shared container based on {}.", method.getName(),
                imageName);
            method.invoke(this);
          }
          sharedContainer.start();
        } catch (IllegalAccessException | InvocationTargetException e) {
          containerCreationError = new RuntimeException(e);
          this.sharedContainer = null;
          throw containerCreationError;
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
      sharedContainer.withNetwork(Network.newNetwork());
    }

    /**
     * Configure postgres with wal_level=logical.
     */
    public void withWalLevelLogical() {
      sharedContainer.withCommand("postgres -c wal_level=logical");
    }

    /**
     * Generate SSL certificates and tell postgres to enable SSL and use them.
     */
    public void withCert() {
      sharedContainer.start();
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
          sharedContainer.execInContainer("su", "-c", cmd);
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
    public void withSSL() {
      sharedContainer.withCommand("postgres " +
          "-c ssl=on " +
          "-c ssl_cert_file=/var/lib/postgresql/server.crt " +
          "-c ssl_key_file=/var/lib/postgresql/server.key");
    }

    /**
     * Configure postgres with client_encoding=sql_ascii.
     */
    public void withASCII() {
      sharedContainer.withCommand("postgres -c client_encoding=sql_ascii");
    }

  }

}
