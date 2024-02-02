/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.testutils;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.ContextQueryFunction;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.JdbcConnector;
import io.airbyte.cdk.integrations.util.HostPortResolver;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.sql.SQLException;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.JdbcDatabaseContainer;

/**
 * TestDatabase provides a convenient pattern for interacting with databases when testing SQL
 * database sources. The basic idea is to share the same database testcontainer instance for all
 * tests and to use SQL constructs such as DATABASE and USER to isolate each test case's state.
 *
 * @param <C> the type of the backing testcontainer.
 * @param <T> itself
 * @param <B> the type of the object returned by {@link #configBuilder()}
 */
abstract public class TestDatabase<C extends JdbcDatabaseContainer<?>, T extends TestDatabase<C, T, B>, B extends TestDatabase.ConfigBuilder<T, B>>
    implements AutoCloseable {

  static private final Logger LOGGER = LoggerFactory.getLogger(TestDatabase.class);

  final private C container;
  final private String suffix;
  final private ArrayList<String> cleanupSQL = new ArrayList<>();
  final private Map<String, String> connectionProperties = new HashMap<>();

  private DataSource dataSource;
  private DSLContext dslContext;

  protected TestDatabase(C container) {
    this.container = container;
    this.suffix = Strings.addRandomSuffix("", "_", 10);
  }

  @SuppressWarnings("unchecked")
  protected T self() {
    return (T) this;
  }

  /**
   * Adds a key-value pair to the JDBC URL's query parameters.
   */
  public T withConnectionProperty(String key, String value) {
    if (isInitialized()) {
      throw new RuntimeException("TestDatabase instance is already initialized");
    }
    connectionProperties.put(key, value);
    return self();
  }

  /**
   * Enqueues a SQL statement to be executed when this object is closed.
   */
  public T onClose(String fmtSql, Object... fmtArgs) {
    cleanupSQL.add(String.format(fmtSql, fmtArgs));
    return self();
  }

  /**
   * Executes a SQL statement after calling String.format on the arguments.
   */
  public T with(String fmtSql, Object... fmtArgs) {
    execSQL(Stream.of(String.format(fmtSql, fmtArgs)));
    return self();
  }

  /**
   * Executes SQL statements as root to provide the necessary isolation for the lifetime of this
   * object. This typically entails at least a CREATE DATABASE and a CREATE USER. Also Initializes the
   * {@link DataSource} and {@link DSLContext} owned by this object.
   */
  final public T initialized() {
    inContainerBootstrapCmd().forEach(this::execInContainer);
    this.dataSource = DataSourceFactory.create(
        getUserName(),
        getPassword(),
        getDatabaseDriver().getDriverClassName(),
        getJdbcUrl(),
        connectionProperties,
        JdbcConnector.getConnectionTimeout(connectionProperties, getDatabaseDriver().getDriverClassName()));
    this.dslContext = DSLContextFactory.create(dataSource, getSqlDialect());
    return self();
  }

  final public boolean isInitialized() {
    return dslContext != null;
  }

  abstract protected Stream<Stream<String>> inContainerBootstrapCmd();

  abstract protected Stream<String> inContainerUndoBootstrapCmd();

  abstract public DatabaseDriver getDatabaseDriver();

  abstract public SQLDialect getSqlDialect();

  final public C getContainer() {
    return container;
  }

  public String withNamespace(String name) {
    return name + suffix;
  }

  public String getDatabaseName() {
    return withNamespace("db");
  }

  public String getUserName() {
    return withNamespace("user");
  }

  public String getPassword() {
    return "password";
  }

  public DataSource getDataSource() {
    if (!isInitialized()) {
      throw new RuntimeException("TestDatabase instance is not yet initialized");
    }
    return dataSource;
  }

  final public DSLContext getDslContext() {
    if (!isInitialized()) {
      throw new RuntimeException("TestDatabase instance is not yet initialized");
    }
    return dslContext;
  }

  public String getJdbcUrl() {
    return String.format(
        getDatabaseDriver().getUrlFormatString(),
        getContainer().getHost(),
        getContainer().getFirstMappedPort(),
        getDatabaseName());
  }

  public Database getDatabase() {
    return new Database(getDslContext());
  }

  protected void execSQL(final Stream<String> sql) {
    try {
      getDatabase().query(ctx -> {
        sql.forEach(statement -> {
          LOGGER.debug("{}", statement);
          ctx.execute(statement);
        });
        return null;
      });
    } catch (SQLException e) {
      throw new RuntimeException(e);
    }
  }

  protected void execInContainer(Stream<String> cmds) {
    final List<String> cmd = cmds.toList();
    if (cmd.isEmpty()) {
      return;
    }
    try {
      LOGGER.debug("executing {}", Strings.join(cmd, " "));
      final var exec = getContainer().execInContainer(cmd.toArray(new String[0]));
      if (exec.getExitCode() == 0) {
        LOGGER.debug("execution success\nstdout:\n{}\nstderr:\n{}", exec.getStdout(), exec.getStderr());
      } else {
        LOGGER.error("execution failure, code {}\nstdout:\n{}\nstderr:\n{}", exec.getExitCode(), exec.getStdout(), exec.getStderr());
      }
    } catch (IOException e) {
      throw new UncheckedIOException(e);
    } catch (InterruptedException e) {
      throw new RuntimeException(e);
    }
  }

  public <X> X query(final ContextQueryFunction<X> transform) throws SQLException {
    return getDatabase().query(transform);
  }

  public <X> X transaction(final ContextQueryFunction<X> transform) throws SQLException {
    return getDatabase().transaction(transform);
  }

  /**
   * Returns a builder for the connector config object.
   */
  public B configBuilder() {
    return new ConfigBuilder<T, B>(self()).self();
  }

  public B testConfigBuilder() {
    return configBuilder()
        .withHostAndPort()
        .withCredentials()
        .withDatabase();
  }

  public B integrationTestConfigBuilder() {
    return configBuilder()
        .withResolvedHostAndPort()
        .withCredentials()
        .withDatabase();
  }

  @Override
  public void close() {
    execSQL(this.cleanupSQL.stream());
    execInContainer(inContainerUndoBootstrapCmd());
  }

  static public class ConfigBuilder<T extends TestDatabase<?, ?, ?>, B extends ConfigBuilder<T, B>> {

    static public final Duration DEFAULT_CDC_REPLICATION_INITIAL_WAIT = Duration.ofSeconds(5);

    protected final ImmutableMap.Builder<Object, Object> builder = ImmutableMap.builder();
    protected final T testDatabase;

    protected ConfigBuilder(T testDatabase) {
      this.testDatabase = testDatabase;
    }

    public JsonNode build() {
      return Jsons.jsonNode(builder.build());
    }

    @SuppressWarnings("unchecked")
    final protected B self() {
      return (B) this;
    }

    public B with(Object key, Object value) {
      builder.put(key, value);
      return self();
    }

    public B withDatabase() {
      return this
          .with(JdbcUtils.DATABASE_KEY, testDatabase.getDatabaseName());
    }

    public B withCredentials() {
      return this
          .with(JdbcUtils.USERNAME_KEY, testDatabase.getUserName())
          .with(JdbcUtils.PASSWORD_KEY, testDatabase.getPassword());
    }

    public B withResolvedHostAndPort() {
      return this
          .with(JdbcUtils.HOST_KEY, HostPortResolver.resolveHost(testDatabase.getContainer()))
          .with(JdbcUtils.PORT_KEY, HostPortResolver.resolvePort(testDatabase.getContainer()));
    }

    public B withHostAndPort() {
      return this
          .with(JdbcUtils.HOST_KEY, testDatabase.getContainer().getHost())
          .with(JdbcUtils.PORT_KEY, testDatabase.getContainer().getFirstMappedPort());
    }

    public B withoutSsl() {
      return with(JdbcUtils.SSL_KEY, false);
    }

    public B withSsl(Map<Object, Object> sslMode) {
      return with(JdbcUtils.SSL_KEY, true).with(JdbcUtils.SSL_MODE_KEY, sslMode);
    }

  }

}
