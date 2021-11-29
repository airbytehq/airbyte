/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.standardtest.source.AbstractSourcePerformanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.nio.file.Path;
import java.util.Map;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Test;

public class MySqlRdsSourcePerformanceSecretTest extends AbstractSourcePerformanceTest {

  private JsonNode config;
  private static final String CREATE_DB_TABLE_TEMPLATE = "CREATE TABLE %s.%s(id INTEGER PRIMARY KEY, %s)";
  private static final String INSERT_INTO_DB_TABLE_QUERY_TEMPLATE = "INSERT INTO %s.%s (%s) VALUES %s";
  private static final String TEST_DB_FIELD_TYPE = "varchar(8)";
  private static final String PERFORMANCE_SECRET_CREDS = "secrets/performance-config.json";

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
    super.databaseName = dbName;
    JsonNode plainConfig = Jsons.deserialize(IOs.readFile(Path.of(PERFORMANCE_SECRET_CREDS)));

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", plainConfig.get("host"))
        .put("port", plainConfig.get("port"))
        .put("database", dbName)
        .put("username", plainConfig.get("username"))
        .put("password", plainConfig.get("password"))
        .put("replication_method", plainConfig.get("replication_method"))
        .build());

    final Database database = Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:mysql://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            dbName),
        "com.mysql.cj.jdbc.Driver",
        SQLDialect.MYSQL,
        "zeroDateTimeBehavior=convertToNull");

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
    return databaseName;
  }

  @Test
  public void test100tables100recordsDb() throws Exception {
    numberOfColumns = 240; // 240 is near the max value for varchar(8) type
    // 200 is near the max value for 1 batch call,if need more - implement multiple batching for single
    // stream
    numberOfDummyRecords = 100; // 200 is near the max value for one shot in batching;
    numberOfStreams = 100;

    setupDatabase("test100tables100recordsDb");

    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog();
    final Map<String, Integer> mapOfExpectedRecordsCount = prepareMapWithExpectedRecords(
        numberOfStreams, numberOfDummyRecords);
    final Map<String, Integer> checkStatusMap =
        runReadVerifyNumberOfReceivedMsgs(catalog, null, mapOfExpectedRecordsCount);
    validateNumberOfReceivedMsgs(checkStatusMap);
  }

  @Test
  public void test1000tables240columns200recordsDb() throws Exception {
    numberOfColumns = 240; // 240 is near the max value for varchar(8) type
    // 200 is near the max value for 1 batch call,if need more - implement multiple batching for single
    // stream
    numberOfDummyRecords = 200;
    numberOfStreams = 1000;

    setupDatabase("test1000tables240columns200recordsDb");

    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog();
    final Map<String, Integer> mapOfExpectedRecordsCount = prepareMapWithExpectedRecords(
        numberOfStreams, numberOfDummyRecords);
    final Map<String, Integer> checkStatusMap =
        runReadVerifyNumberOfReceivedMsgs(catalog, null, mapOfExpectedRecordsCount);
    validateNumberOfReceivedMsgs(checkStatusMap);
  }

  @Test
  public void test5000tables240columns200recordsDb() throws Exception {
    numberOfColumns = 240; // 240 is near the max value for varchar(8) type
    // 200 is near the max value for 1 batch call,if need more - implement multiple batching for single
    // stream
    numberOfDummyRecords = 200;
    numberOfStreams = 5000;

    setupDatabase("test5000tables240columns200recordsDb");

    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog();
    final Map<String, Integer> mapOfExpectedRecordsCount = prepareMapWithExpectedRecords(
        numberOfStreams, numberOfDummyRecords);
    final Map<String, Integer> checkStatusMap =
        runReadVerifyNumberOfReceivedMsgs(catalog, null, mapOfExpectedRecordsCount);
    validateNumberOfReceivedMsgs(checkStatusMap);
  }

  @Test
  public void testSmall1000tableswith10000recordsDb() throws Exception {
    numberOfDummyRecords = 10001;
    numberOfStreams = 1000;

    setupDatabase("newsmall1000tableswith10000rows");

    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog();
    final Map<String, Integer> mapOfExpectedRecordsCount = prepareMapWithExpectedRecords(
        numberOfStreams, numberOfDummyRecords);
    final Map<String, Integer> checkStatusMap =
        runReadVerifyNumberOfReceivedMsgs(catalog, null, mapOfExpectedRecordsCount);
    validateNumberOfReceivedMsgs(checkStatusMap);
  }

  @Test
  public void testInterim15tableswith50000recordsDb() throws Exception {
    numberOfDummyRecords = 50010;
    numberOfStreams = 15;

    setupDatabase("newinterim15tableswith50000records");

    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog();
    final Map<String, Integer> mapOfExpectedRecordsCount = prepareMapWithExpectedRecords(
        numberOfStreams, numberOfDummyRecords);
    final Map<String, Integer> checkStatusMap =
        runReadVerifyNumberOfReceivedMsgs(catalog, null, mapOfExpectedRecordsCount);
    validateNumberOfReceivedMsgs(checkStatusMap);
  }

  @Test
  public void testRegular25tables50000recordsDb() throws Exception {
    numberOfDummyRecords = 49960;
    numberOfStreams = 25;

    setupDatabase("newregular25tables50000records");

    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog();
    final Map<String, Integer> mapOfExpectedRecordsCount = prepareMapWithExpectedRecords(
        numberOfStreams, numberOfDummyRecords);
    final Map<String, Integer> checkStatusMap =
        runReadVerifyNumberOfReceivedMsgs(catalog, null, mapOfExpectedRecordsCount);
    validateNumberOfReceivedMsgs(checkStatusMap);
  }

}
