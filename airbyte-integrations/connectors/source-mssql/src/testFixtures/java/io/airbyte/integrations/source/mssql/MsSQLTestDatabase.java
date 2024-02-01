/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.google.common.util.concurrent.Uninterruptibles;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.testutils.TestDatabase;
import io.debezium.connector.sqlserver.Lsn;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jooq.SQLDialect;
import org.jooq.exception.DataAccessException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.MSSQLServerContainer;

public class MsSQLTestDatabase extends TestDatabase<MSSQLServerContainer<?>, MsSQLTestDatabase, MsSQLTestDatabase.MsSQLConfigBuilder> {

  static private final Logger LOGGER = LoggerFactory.getLogger(MsSQLTestDatabase.class);

  static public final int MAX_RETRIES = 60;

  public enum BaseImage {

    MSSQL_2022("mcr.microsoft.com/mssql/server:2022-latest"),
    ;

    final String reference;

    BaseImage(final String reference) {
      this.reference = reference;
    }

  }

  static public MsSQLTestDatabase in(final BaseImage imageName) {
    final var container = new MsSQLContainerFactory().shared(imageName.reference);
    final var testdb = new MsSQLTestDatabase(container);
    return testdb.withConnectionProperty("encrypt", "false")
        .withConnectionProperty("databaseName", testdb.getDatabaseName())
        .withConnectionProperty("trustServerCertificate", "true")
        .initialized();
  }

  public MsSQLTestDatabase(final MSSQLServerContainer<?> container) {
    super(container);
    withConnectionProperty("encrypt", "false")
        .withConnectionProperty("databaseName", getDatabaseName())
        .withConnectionProperty("trustServerCertificate", "true");
  }

  protected void execSQL(String sql) {
    int tries = 1;
    while (tries < 10) {
      tries++;
      try {
        execSQL(Stream.of(sql));
        return;
      } catch (DataAccessException e) {
        if (!e.getMessage().contains("Cannot perform this operation while SQLServerAgent is starting") &&
            !e.getMessage().contains("Run the stored procedure 'sys.sp_cdc_add_job' to create the appropriate CDC capture or cleanup job.") &&
            !e.getMessage().contains("Use sys.sp_cdc_help_change_data_capture to verify the capture instance name and retry the operation") &&
            !e.getMessage().contains("refused because the job is already running from a request by") &&
            !e.getMessage().contains("Use the stored procedure 'sys.sp_cdc_add_job' to add the Change Data Capture job") &&
            !e.getMessage().contains("refused because the job already has a pending request from User")) {
          throw e;
        }
        LOGGER.info("SQLServerAgent was starting when executing query. try #" + tries + ". SQL was " + sql);
        Uninterruptibles.sleepUninterruptibly(1000, TimeUnit.MILLISECONDS);
      }
    }
  }

  protected void execSQL(Stream<String> sql) {
    var stmts = sql.toList();
    try {
      var r = this.getDatabase().query((ctx) -> {
        List<Integer> retVals = new ArrayList<>();
        for (var statement : stmts) {
          LOGGER.info("executing {}", statement);
          retVals.add(ctx.execute(statement));
        }
        return retVals;
      });
      if (!stmts.isEmpty()) {
        LOGGER.info("execSQL got " + r.get(0));
      }
    } catch (SQLException var3) {
      throw new RuntimeException(var3);
    }
  }

  public MsSQLTestDatabase with(String fmtSql, Object... fmtArgs) {
    this.execSQL(String.format(fmtSql, fmtArgs));
    return this.self();
  }

  public MsSQLTestDatabase withCdc() {
    return with("EXEC sys.sp_cdc_enable_db;");
  }

  public MsSQLTestDatabase withoutCdc() {
    return with("EXEC sys.sp_cdc_disable_db;");
  }

  public MsSQLTestDatabase withShortenedCapturePollingInterval() {
    return with("EXEC sys.sp_cdc_change_job @job_type = 'capture', @pollinginterval = %d;",
        MssqlCdcTargetPosition.MAX_LSN_QUERY_DELAY_TEST.toSeconds());
  }

  public MsSQLTestDatabase withCdcJobStarted() {
    return with("EXEC sys.sp_cdc_start_job;");
  }

  public MsSQLTestDatabase withWaitUntilMaxLsnAvailable() {
    LOGGER.info("Waiting for max LSN to become available for database {}.", getDatabaseName());
    for (int i = 0; i < MAX_RETRIES; i++) {
      try {
        final var maxLSN = query(ctx -> ctx.fetch("SELECT sys.fn_cdc_get_max_lsn();").get(0).get(0, byte[].class));
        if (maxLSN != null) {
          LOGGER.info("Max LSN available for database {}: {}", getDatabaseName(), Lsn.valueOf(maxLSN));
          return self();
        }
        LOGGER.info("Retrying, max LSN still not available for database {}.", getDatabaseName());
      } catch (final SQLException e) {
        LOGGER.warn("Retrying max LSN query after catching exception {}", e.getMessage());
      }
      try {
        Thread.sleep(1_000); // Wait one second between retries.
      } catch (final InterruptedException e) {
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
    return Stream.of("/opt/mssql-tools/bin/sqlcmd",
        "-U", getContainer().getUsername(),
        "-P", getContainer().getPassword(),
        "-Q", sql.collect(Collectors.joining("; ")),
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
            "trustServerCertificate", "false",
            "hostNameInCertificate", hostnameInCertificate));
      } else {
        return withSsl(Map.of("ssl_method", "encrypted_verify_certificate",
            "certificate", certificate));
      }
    }

  }

}
