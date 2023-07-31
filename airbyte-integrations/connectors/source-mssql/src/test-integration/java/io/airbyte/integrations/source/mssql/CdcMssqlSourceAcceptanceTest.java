/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.ssh.SshHelpers;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.List;
import java.util.Map;
import org.jooq.DSLContext;
import org.junit.jupiter.api.AfterAll;
import org.testcontainers.containers.MSSQLServerContainer;

public class CdcMssqlSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final String SCHEMA_NAME = "dbo";
  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME2 = "starships";
  private static final String TEST_USER_PASSWORD = "testerjester[1]";
  private static final String CDC_ROLE_NAME = "cdc_selector";
  public static MSSQLServerContainer<?> container;
  private String dbName;
  private String testUserName;
  private JsonNode config;
  private Database database;
  private DSLContext dslContext;

  @AfterAll
  public static void closeContainer() {
    if (container != null) {
      container.close();
      container.stop();
    }
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-mssql:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return SshHelpers.getSpecAndInjectSsh();
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                String.format("%s", STREAM_NAME),
                String.format("%s", SCHEMA_NAME),
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSourceDefinedCursor(true)
                .withSourceDefinedPrimaryKey(List.of(List.of("id")))
                .withSupportedSyncModes(
                    Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                String.format("%s", STREAM_NAME2),
                String.format("%s", SCHEMA_NAME),
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSourceDefinedCursor(true)
                .withSourceDefinedPrimaryKey(List.of(List.of("id")))
                .withSupportedSyncModes(
                    Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))));
  }

  @Override
  protected JsonNode getState() {
    return null;
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws InterruptedException {
    if (container == null) {
      container = new MSSQLServerContainer<>("mcr.microsoft.com/mssql/server:2019-latest").acceptLicense();
      container.addEnv("MSSQL_AGENT_ENABLED", "True"); // need this running for cdc to work
      container.start();
    }

    dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();
    testUserName = Strings.addRandomSuffix("test", "_", 5).toLowerCase();

    final JsonNode replicationConfig = Jsons.jsonNode(Map.of(
        "method", "CDC",
        "data_to_sync", "Existing and New",
        "initial_waiting_seconds", 5,
        "snapshot_isolation", "Snapshot"));

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, container.getHost())
        .put(JdbcUtils.PORT_KEY, container.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, dbName)
        .put(JdbcUtils.USERNAME_KEY, testUserName)
        .put(JdbcUtils.PASSWORD_KEY, TEST_USER_PASSWORD)
        .put("replication_method", replicationConfig)
        .put("ssl_method", Jsons.jsonNode(Map.of("ssl_method", "unencrypted")))
        .build());

    dslContext = DSLContextFactory.create(DataSourceFactory.create(
        container.getUsername(),
        container.getPassword(),
        container.getDriverClassName(),
        String.format("jdbc:sqlserver://%s:%d;",
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt()),
        Map.of("encrypt", "false")), null);
    database = new Database(dslContext);

    executeQuery("CREATE DATABASE " + dbName + ";");
    executeQuery("ALTER DATABASE " + dbName + "\n\tSET ALLOW_SNAPSHOT_ISOLATION ON");
    executeQuery("USE " + dbName + "\n" + "EXEC sys.sp_cdc_enable_db");

    setupTestUser();
    revokeAllPermissions();
    createAndPopulateTables();
    grantCorrectPermissions();
  }

  private void setupTestUser() {
    executeQuery("USE " + dbName);
    executeQuery("CREATE LOGIN " + testUserName + " WITH PASSWORD = '" + TEST_USER_PASSWORD + "';");
    executeQuery("CREATE USER " + testUserName + " FOR LOGIN " + testUserName + ";");
  }

  private void revokeAllPermissions() {
    executeQuery("REVOKE ALL FROM " + testUserName + " CASCADE;");
    executeQuery("EXEC sp_msforeachtable \"REVOKE ALL ON '?' TO " + testUserName + ";\"");
  }

  private void createAndPopulateTables() throws InterruptedException {
    executeQuery(String.format("CREATE TABLE %s.%s(id INTEGER PRIMARY KEY, name VARCHAR(200));",
        SCHEMA_NAME, STREAM_NAME));
    executeQuery(String.format("INSERT INTO %s.%s (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');",
        SCHEMA_NAME, STREAM_NAME));
    executeQuery(String.format("CREATE TABLE %s.%s(id INTEGER PRIMARY KEY, name VARCHAR(200));",
        SCHEMA_NAME, STREAM_NAME2));
    executeQuery(String.format("INSERT INTO %s.%s (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');",
        SCHEMA_NAME, STREAM_NAME2));

    // sometimes seeing an error that we can't enable cdc on a table while sql server agent is still
    // spinning up
    // solving with a simple while retry loop
    boolean failingToStart = true;
    int retryNum = 0;
    final int maxRetries = 10;
    while (failingToStart) {
      try {
        // enabling CDC on each table
        final String[] tables = {STREAM_NAME, STREAM_NAME2};
        for (final String table : tables) {
          executeQuery(String.format(
              "EXEC sys.sp_cdc_enable_table\n"
                  + "\t@source_schema = N'%s',\n"
                  + "\t@source_name   = N'%s', \n"
                  + "\t@role_name     = N'%s',\n"
                  + "\t@supports_net_changes = 0",
              SCHEMA_NAME, table, CDC_ROLE_NAME));
        }
        failingToStart = false;
      } catch (final Exception e) {
        if (retryNum >= maxRetries) {
          throw e;
        } else {
          retryNum++;
          Thread.sleep(10000); // 10 seconds
        }
      }
    }
  }

  private void grantCorrectPermissions() {
    executeQuery(String.format("EXEC sp_addrolemember N'%s', N'%s';", "db_datareader", testUserName));
    executeQuery(String.format("USE %s;\n" + "GRANT SELECT ON SCHEMA :: [%s] TO %s", dbName, "cdc", testUserName));
    executeQuery(String.format("EXEC sp_addrolemember N'%s', N'%s';", CDC_ROLE_NAME, testUserName));
  }

  private void executeQuery(final String query) {
    try {
      database.query(
          ctx -> ctx
              .execute(query));
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    dslContext.close();
  }

}
