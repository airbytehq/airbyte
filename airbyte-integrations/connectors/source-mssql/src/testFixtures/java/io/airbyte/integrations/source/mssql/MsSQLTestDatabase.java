/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.google.common.util.concurrent.Uninterruptibles;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.testutils.ContainerFactory.NamedContainerModifier;
import io.airbyte.cdk.testutils.TestDatabase;
import io.debezium.connector.sqlserver.Lsn;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.MSSQLServerContainer;

public class MsSQLTestDatabase extends TestDatabase<MSSQLServerContainer<?>, MsSQLTestDatabase, MsSQLTestDatabase.MsSQLConfigBuilder> {

  static private final Logger LOGGER = LoggerFactory.getLogger(MsSQLTestDatabase.class);

  static public final int MAX_RETRIES = 300;

  public enum BaseImage {

    MSSQL_2022("mcr.microsoft.com/mssql/server:2022-latest"),
    MSSQL_2017("mcr.microsoft.com/mssql/server:2017-latest"),
    ;

    public final String reference;

    BaseImage(final String reference) {
      this.reference = reference;
    }

  }

  public enum ContainerModifier implements NamedContainerModifier<MSSQLServerContainer<?>> {

    NETWORK(MsSQLContainerFactory::withNetwork),
    AGENT(MsSQLContainerFactory::withAgent),
    WITH_SSL_CERTIFICATES(MsSQLContainerFactory::withSslCertificates, MsSQLTestDatabase::initWithSsl),
    ;

    private final Consumer<MsSQLTestDatabase> databaseModifier;
    private Consumer<MSSQLServerContainer<?>> containerModifier;
    ContainerModifier(Consumer<MSSQLServerContainer<?>> containerModifier) {
      this(containerModifier, null);
    }

    ContainerModifier(Consumer<MSSQLServerContainer<?>> containerModifier, Consumer<MsSQLTestDatabase> databaseModifier) {
      this.databaseModifier = databaseModifier;
      this.containerModifier = containerModifier;
    }

    public Consumer<MSSQLServerContainer<?>> modifier() {
      return containerModifier;
    }
  }

  static public MsSQLTestDatabase in(final BaseImage imageName, final ContainerModifier... methods) {
    final var container = new MsSQLContainerFactory().shared(imageName.reference, methods);
    final var testdb = new MsSQLTestDatabase(container);
    testdb.withConnectionProperty("encrypt", "false")
        .withConnectionProperty("databaseName", testdb.getDatabaseName());
    for (ContainerModifier modifier : methods) {
      if (modifier.databaseModifier != null) {
        modifier.databaseModifier.accept(testdb);
      }
    }
    return testdb.initialized();
  }

  public MsSQLTestDatabase(final MSSQLServerContainer<?> container) {
    super(container);
    LOGGER.info("creating new database. databaseId=" + this.databaseId + ", databaseName=" + getDatabaseName());
  }

  private void initWithSsl() {
    withConnectionProperty("encrypt", "true");
    withConnectionProperty("databaseName", getDatabaseName());
    withConnectionProperty("trustServerCertificate", "true");
  }

  public MsSQLTestDatabase withCdc() {
    return with("EXEC sys.sp_cdc_enable_db;");
  }

  public MsSQLTestDatabase withCdcForTable(String schemaName, String tableName, String roleName) {
    String captureInstanceName = "%s_%s".formatted(schemaName, tableName);
    return withCdcForTable(schemaName, tableName, roleName, captureInstanceName);
  }

  public MsSQLTestDatabase withCdcForTable(String schemaName, String tableName, String roleName, String captureInstanceName) {
    final var enableCdcSqlFmt = """
                                EXEC sys.sp_cdc_enable_table
                                \t@source_schema = N'%s',
                                \t@source_name   = N'%s',
                                \t@role_name     = %s,
                                \t@supports_net_changes = 0,
                                \t@capture_instance = N'%s'""";
    String sqlRoleName = roleName == null ? "NULL" : "N'%s'".formatted(roleName);

    for (int i = 0; i < MAX_RETRIES; i++) {
      try {
        synchronized (getContainer()) {
          getDslContext().execute(
              enableCdcSqlFmt.formatted(schemaName, tableName, sqlRoleName, captureInstanceName));
        }
        return this;
      } catch (Exception e) {
        if (!e.getMessage().contains("The error returned was 14258: 'Cannot perform this operation while SQLServerAgent is starting.")) {
          throw new RuntimeException(e);
        }
        Uninterruptibles.sleepUninterruptibly(1, TimeUnit.SECONDS);
      }
    }
    throw new RuntimeException("Couldn't enable CDC for table %s.%s".formatted(schemaName, tableName));
  }

  public MsSQLTestDatabase withoutCdc() {
    return with("EXEC sys.sp_cdc_disable_db;");
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

  public MsSQLTestDatabase withShortenedCapturePollingInterval() {
    return with("EXEC sys.sp_cdc_change_job @job_type = 'capture', @pollinginterval = 1;");
  }

  private void waitForAgentState(final boolean running) {
    final String expectedValue = running ? "Running." : "Stopped.";
    LOGGER.info(formatLogLine("Waiting for SQLServerAgent state to change to '{}'."), expectedValue);
    for (int i = 0; i < MAX_RETRIES; i++) {
      try {
        final var r = query(ctx -> ctx.fetch("EXEC master.dbo.xp_servicecontrol 'QueryState', N'SQLServerAGENT';").get(0));
        if (expectedValue.equalsIgnoreCase(r.getValue(0).toString())) {
          LOGGER.info(formatLogLine("SQLServerAgent state is '{}', as expected."), expectedValue);
          return;
        }
        LOGGER.info(formatLogLine("Retrying, SQLServerAgent state {} does not match expected '{}'."), r, expectedValue);
      } catch (final SQLException e) {
        LOGGER.info(formatLogLine("Retrying agent state query after catching exception {}."), e.getMessage());
      }
      Uninterruptibles.sleepUninterruptibly(1, TimeUnit.SECONDS);
    }
    throw new RuntimeException(formatLogLine("Exhausted retry attempts while polling for agent state"));
  }

  public MsSQLTestDatabase withWaitUntilMaxLsnAvailable() {
    LOGGER.info(formatLogLine("Waiting for max LSN to become available for database {}."), getDatabaseName());
    for (int i = 0; i < MAX_RETRIES; i++) {
      try {
        final var maxLSN = query(ctx -> ctx.fetch("SELECT sys.fn_cdc_get_max_lsn();").get(0).get(0, byte[].class));
        if (maxLSN != null) {
          LOGGER.info(formatLogLine("Max LSN available for database {}: {}"), getDatabaseName(), Lsn.valueOf(maxLSN));
          return self();
        }
        LOGGER.info(formatLogLine("Retrying, max LSN still not available for database {}."), getDatabaseName());
      } catch (final SQLException e) {
        LOGGER.info(formatLogLine("Retrying max LSN query after catching exception {}"), e.getMessage());
      }
      Uninterruptibles.sleepUninterruptibly(1, TimeUnit.SECONDS);
    }
    throw new RuntimeException("Exhausted retry attempts while polling for max LSN availability");
  }

  public void waitForCdcRecords(String schemaName, String tableName, int recordCount)
      throws SQLException {
    String sql = "SELECT count(*) FROM cdc.%s_%s_ct".formatted(schemaName, tableName);
    int actualRecordCount = 0;
    for (int i = 0; i < MAX_RETRIES; i++) {
      LOGGER.info("fetching the number of CDC records for {}.{}", schemaName, tableName);
      actualRecordCount = query(ctx -> ctx.fetch(sql)).get(0).get(0, Integer.class);
      if (actualRecordCount >= recordCount) {
        LOGGER.info("found {} records!", actualRecordCount);
        return;
      }
      LOGGER.info("Found {} CDC records for {}.{}. Expecting {}. Trying again", actualRecordCount,
          schemaName, tableName, recordCount);
      Uninterruptibles.sleepUninterruptibly(1, TimeUnit.SECONDS);
    }
    throw new RuntimeException(
        "failed to find %d records after %s seconds. Only found %d!".formatted(recordCount, MAX_RETRIES, actualRecordCount));
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
    return Stream.of("/opt/mssql-tools/bin/sqlcmd",
        "-U", getContainer().getUsername(),
        "-P", getContainer().getPassword(),
        "-Q", sql.collect(Collectors.joining("; ")),
        "-b", "-e");
  }

  @Override
  public DatabaseDriver getDatabaseDriver() {
    return MssqlSource.driver;
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

  private Map<CertificateKey, String> cachedCerts;

  public synchronized String getCertificate(final CertificateKey certificateKey) {
    if (cachedCerts == null) {
      final Map<CertificateKey, String> cachedCerts = new HashMap<>();
      try {
        for (final CertificateKey key : CertificateKey.values()) {
          final String command = "cat /tmp/certs/" + key.name().toLowerCase() + ".crt";
          final String certificate = getContainer().execInContainer("bash", "-c", command).getStdout().trim();
          cachedCerts.put(key, certificate);
        }
      } catch (final IOException e) {
        throw new UncheckedIOException(e);
      } catch (final InterruptedException e) {
        throw new RuntimeException(e);
      }
      this.cachedCerts = cachedCerts;
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
              "initial_waiting_seconds", DEFAULT_CDC_REPLICATION_INITIAL_WAIT.getSeconds()));
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

}
