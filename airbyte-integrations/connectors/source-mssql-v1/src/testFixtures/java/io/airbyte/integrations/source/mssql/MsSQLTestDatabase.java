/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static io.airbyte.integrations.source.mssql.MsSqlSpecConstants.INVALID_CDC_CURSOR_POSITION_PROPERTY;
import static io.airbyte.integrations.source.mssql.MsSqlSpecConstants.RESYNC_DATA_OPTION;

import com.google.common.collect.Sets;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.testutils.ContainerFactory.NamedContainerModifier;
import io.airbyte.cdk.testutils.TestDatabase;
import io.airbyte.integrations.source.mssql.cdc.MssqlDebeziumStateUtil;
import io.debezium.connector.sqlserver.Lsn;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jetbrains.annotations.NotNull;
import org.jooq.SQLDialect;
import org.jooq.exception.DataAccessException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.MSSQLServerContainer;

public class MsSQLTestDatabase extends TestDatabase<MSSQLServerContainer<?>, MsSQLTestDatabase, MsSQLTestDatabase.MsSQLConfigBuilder> {

  static private final Logger LOGGER = LoggerFactory.getLogger(MsSQLTestDatabase.class);

  // Turning this to true will create a bunch of background threads that will regularly check the
  // state of the database and log every time it changes. A bit verbose, but useful for debugging
  private static final boolean ENABLE_BACKGROUND_THREADS = false;

  // empirically, 240 is enough. If you fee like you need to increase it, you're probably mmissing a
  // check somewhere
  static public final int MAX_RETRIES = 240;

  public enum BaseImage {

    MSSQL_2022("mcr.microsoft.com/mssql/server:2022-latest"),
    ;

    public final String reference;

    BaseImage(final String reference) {
      this.reference = reference;
    }

  }

  public enum ContainerModifier implements NamedContainerModifier<MSSQLServerContainer<?>> {

    AGENT(MsSQLContainerFactory::withAgent),
    WITH_SSL_CERTIFICATES(MsSQLContainerFactory::withSslCertificates),
    ;

    public final Consumer<MSSQLServerContainer<?>> modifier;

    ContainerModifier(final Consumer<MSSQLServerContainer<?>> modifier) {
      this.modifier = modifier;
    }


    @NotNull
    @Override
    public Consumer<MSSQLServerContainer<?>> getModifier() {
      return this.modifier;
    }
  }

  static public MsSQLTestDatabase in(final BaseImage imageName, final ContainerModifier... modifiers) {
    final var container = new MsSQLContainerFactory().shared(imageName.reference, modifiers);
    final MsSQLTestDatabase testdb;
    if (ENABLE_BACKGROUND_THREADS) {
      testdb = new MsSqlTestDatabaseWithBackgroundThreads(container);
    } else {
      testdb = new MsSQLTestDatabase(container);
    }
    return testdb
        .withConnectionProperty("encrypt", "false")
        .withConnectionProperty("trustServerCertificate", "true")
        .withConnectionProperty("databaseName", testdb.getDatabaseName())
        .initialized();
  }

  public MsSQLTestDatabase(final MSSQLServerContainer<?> container) {
    super(container);
    LOGGER.info("creating new database. databaseId=" + this.databaseId + ", databaseName=" + getDatabaseName());
  }

  public MsSQLTestDatabase withCdc() {
    LOGGER.info("enabling CDC on database {} with id {}", getDatabaseName(), databaseId);
    with("EXEC sys.sp_cdc_enable_db;");
    LOGGER.info("CDC enabled on database {} with id {}", getDatabaseName(), databaseId);
    return this;
  }

  private static final String RETRYABLE_CDC_TABLE_ENABLEMENT_ERROR_CONTENT =
      "The error returned was 14258: 'Cannot perform this operation while SQLServerAgent is starting. Try again later.'";
  private static final String ENABLE_CDC_SQL_FMT = """
                                                   EXEC sys.sp_cdc_enable_table
                                                   \t@source_schema = N'%s',
                                                   \t@source_name   = N'%s',
                                                   \t@role_name     = %s,
                                                   \t@supports_net_changes = 0,
                                                   \t@capture_instance = N'%s'""";
  private final Set<String> CDC_INSTANCE_NAMES = Sets.newConcurrentHashSet();

  public MsSQLTestDatabase withCdcForTable(String schemaName, String tableName, String roleName) {
    return withCdcForTable(schemaName, tableName, roleName, "%s_%s".formatted(schemaName, tableName));
  }

  public MsSQLTestDatabase withCdcForTable(String schemaName, String tableName, String roleName, String instanceName) {
    LOGGER.info(formatLogLine("enabling CDC for table {}.{} and role {}, instance {}"), schemaName, tableName, roleName, instanceName);
    String sqlRoleName = roleName == null ? "NULL" : "N'%s'".formatted(roleName);
    for (int tryCount = 0; tryCount < MAX_RETRIES; tryCount++) {
      try {
        Thread.sleep(1_000);
        synchronized (getContainer()) {
          LOGGER.info(formatLogLine("Trying to enable CDC for table {}.{} and role {}, instance {}, try {}/{}"), schemaName, tableName, roleName,
              instanceName, tryCount, MAX_RETRIES);
          with(ENABLE_CDC_SQL_FMT.formatted(schemaName, tableName, sqlRoleName, instanceName));
        }
        CDC_INSTANCE_NAMES.add(instanceName);
        return withShortenedCapturePollingInterval();
      } catch (DataAccessException e) {
        if (!e.getMessage().contains(RETRYABLE_CDC_TABLE_ENABLEMENT_ERROR_CONTENT)) {
          throw e;
        }
        tryCount++;
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }
    }
    throw new RuntimeException(formatLogLine("failed to enable CDC for table %s.%s within %d seconds").formatted(schemaName, tableName, MAX_RETRIES));
  }

  private static final String DISABLE_CDC_SQL_FMT = """
                                                    EXEC sys.sp_cdc_disable_table
                                                    \t@source_schema = N'%s',
                                                    \t@source_name   = N'%s',
                                                    \t@capture_instance = N'%s'
                                                    """;

  public MsSQLTestDatabase withCdcDisabledForTable(String schemaName, String tableName, String instanceName) {
    LOGGER.info(formatLogLine("disabling CDC for table {}.{}, instance {}"), schemaName, tableName, instanceName);
    if (!CDC_INSTANCE_NAMES.remove(instanceName)) {
      throw new RuntimeException(formatLogLine("CDC was disabled for instance ") + instanceName);
    }
    synchronized (getContainer()) {
      return with(DISABLE_CDC_SQL_FMT.formatted(schemaName, tableName, instanceName));
    }
  }

  private static final String DISABLE_CDC_SQL = "EXEC sys.sp_cdc_disable_db;";

  public MsSQLTestDatabase withoutCdc() {
    CDC_INSTANCE_NAMES.clear();
    synchronized (getContainer()) {
      return with(DISABLE_CDC_SQL);
    }
  }

  public MsSQLTestDatabase withAgentStarted() {
    return with("EXEC master.dbo.xp_servicecontrol N'START', N'SQLServerAGENT';");
  }

  public MsSQLTestDatabase withAgentStopped() {
    return with("EXEC master.dbo.xp_servicecontrol N'STOP', N'SQLServerAGENT';");
  }

  public MsSQLTestDatabase withWaitUntilAgentRunning() {
    waitForAgentState(true);
    return self();
  }

  public MsSQLTestDatabase withWaitUntilAgentStopped() {
    waitForAgentState(false);
    return self();
  }

  public MsSQLTestDatabase waitForCdcRecords(String schemaName, String tableName, int recordCount) {
    return waitForCdcRecords(schemaName, tableName, "%s_%s".formatted(schemaName, tableName), recordCount);
  }

  public MsSQLTestDatabase waitForCdcRecords(String schemaName, String tableName, String cdcInstanceName, int recordCount) {
    if (!CDC_INSTANCE_NAMES.contains(cdcInstanceName)) {
      throw new RuntimeException("CDC is not enabled on instance %s".formatted(cdcInstanceName));
    }
    String sql = "SELECT count(*) FROM cdc.%s_ct".formatted(cdcInstanceName);
    int actualRecordCount = 0;
    for (int tryCount = 0; tryCount < MAX_RETRIES; tryCount++) {
      LOGGER.info(formatLogLine("fetching the number of CDC records for {}.{}, instance {}"), schemaName, tableName, cdcInstanceName);
      try {
        Thread.sleep(1_000);
        actualRecordCount = query(ctx -> ctx.fetch(sql)).get(0).get(0, Integer.class);
      } catch (SQLException | DataAccessException e) {
        actualRecordCount = 0;
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }
      LOGGER.info(formatLogLine("Found {} CDC records for {}.{} in instance {}. Expecting {}. Trying again ({}/{}"), actualRecordCount, schemaName,
          tableName, cdcInstanceName,
          recordCount, tryCount, MAX_RETRIES);
      if (actualRecordCount >= recordCount) {
        LOGGER.info(formatLogLine("found {} records after {} tries!"), actualRecordCount, tryCount);
        return self();
      }
    }
    throw new RuntimeException(formatLogLine(
        "failed to find %d records after %s seconds. Only found %d!").formatted(recordCount, MAX_RETRIES, actualRecordCount));
  }

  private boolean shortenedPollingIntervalEnabled = false;

  public MsSQLTestDatabase withShortenedCapturePollingInterval() {
    if (!shortenedPollingIntervalEnabled) {
      synchronized (getContainer()) {
        shortenedPollingIntervalEnabled = true;
        with("EXEC sys.sp_cdc_change_job @job_type = 'capture', @pollinginterval = 1;");
      }
    }
    return this;
  }

  private void waitForAgentState(final boolean running) {
    final String expectedValue = running ? "Running." : "Stopped.";
    LOGGER.info(formatLogLine("Waiting for SQLServerAgent state to change to '{}'."), expectedValue);
    for (int i = 0; i < MAX_RETRIES; i++) {
      try {
        Thread.sleep(1_000);
        final var r = query(ctx -> ctx.fetch("EXEC master.dbo.xp_servicecontrol 'QueryState', N'SQLServerAGENT';").get(0));
        if (expectedValue.equalsIgnoreCase(r.getValue(0).toString())) {
          LOGGER.info(formatLogLine("SQLServerAgent state is '{}', as expected."), expectedValue);
          return;
        }
        LOGGER.info(formatLogLine("Retrying, SQLServerAgent state {} does not match expected '{}'."), r, expectedValue);
      } catch (final SQLException e) {
        LOGGER.info(formatLogLine("Retrying agent state query after catching exception {}."), e.getMessage());
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }
    }
    throw new RuntimeException(formatLogLine("Exhausted retry attempts while polling for agent state"));
  }

  public static final String MAX_LSN_QUERY = "SELECT sys.fn_cdc_get_max_lsn();";

  public MsSQLTestDatabase withWaitUntilMaxLsnAvailable() {
    LOGGER.info(formatLogLine("Waiting for max LSN to become available for database {}."), getDatabaseName());
    for (int i = 0; i < MAX_RETRIES; i++) {
      try {
        Thread.sleep(1_000);
        final var maxLSN = query(ctx -> ctx.fetch(MAX_LSN_QUERY).get(0).get(0, byte[].class));
        if (maxLSN != null) {
          LOGGER.info(formatLogLine("Max LSN available for database {}: {}"), getDatabaseName(), Lsn.valueOf(maxLSN));
          return self();
        }
        LOGGER.info(formatLogLine("Retrying, max LSN still not available for database {}."), getDatabaseName());
      } catch (final SQLException e) {
        LOGGER.info(formatLogLine("Retrying max LSN query after catching exception {}"), e.getMessage());
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }
    }
    throw new RuntimeException("Exhausted retry attempts while polling for max LSN availability");
  }

  @Override
  public String getPassword() {
    return "S00p3rS33kr3tP4ssw0rd!";
  }

  @Override
  public String getJdbcUrl() {
    return String.format("jdbc:sqlserver://%s:%d", getContainer().getHost(), getContainer().getFirstMappedPort());
  }

  @Override
  protected Stream<Stream<String>> inContainerBootstrapCmd() {
    return Stream.of(
        mssqlCmd(Stream.of(String.format("CREATE DATABASE %s", getDatabaseName()))),
        mssqlCmd(Stream.of(
            String.format("USE %s", getDatabaseName()),
            String.format("CREATE LOGIN %s WITH PASSWORD = '%s', DEFAULT_DATABASE = %s", getUserName(), getPassword(), getDatabaseName()),
            String.format("ALTER SERVER ROLE [sysadmin] ADD MEMBER %s", getUserName()),
            String.format("CREATE USER %s FOR LOGIN %s WITH DEFAULT_SCHEMA = [dbo]", getUserName(), getUserName()),
            String.format("ALTER ROLE [db_owner] ADD MEMBER %s", getUserName()))));
  }

  /**
   * Don't drop anything when closing the test database. Instead, if cleanup is required, call
   * {@link #dropDatabaseAndUser()} explicitly. Implicit cleanups may result in deadlocks and so
   * aren't really worth it.
   */
  @Override
  protected Stream<String> inContainerUndoBootstrapCmd() {
    return Stream.empty();
  }

  public void dropDatabaseAndUser() {
    execInContainer(mssqlCmd(Stream.of(
        String.format("USE master"),
        String.format("ALTER DATABASE %s SET single_user WITH ROLLBACK IMMEDIATE", getDatabaseName()),
        String.format("DROP DATABASE %s", getDatabaseName()))));
  }

  public Stream<String> mssqlCmd(final Stream<String> sql) {
    return Stream.of("/opt/mssql-tools18/bin/sqlcmd",
        "-U", getContainer().getUsername(),
        "-P", getContainer().getPassword(),
        "-Q", sql.collect(Collectors.joining("; ")),
        "-b", "-e", "-C");
  }

  @Override
  public DatabaseDriver getDatabaseDriver() {
    return DatabaseDriver.MSSQLSERVER;
  }

  @Override
  public SQLDialect getSqlDialect() {
    return SQLDialect.DEFAULT;
  }

  public static enum CertificateKey {

    CA(true),
    DUMMY_CA(false),
    SERVER(true),
    DUMMY_SERVER(false),
    SERVER_DUMMY_CA(false),
    ;

    public final boolean isValid;

    CertificateKey(final boolean isValid) {
      this.isValid = isValid;
    }

  }

  private volatile Map<CertificateKey, String> cachedCerts = new ConcurrentHashMap<>();

  public String getCertificate(final CertificateKey certificateKey) {
    if (!cachedCerts.containsKey(certificateKey)) {
      final String certificate;
      try {
        final String command = "cat /tmp/certs/" + certificateKey.name().toLowerCase() + ".crt";
        certificate = getContainer().execInContainer("bash", "-c", command).getStdout().trim();
      } catch (final IOException e) {
        throw new UncheckedIOException(e);
      } catch (final InterruptedException e) {
        throw new RuntimeException(e);
      }
      synchronized (cachedCerts) {
        this.cachedCerts.put(certificateKey, certificate);
      }
    }
    return cachedCerts.get(certificateKey);
  }

  @Override
  public MsSQLConfigBuilder configBuilder() {
    return new MsSQLConfigBuilder(this);
  }

  static public class MsSQLConfigBuilder extends ConfigBuilder<MsSQLTestDatabase, MsSQLConfigBuilder> {

    protected MsSQLConfigBuilder(final MsSQLTestDatabase testDatabase) {

      super(testDatabase);
      with(JdbcUtils.JDBC_URL_PARAMS_KEY, "loginTimeout=2");

    }

    public MsSQLConfigBuilder withCdcReplication() {
      return with("is_test", true)
          .with("replication_method", Map.of(
              "method", "CDC",
              "initial_waiting_seconds", DEFAULT_CDC_REPLICATION_INITIAL_WAIT.getSeconds(),
              INVALID_CDC_CURSOR_POSITION_PROPERTY, RESYNC_DATA_OPTION));
    }

    public MsSQLConfigBuilder withSchemas(final String... schemas) {
      return with(JdbcUtils.SCHEMAS_KEY, List.of(schemas));
    }

    @Override
    public MsSQLConfigBuilder withoutSsl() {
      return withSsl(Map.of("ssl_method", "unencrypted"));
    }

    @Deprecated
    public MsSQLConfigBuilder withSsl(final Map<Object, Object> sslMode) {
      return with("ssl_method", sslMode);
    }

    public MsSQLConfigBuilder withEncrytedTrustServerCertificate() {
      return withSsl(Map.of("ssl_method", "encrypted_trust_server_certificate"));
    }

    public MsSQLConfigBuilder withEncrytedVerifyServerCertificate(final String certificate, final String hostnameInCertificate) {
      if (hostnameInCertificate != null) {
        return withSsl(Map.of("ssl_method", "encrypted_verify_certificate",
            "certificate", certificate,
            "hostNameInCertificate", hostnameInCertificate));
      } else {
        return withSsl(Map.of("ssl_method", "encrypted_verify_certificate",
            "certificate", certificate));
      }
    }

  }

  @Override
  public void close() {
    MssqlDebeziumStateUtil.disposeInitialState();
    super.close();
  }

}
