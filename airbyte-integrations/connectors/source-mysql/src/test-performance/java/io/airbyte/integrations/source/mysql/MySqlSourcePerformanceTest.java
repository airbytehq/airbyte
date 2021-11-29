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
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MySQLContainer;

public class MySqlSourcePerformanceTest extends AbstractSourcePerformanceTest {

  private MySQLContainer<?> container;
  private JsonNode config;
  private static final String CREATE_DB_TABLE_TEMPLATE = "CREATE TABLE %s.%s(id INTEGER PRIMARY KEY, %s)";
  private static final String INSERT_INTO_DB_TABLE_QUERY_TEMPLATE = "INSERT INTO %s.%s (%s) VALUES %s";
  private static final String TEST_DB_FIELD_TYPE = "varchar(8)";

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    container.close();
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-mysql:dev";
  }

  @Override
  protected Database setupDatabase() throws Exception {
    container = new MySQLContainer<>("mysql:8.0");
    container.start();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("database", container.getDatabaseName())
        .put("username", container.getUsername())
        .put("password", container.getPassword())
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

    super.databaseName = container.getDatabaseName();

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
    return container.getDatabaseName();
  }

  /**
   * Creates all tables and insert data described in the registered data type tests.
   *
   * @throws Exception might raise exception if configuration goes wrong or tables creation/insert
   *         scripts failed.
   */
  private void setupDatabaseInternal() throws Exception {
    final Database database = setupDatabase();

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
   * The test checks that connector can fetch prepared data without failure.
   */
  @Test
  public void test1000Streams() throws Exception {
    numberOfColumns = 240; // 240 is near the max value for varchar(8) type
    // 200 is near the max value for 1 batch call,if need more - implement multiple batching for single
    // stream
    numberOfDummyRecords = 20; // 200;
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
