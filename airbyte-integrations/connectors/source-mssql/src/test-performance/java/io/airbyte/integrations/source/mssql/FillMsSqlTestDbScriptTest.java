/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.standardtest.source.AbstractSourcePerformanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

public class FillMsSqlTestDbScriptTest extends AbstractSourcePerformanceTest {

  private JsonNode config;
  private static final String CREATE_DB_TABLE_TEMPLATE = "CREATE TABLE %s.%s(id INTEGER PRIMARY KEY, %s)";
  private static final String INSERT_INTO_DB_TABLE_QUERY_TEMPLATE = "INSERT INTO %s.%s (%s) VALUES %s";
  private static final String TEST_DB_FIELD_TYPE = "varchar(10)";
  private static final String DATABASE_NAME = "test5000tables240columns200recordsDb";

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {}

  @Override
  protected String getImageName() {
    return "airbyte/source-mssql:dev";
  }

  @Override
  protected Database setupDatabase(String dbName) throws Exception {
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "Standard")
        .build());

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", "your_host")
        .put("port", 1433)
        .put("database", DATABASE_NAME) // set your db name
        .put("username", "username")
        .put("password", "pass")
        .put("replication_method", replicationMethod)
        .build());

    final Database database = Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:sqlserver://%s:%s;databaseName=%s;",
            config.get("host").asText(),
            config.get("port").asInt(),
            DATABASE_NAME),
        "com.microsoft.sqlserver.jdbc.SQLServerDriver",
        null);

    super.databaseName = dbName;

    return database;
  }

  @Override
  protected String getCreateTableTemplate() {
    return CREATE_DB_TABLE_TEMPLATE;
  }

  @Override
  protected String getInsertQueryTemplate() {
    return INSERT_INTO_DB_TABLE_QUERY_TEMPLATE;
  }

  @Override
  protected String getTestFieldType() {
    return TEST_DB_FIELD_TYPE;
  }

  @Override
  protected String getNameSpace() {
    return DATABASE_NAME;
  }

  /**
   * The test added test data to a new DB. 1. Set DB creds in static variables above 2. Set desired
   * number for streams, coolumns and records 3. Run the test
   */
  @Test
  @Disabled
  public void addTestDataToDbAndCheckTheResult() throws Exception {
    numberOfColumns = 240;
    numberOfDummyRecords = 200;
    numberOfStreams = 5000;
    int numberOfBatches = 1;

    final Database database = setupDatabase("dbo"); // "dbo" is a default schema name in DB

    database.query(ctx -> {
      for (int currentSteamNumber = 0; currentSteamNumber < numberOfStreams; currentSteamNumber++) {

        String currentTableName = String.format(getTestStreamNameTemplate(), currentSteamNumber);

        ctx.fetch(prepareCreateTableQuery(numberOfColumns, currentTableName));
        for (int i = 0; i < numberOfBatches; i++) {
          String insertQueryTemplate = prepareInsertQueryTemplatePostgres(i, numberOfColumns,
              numberOfDummyRecords);
          ctx.fetch(String.format(insertQueryTemplate, currentTableName));
        }

        c.info("Finished processing for stream " + currentSteamNumber);
      }
      return null;
    });

    database.close();

  }

}
