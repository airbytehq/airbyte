/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.cdk.integrations.base.ssh.SshHelpers;
import io.airbyte.cdk.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.List;

public class CdcMssqlSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final String SCHEMA_NAME = "dbo";
  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME2 = "starships";
  private static final String CDC_ROLE_NAME = "cdc_selector";

  private MsSQLTestDatabase testdb;

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
    return testdb.integrationTestConfigBuilder()
        .withCdcReplication()
        .withoutSsl()
        .build();
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
    testdb = MsSQLTestDatabase.in("mcr.microsoft.com/mssql/server:2022-latest", "withAgent");
    testdb
        .withSnapshotIsolation()
        .withCdc()
        .with("REVOKE ALL FROM %s CASCADE;", testdb.getUserName())
        .with("EXEC sp_msforeachtable \"REVOKE ALL ON '?' TO %s;\"", testdb.getUserName());
    createAndPopulateTables();
    testdb
        .with("EXEC sp_addrolemember N'%s', N'%s';", "db_datareader", testdb.getUserName())
        .with("GRANT SELECT ON SCHEMA :: [cdc] TO %s", testdb.getUserName())
        .with("EXEC sp_addrolemember N'%s', N'%s';", CDC_ROLE_NAME, testdb.getUserName());
  }

  private void createAndPopulateTables() throws InterruptedException {
    testdb.with("CREATE TABLE %s.%s(id INTEGER PRIMARY KEY, name VARCHAR(200));", SCHEMA_NAME, STREAM_NAME);
    testdb.with("INSERT INTO %s.%s (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');", SCHEMA_NAME, STREAM_NAME);
    testdb.with("CREATE TABLE %s.%s(id INTEGER PRIMARY KEY, name VARCHAR(200));", SCHEMA_NAME, STREAM_NAME2);
    testdb.with("INSERT INTO %s.%s (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');", SCHEMA_NAME, STREAM_NAME2);

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
          testdb.with(
              "EXEC sys.sp_cdc_enable_table\n"
                  + "\t@source_schema = N'%s',\n"
                  + "\t@source_name   = N'%s', \n"
                  + "\t@role_name     = N'%s',\n"
                  + "\t@supports_net_changes = 0",
              SCHEMA_NAME, table, CDC_ROLE_NAME);
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

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    testdb.close();
  }

}
