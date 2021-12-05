/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.integrations.standardtest.source.performancetest.AbstractSourcePerformanceTest;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.nio.file.Path;
import java.util.Map;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Test;

public class PostgresRdsSourcePerformanceSecretTest extends AbstractSourcePerformanceTest {

  private JsonNode config;
  private static final String PERFORMANCE_SECRET_CREDS = "secrets/performance-config.json";

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {}

  @Override
  protected String getImageName() {
    return "airbyte/source-postgres:dev";
  }

  @Override
  protected Database setupDatabase(String dbName) {
    JsonNode plainConfig = Jsons.deserialize(IOs.readFile(Path.of(PERFORMANCE_SECRET_CREDS)));

    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "Standard")
        .build());

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", plainConfig.get("host"))
        .put("port", plainConfig.get("port"))
        .put("database", plainConfig.get("database"))
        .put("username", plainConfig.get("username"))
        .put("password", plainConfig.get("password"))
        .put("ssl", true)
        .put("replication_method", replicationMethod)
        .build());

    final Database database = Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:postgresql://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()),
        "org.postgresql.Driver",
        SQLDialect.POSTGRES);

    return database;
  }

  @Test
  public void test100tables100recordsDb() throws Exception {
    int numberOfDummyRecords = 100; // 200 is near the max value for one shot in batching;
    int numberOfStreams = 100;
    String dbName = "test100tables100recordsDb";

    setupDatabase(dbName);

    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog(dbName, numberOfStreams,
        numberOfDummyRecords);
    final Map<String, Integer> mapOfExpectedRecordsCount = prepareMapWithExpectedRecords(
        numberOfStreams, numberOfDummyRecords);
    final Map<String, Integer> checkStatusMap =
        runReadVerifyNumberOfReceivedMsgs(catalog, null, mapOfExpectedRecordsCount);
    validateNumberOfReceivedMsgs(checkStatusMap);
  }

  @Test
  public void test1000tables240columns200recordsDb() throws Exception {
    int numberOfDummyRecords = 200;
    int numberOfStreams = 1000;
    String dbName = "test1000tables240columns200recordsDb";

    setupDatabase(dbName);

    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog(dbName, numberOfStreams,
        numberOfDummyRecords);
    final Map<String, Integer> mapOfExpectedRecordsCount = prepareMapWithExpectedRecords(
        numberOfStreams, numberOfDummyRecords);
    final Map<String, Integer> checkStatusMap =
        runReadVerifyNumberOfReceivedMsgs(catalog, null, mapOfExpectedRecordsCount);
    validateNumberOfReceivedMsgs(checkStatusMap);
  }

  @Test
  public void test5000tables240columns200recordsDb() throws Exception {
    int numberOfDummyRecords = 200;
    int numberOfStreams = 5000;
    String dbName = "test5000tables240columns200recordsDb";

    setupDatabase(dbName);

    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog(dbName, numberOfStreams,
        numberOfDummyRecords);
    final Map<String, Integer> mapOfExpectedRecordsCount = prepareMapWithExpectedRecords(
        numberOfStreams, numberOfDummyRecords);
    final Map<String, Integer> checkStatusMap =
        runReadVerifyNumberOfReceivedMsgs(catalog, null, mapOfExpectedRecordsCount);
    validateNumberOfReceivedMsgs(checkStatusMap);
  }

  @Test
  public void testSmall1000tableswith10000recordsDb() throws Exception {
    int numberOfDummyRecords = 10001;
    int numberOfStreams = 1000;
    String dbName = "newsmall1000tableswith10000rows";
    setupDatabase(dbName);

    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog(dbName, numberOfStreams,
        numberOfDummyRecords);
    final Map<String, Integer> mapOfExpectedRecordsCount = prepareMapWithExpectedRecords(
        numberOfStreams, numberOfDummyRecords);
    final Map<String, Integer> checkStatusMap =
        runReadVerifyNumberOfReceivedMsgs(catalog, null, mapOfExpectedRecordsCount);
    validateNumberOfReceivedMsgs(checkStatusMap);
  }

  @Test
  public void testInterim15tableswith50000recordsDb() throws Exception {
    int numberOfDummyRecords = 50010;
    int numberOfStreams = 15;
    String dbName = "newinterim15tableswith50000records";
    setupDatabase(dbName);

    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog(dbName, numberOfStreams,
        numberOfDummyRecords);
    final Map<String, Integer> mapOfExpectedRecordsCount = prepareMapWithExpectedRecords(
        numberOfStreams, numberOfDummyRecords);
    final Map<String, Integer> checkStatusMap =
        runReadVerifyNumberOfReceivedMsgs(catalog, null, mapOfExpectedRecordsCount);
    validateNumberOfReceivedMsgs(checkStatusMap);
  }

  @Test
  public void testRegular25tables50000recordsDb() throws Exception {
    int numberOfDummyRecords = 50011;
    int numberOfStreams = 25;
    String dbName = "newregular25tables50000records";
    setupDatabase(dbName);

    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog(dbName, numberOfStreams,
        numberOfDummyRecords);
    final Map<String, Integer> mapOfExpectedRecordsCount = prepareMapWithExpectedRecords(
        numberOfStreams, numberOfDummyRecords);
    final Map<String, Integer> checkStatusMap =
        runReadVerifyNumberOfReceivedMsgs(catalog, null, mapOfExpectedRecordsCount);
    validateNumberOfReceivedMsgs(checkStatusMap);
  }

}
