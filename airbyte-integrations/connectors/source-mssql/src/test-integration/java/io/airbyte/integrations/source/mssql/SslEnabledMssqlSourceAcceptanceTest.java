/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.BaseImage;

public class SslEnabledMssqlSourceAcceptanceTest extends MssqlSourceAcceptanceTest {

  @Override
  protected JsonNode getConfig() {
    return testdb.integrationTestConfigBuilder()
        .withEncrytedTrustServerCertificate()
        .build();
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) {
    final var container = new MsSQLContainerFactory().shared(BaseImage.MSSQL_2022.reference);
    testdb = new MsSQLTestDatabase(container);
    testdb = testdb
        .withConnectionProperty("encrypt", "true")
        .withConnectionProperty("trustServerCertificate", "true")
        .withConnectionProperty("databaseName", testdb.getDatabaseName())
        .initialized()
        .with("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200), born DATETIMEOFFSET(7));")
        .with("CREATE TABLE %s.%s(id INTEGER PRIMARY KEY, name VARCHAR(200));", SCHEMA_NAME, STREAM_NAME2)
        .with("INSERT INTO id_and_name (id, name, born) VALUES " +
            "(1, 'picard', '2124-03-04T01:01:01Z'), " +
            "(2, 'crusher', '2124-03-04T01:01:01Z'), " +
            "(3, 'vash', '2124-03-04T01:01:01Z');")
        .with("INSERT INTO %s.%s (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato'), (4, 'Argo');", SCHEMA_NAME, STREAM_NAME2)
        .with("CREATE TABLE %s.%s (id INTEGER PRIMARY KEY, name VARCHAR(200), userid INTEGER DEFAULT NULL);", SCHEMA_NAME, STREAM_NAME3)
        .with("INSERT INTO %s.%s (id, name) VALUES (4,'voyager');", SCHEMA_NAME, STREAM_NAME3);

  }

}
