/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.testutils.TestDatabase;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jooq.SQLDialect;
import org.testcontainers.containers.MSSQLServerContainer;

public class MsSQLTestDatabase extends TestDatabase<MSSQLServerContainer<?>, MsSQLTestDatabase, MsSQLTestDatabase.MsSQLConfigBuilder> {

  static public MsSQLTestDatabase in(String imageName, String... methods) {
    final var container = new MsSQLContainerFactory().shared(imageName, methods);
    final var testdb = new MsSQLTestDatabase(container);
    return testdb
        .withConnectionProperty("encrypt", "false")
        .withConnectionProperty("databaseName", testdb.getDatabaseName())
        .initialized();
  }

  public MsSQLTestDatabase(MSSQLServerContainer<?> container) {
    super(container);
  }

  public MsSQLTestDatabase withSnapshotIsolation() {
    return with("ALTER DATABASE %s SET ALLOW_SNAPSHOT_ISOLATION ON;", getDatabaseName());
  }

  public MsSQLTestDatabase withoutSnapshotIsolation() {
    return with("ALTER DATABASE %s SET ALLOW_SNAPSHOT_ISOLATION OFF;", getDatabaseName());
  }

  public MsSQLTestDatabase withCdc() {
    return with("EXEC sys.sp_cdc_enable_db;");
  }

  public MsSQLTestDatabase withoutCdc() {
    return with("EXEC sys.sp_cdc_disable_db;");
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

  @Override
  protected Stream<String> inContainerUndoBootstrapCmd() {
    return mssqlCmd(Stream.of(
        String.format("USE master"),
        String.format("ALTER DATABASE %s SET single_user WITH ROLLBACK IMMEDIATE", getDatabaseName()),
        String.format("DROP DATABASE %s", getDatabaseName())));
  }

  public Stream<String> mssqlCmd(Stream<String> sql) {
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

  @Override
  public MsSQLConfigBuilder configBuilder() {
    return new MsSQLConfigBuilder(this);
  }

  static public class MsSQLConfigBuilder extends ConfigBuilder<MsSQLTestDatabase, MsSQLConfigBuilder> {

    protected MsSQLConfigBuilder(MsSQLTestDatabase testDatabase) {
      super(testDatabase);
    }

    public MsSQLConfigBuilder withCdcReplication() {
      return with("replication_method", Map.of(
          "method", "CDC",
          "data_to_sync", "Existing and New",
          "initial_waiting_seconds", DEFAULT_CDC_REPLICATION_INITIAL_WAIT.getSeconds(),
          "snapshot_isolation", "Snapshot"));
    }

    public MsSQLConfigBuilder withSchemas(String... schemas) {
      return with(JdbcUtils.SCHEMAS_KEY, List.of(schemas));
    }

    @Override
    public MsSQLConfigBuilder withoutSsl() {
      return withSsl(Map.of("ssl_method", "unencrypted"));
    }

    @Override
    public MsSQLConfigBuilder withSsl(Map<Object, Object> sslMode) {
      return with("ssl_method", sslMode);
    }
  }
}
