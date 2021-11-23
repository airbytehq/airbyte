/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.source.mysql.MySqlSource.ReplicationMethod;
import io.airbyte.integrations.standardtest.source.AbstractSourcePerformanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.Map;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

public class FillTestDbScriptTest extends AbstractSourcePerformanceTest {

  private JsonNode config;
  private static final String CREATE_DB_TABLE_TEMPLATE = "CREATE TABLE %s.%s(id INTEGER PRIMARY KEY, %s)";
  private static final String INSERT_INTO_DB_TABLE_QUERY_TEMPLATE = "INSERT INTO %s.%s (%s) VALUES %s";
  private static final String TEST_DB_FIELD_TYPE = "varchar(8)";
  private static final String DATABASE_NAME = "your_db_name";

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {}

  @Override
  protected String getImageName() {
    return "airbyte/source-mysql:dev";
  }

  @Override
  protected Database setupDatabase(String dbName) throws Exception {
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", "your_host")
        .put("port", 3306)
        .put("database", DATABASE_NAME) // set your db name
        .put("username", "your_username")
        .put("password", "your_padd")
        .put("replication_method", ReplicationMethod.STANDARD)
        .build());

    final Database database = Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:mysql://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()),
        "com.mysql.cj.jdbc.Driver",
        SQLDialect.MYSQL,
        "zeroDateTimeBehavior=convertToNull");

    super.databaseName = DATABASE_NAME;

    // It disable strict mode in the DB and allows to insert specific values.
    // For example, it's possible to insert date with zero values "2021-00-00"
    database.query(ctx -> ctx.execute("SET @@sql_mode=''"));

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
   * Creates all tables and insert data described in the registered data type tests.
   *
   * @throws Exception might raise exception if configuration goes wrong or tables creation/insert
   *         scripts failed.
   */
  private void setupDatabaseInternal() throws Exception {
    final Database database = setupDatabase(null);

    database.query(ctx -> {
      String insertQueryTemplate = prepareInsertQueryTemplate(numberOfColumns,
          numberOfDummyRecords);

      for (int currentSteamNumber = 0; currentSteamNumber < numberOfStreams; currentSteamNumber++) {
        // CREATE TABLE test.test_1_int(id INTEGER PRIMARY KEY, test_column int)

        String currentTableName = String.format(getTestStreamNameTemplate(), currentSteamNumber);

        ctx.fetch(prepareCreateTableQuery(numberOfColumns, currentTableName));
        ctx.fetch(String.format(insertQueryTemplate, currentTableName));

        c.info("Finished processing for stream " + currentSteamNumber);
      }
      return null;
    });

    database.close();
  }

  /**
   * The test added test data to a new DB and check results. 1. Set DB creds in static variables above
   * 2. Set desired number for streams, coolumns and records 3. Run the test
   */
  @Test
  @Disabled
  public void addTestDataToDbAndCheckTheResult() throws Exception {
    numberOfColumns = 240; // 240 is near the max value for varchar(8) type
    // 200 is near the max value for 1 batch call,if need more - implement multiple batching for single
    // stream
    numberOfDummyRecords = 200; // 200;
    numberOfStreams = 1000;

    setupDatabaseInternal();

    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog();
    final Map<String, Integer> mapOfExpectedRecordsCount = prepareMapWithExpectedRecords(
        numberOfStreams, numberOfDummyRecords);
    final Map<String, Integer> checkStatusMap =
        runReadVerifyNumberOfReceivedMsgs(catalog, null, mapOfExpectedRecordsCount);
    validateNumberOfReceivedMsgs(checkStatusMap);
  }

}
