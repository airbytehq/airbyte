/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.integrations.standardtest.source.performancetest.AbstractSourceFillDbWithTestData;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.params.provider.Arguments;

public class FillMsSqlTestDbScriptTest extends AbstractSourceFillDbWithTestData {

  private JsonNode config;

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
  protected Database setupDatabase(String dbName) {
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "Standard")
        .build());

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", "your_host")
        .put("port", 1433)
        .put("database", dbName) // set your db name
        .put("username", "your_username")
        .put("password", "your_pass")
        .put("replication_method", replicationMethod)
        .build());

    final Database database = Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:sqlserver://%s:%s;databaseName=%s;",
            config.get("host").asText(),
            config.get("port").asInt(),
            dbName),
        "com.microsoft.sqlserver.jdbc.SQLServerDriver",
        null);

    return database;
  }

  /**
   * This is a data provider for fill DB script,, Each argument's group would be ran as a separate
   * test. 1st arg - a name of DB that will be used in jdbc connection string. 2nd arg - a schemaName
   * that will be ised as a NameSpace in Configured Airbyte Catalog. 3rd arg - a number of expected
   * records retrieved in each stream. 4th arg - a number of messages batches
   * (numberOfMessages*numberOfBatches, ex. 100*2=200 messages in total in each stream) 5th arg - a
   * number of columns in each stream\table that will be use for Airbyte Cataloq configuration 6th arg
   * - a number of streams to read in configured airbyte Catalog. Each stream\table in DB should be
   * names like "test_0", "test_1",..., test_n.
   */
  @BeforeAll
  public static void beforeAll() {
    AbstractSourceFillDbWithTestData.testArgs = Stream.of(
        Arguments.of("your_db_name", "dbo", 100, 2, 240, 1000) // "dbo" is a default schema name in MsSQl DB
    );
  }

}
