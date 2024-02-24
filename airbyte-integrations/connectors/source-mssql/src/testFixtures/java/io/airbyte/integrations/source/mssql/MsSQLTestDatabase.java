/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.testutils.TestDatabase;
import io.debezium.connector.sqlserver.Lsn;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;
import org.apache.commons.lang3.StringUtils;
import org.jooq.Record;
import org.jooq.Result;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.MSSQLServerContainer;

public class MsSQLTestDatabase extends TestDatabase<MSSQLServerContainer<?>, MsSQLTestDatabase, MsSQLTestDatabase.MsSQLConfigBuilder> {

  static private final Logger LOGGER = LoggerFactory.getLogger(MsSQLTestDatabase.class);

  static public final int MAX_RETRIES = 60;

  public enum BaseImage {

    MSSQL_2022("mcr.microsoft.com/mssql/server:2022-latest"),
    MSSQL_2017("mcr.microsoft.com/mssql/server:2017-latest"),
    ;

    public final String reference;

    BaseImage(final String reference) {
      this.reference = reference;
    }

  }

  public enum ContainerModifier {

    NETWORK("withNetwork"),
    AGENT("withAgent"),
    WITH_SSL_CERTIFICATES("withSslCertificates"),
    ;

    public final String methodName;

    ContainerModifier(final String methodName) {
      this.methodName = methodName;
    }

  }

  static public MsSQLTestDatabase in(final BaseImage imageName, final ContainerModifier... methods) {
    final String[] methodNames = Stream.of(methods).map(im -> im.methodName).toList().toArray(new String[0]);
    final var container = new MsSQLContainerFactory().shared(imageName.reference, methodNames);
    final var testdb = new MsSQLTestDatabase(container);
    return testdb
        .withConnectionProperty("encrypt", "false")
        .withConnectionProperty("databaseName", testdb.getDatabaseName())
        .initialized();
  }

  private abstract class AbstractMssqlTestDatabaseBackgroundThread extends Thread {

    protected volatile boolean stop = false;
    protected Logger LOGGER = LoggerFactory.getLogger(this.getClass());

    protected String formatLogLine(String logLine) {
      String retVal = "SGX " + this.getClass().getSimpleName() + " databaseId=" + databaseId + ", containerId=" + containerId + " - " + logLine;
      return retVal;
    }

    public void run() {
      while (!stop) {
        try {
          innerRun();
          sleep(100);
        } catch (final Throwable t) {
          // String exceptionAsString = StringUtils.join(ExceptionUtils.getStackFrames(t), "\n ");
          LOGGER.info(formatLogLine("got exception " + StringUtils.replace(t.getMessage(), "\n", "\\n")));
        }
      }
    }

    public abstract void innerRun() throws Exception;

  }

  private class MssqlTestDatabaseBackgroundThreadAgentState extends AbstractMssqlTestDatabaseBackgroundThread {

    @Override
    public void innerRun() throws Exception {
      String agentStateSql = "EXEC master.dbo.xp_servicecontrol 'QueryState', N'SQLServerAGENT';";
      LOGGER.info(formatLogLine("executing agentStateSql {}"), agentStateSql);
      final var r = query(ctx -> ctx.fetch(agentStateSql).get(0));
      String agentState = r.getValue(0).toString();
      LOGGER.info(formatLogLine("agentState=" + agentState));
    }

  }

  private class MssqlTestDatabaseBackgroundThreadFnCdcGetMaxLsn extends AbstractMssqlTestDatabaseBackgroundThread {

    @Override
    public void innerRun() throws Exception {
      LOGGER.info(formatLogLine("querying fn_cdc_get_max_lsn"));
      LOGGER.info(formatLogLine(String.format("sys.fn_cdc_get_max_lsn returned %s",
          query(ctx -> ctx.fetch("SELECT sys.fn_cdc_get_max_lsn() AS max_lsn;")).get(0)
              .getValue(0))));
    }

  }

  private class MssqlTestDatabaseBackgroundThreadLsnTimeMapping extends AbstractMssqlTestDatabaseBackgroundThread {

    @Override
    public void innerRun() throws Exception {
      LOGGER.info(formatLogLine("querying lsn_time_mapping"));
      Result<Record> results = query(ctx -> ctx.fetch(
          "SELECT start_lsn, tran_begin_time, tran_end_time, tran_id FROM cdc.lsn_time_mapping;"));
      LOGGER.info(formatLogLine(
          String.format("lsn_time_mapping has %d rows: %s", results.size(),
              results.toString())));
    }

  }

  private class MssqlTestDatabaseBackgroundThreadEnableInternalTable extends AbstractMssqlTestDatabaseBackgroundThread {

    @Override
    public void innerRun() throws Exception {
      LOGGER.info(formatLogLine("enabling CDC for internal table"));
      withCdcForTable(getInternalSchemaName(),
          getInternalTableName(), null);
      stop = true;
      LOGGER.info(formatLogLine("enabled CDC for internal table"));
    }

  }

  private class MssqlTestDatabaseBackgroundThreadQueryChangeTables extends AbstractMssqlTestDatabaseBackgroundThread {

    @Override
    public void innerRun() throws Exception {
      LOGGER.info(formatLogLine("querying cdc.change_tables"));
      Result<Record> results = query(ctx -> ctx.fetch("""
                                                      SELECT OBJECT_SCHEMA_NAME(source_object_id, DB_ID('%s')),
                                                      OBJECT_NAME(source_object_id, DB_ID('%s')),
                                                      capture_instance,
                                                      object_id,
                                                      start_lsn FROM cdc.change_tables""".formatted(getDatabaseName(), getDatabaseName())));
      LOGGER.info(formatLogLine(
          String.format("change_tables has %d rows: %s", results.size(),
              results.toString())));
    }

  }

  private class MssqlTestDatabaseBackgroundThreadQueryInternalTable extends AbstractMssqlTestDatabaseBackgroundThread {

    @Override
    public void innerRun() throws Exception {
      LOGGER.info(formatLogLine("querying internal table"));
      Result<Record> results = query(ctx -> ctx.fetch("SELECT* FROM %s.%s".formatted(getInternalSchemaName(), getInternalTableName())));
      LOGGER.info(formatLogLine(
          String.format("internal table has %d rows: %s", results.size(),
              results.toString())));
    }

  }

  private final AbstractMssqlTestDatabaseBackgroundThread bgThreads[];

  public MsSQLTestDatabase(final MSSQLServerContainer<?> container) {
    super(container);
    bgThreads = new AbstractMssqlTestDatabaseBackgroundThread[] {};
    LOGGER.info("SGX creating new database. databaseId=" + this.databaseId + ", databaseName=" + getDatabaseName());
  }

  @Override
  public void initializedPostHook() {
    for (var bgThread : bgThreads) {
      bgThread.start();
    }
  }

  public MsSQLTestDatabase withCdc() {
    LOGGER.info("enabling CDC on database {} with id {}", getDatabaseName(), databaseId);
    with("EXEC sys.sp_cdc_enable_db;");
    LOGGER.info("CDC enabled on database {} with id {}", getDatabaseName(), databaseId);
    return this;
  }

  public synchronized MsSQLTestDatabase withCdcForTable(String schemaName, String tableName, String roleName) {
    final var enableCdcSqlFmt = """
                                EXEC sys.sp_cdc_enable_table
                                \t@source_schema = N'%s',
                                \t@source_name   = N'%s',
                                \t@role_name     = %s,
                                \t@supports_net_changes = 0""";
    String sqlRoleName = roleName == null ? "NULL" : "N'%s'".formatted(roleName);
    Instant startTime = Instant.now();
    Instant timeout = startTime.plusSeconds(300);
    while (timeout.isAfter(Instant.now())) {
      try {
        getDslContext().execute(enableCdcSqlFmt.formatted(schemaName, tableName, sqlRoleName));
        return this;
      } catch (Exception e) {
        if (!e.getMessage().contains("The error returned was 14258: 'Cannot perform this operation while SQLServerAgent is starting.")) {
          throw new RuntimeException(e);
        }
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
      try {
        Thread.sleep(1_000); // Wait one second between retries.
      } catch (final InterruptedException e) {
        throw new RuntimeException(e);
      }
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
      try {
        Thread.sleep(1_000); // Wait one second between retries.
      } catch (final InterruptedException e) {
        throw new RuntimeException(e);
      }
    }
    throw new RuntimeException("Exhausted retry attempts while polling for max LSN availability");
  }

  public void waitForCdcRecords(String schemaName, String tableName, int recordCount)
      throws SQLException {
    int maxTimeoutSec = 60;
    String sql = "SELECT count(*) FROM cdc.%s_%s_ct".formatted(schemaName, tableName);
    int actualRecordCount;
    Instant startTime = Instant.now();
    Instant maxTime = startTime.plusSeconds(maxTimeoutSec);
    do {
      LOGGER.info("fetching the number of CDC records for {}.{}", schemaName, tableName);
      actualRecordCount = query(ctx -> ctx.fetch(sql)).get(0).get(0, Integer.class);
      LOGGER.info("Found {} CDC records for {}.{}. Expecting {}. Trying again", actualRecordCount, schemaName, tableName, recordCount);
    } while (actualRecordCount < recordCount && maxTime.isAfter(Instant.now()));
    if (actualRecordCount >= recordCount) {
      LOGGER.info("found {} records!", actualRecordCount);
    } else {
      throw new RuntimeException(
          "failed to find %d records after %s seconds. Only found %d!".formatted(recordCount, maxTimeoutSec, actualRecordCount));
    }
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
  protected List<List<String>> inContainerBootstrapCmd() {
    return List.of(
        mssqlCmdInMasterDb(List.of(String.format("CREATE DATABASE %s", getDatabaseName()))),
        mssqlCmdInMasterDb(List.of(
            String.format("USE %s", getDatabaseName()),
            String.format("CREATE LOGIN %s WITH PASSWORD = '%s', DEFAULT_DATABASE = %s", getUserName(), getPassword(), getDatabaseName()),
            String.format("ALTER SERVER ROLE [sysadmin] ADD MEMBER %s", getUserName()),
            String.format("CREATE USER %s FOR LOGIN %s WITH DEFAULT_SCHEMA = [dbo]", getUserName(), getUserName()),
            String.format("ALTER ROLE [db_owner] ADD MEMBER %s", getUserName()))),
        mssqlCmd(List.of(String.format("CREATE SCHEMA %s", getInternalSchemaName()))),
        mssqlCmd(List.of(String.format("CREATE TABLE %s.%s (id INTEGER PRIMARY KEY)", getInternalSchemaName(), getInternalTableName()))),
        mssqlCmd(List.of(String.format("GRANT ALL ON SCHEMA :: %s TO PUBLIC", getInternalSchemaName()))),
        mssqlCmd(List.of(String.format("GRANT ALL ON %s.%s TO PUBLIC", getInternalSchemaName(), getInternalTableName()))));

  }

  /**
   * Don't drop anything when closing the test database. Instead, if cleanup is required, call
   * {@link #dropDatabaseAndUser()} explicitly. Implicit cleanups may result in deadlocks and so
   * aren't really worth it.
   */
  @Override
  protected List<String> inContainerUndoBootstrapCmd() {
    return Collections.emptyList();
  }

  public void dropDatabaseAndUser() {
    execInContainer(mssqlCmdInMasterDb(List.of(
        String.format("USE master"),
        String.format("ALTER DATABASE %s SET single_user WITH ROLLBACK IMMEDIATE", getDatabaseName()),
        String.format("DROP DATABASE %s", getDatabaseName()))));
  }

  public List<String> mssqlCmdInMasterDb(final List<String> sql) {
    return Arrays.asList("/opt/mssql-tools/bin/sqlcmd",
        "-U", getContainer().getUsername(),
        "-P", getContainer().getPassword(),
        "-Q", StringUtils.join(sql, "; "),
        "-d", "master",
        "-b", "-e");
  }

  public List<String> mssqlCmd(final List<String> sql) {
    return Arrays.asList("/opt/mssql-tools/bin/sqlcmd",
        "-U", getUserName(),
        "-P", getPassword(),
        "-Q", StringUtils.join(sql, "; "),
        "-b", "-e");
  }

  @Override
  public DatabaseDriver getDatabaseDriver() {
    return DatabaseDriver.MSSQLSERVER;
  }

  @Override
  public SQLDialect getSqlDialect() {
    return SQLDialect.DEFAULT;
  }

  private String getInternalTableName() {
    return withNamespace("internal_table_");
  }

  private String getInternalSchemaName() {
    return withNamespace("internal_schema_");
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

  public void close() {
    for (var bgThread : bgThreads) {
      bgThread.stop = true;
    }
    super.close();
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
