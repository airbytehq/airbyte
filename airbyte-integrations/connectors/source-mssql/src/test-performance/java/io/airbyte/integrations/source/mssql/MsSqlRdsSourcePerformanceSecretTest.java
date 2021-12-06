/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.integrations.standardtest.source.performancetest.AbstractSourcePerformanceTest;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.nio.file.Path;
import java.util.Map;
import org.junit.jupiter.api.Test;

public class MsSqlRdsSourcePerformanceSecretTest extends AbstractSourcePerformanceTest {

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
    return "airbyte/source-mssql:dev";
  }

  @Override
  protected void setupDatabase(String dbName) {
    JsonNode plainConfig = Jsons.deserialize(IOs.readFile(Path.of(PERFORMANCE_SECRET_CREDS)));

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", plainConfig.get("host"))
        .put("port", plainConfig.get("port"))
        .put("database", dbName)
        .put("username", plainConfig.get("username"))
        .put("password", plainConfig.get("password"))
        .build());
  }

  @Test
  public void test100tables100recordsDb() throws Exception {
    int numberOfDummyRecords = 100;
    int numberOfStreams = 100;
    String defaultDbSchemaName = "dbo";

    setupDatabase("test100tables100recordsDb");

    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog(defaultDbSchemaName,
        numberOfStreams, numberOfDummyRecords);
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
    String defaultDbSchemaName = "dbo";

    setupDatabase("test1000tables240columns200recordsDb");

    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog(defaultDbSchemaName,
        numberOfStreams, numberOfDummyRecords);
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
    String defaultDbSchemaName = "dbo";

    setupDatabase("test5000tables240columns200recordsDb");

    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog(defaultDbSchemaName,
        numberOfStreams, numberOfDummyRecords);
    final Map<String, Integer> mapOfExpectedRecordsCount = prepareMapWithExpectedRecords(
        numberOfStreams, numberOfDummyRecords);
    final Map<String, Integer> checkStatusMap =
        runReadVerifyNumberOfReceivedMsgs(catalog, null, mapOfExpectedRecordsCount);
    validateNumberOfReceivedMsgs(checkStatusMap);
  }

  @Test
  public void testSmall1000tableswith10000recordsDb() throws Exception {
    int numberOfDummyRecords = 10011;
    int numberOfStreams = 1000;
    String defaultDbSchemaName = "dbo";

    setupDatabase("newsmall1000tableswith10000rows");

    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog(defaultDbSchemaName,
        numberOfStreams, numberOfDummyRecords);
    final Map<String, Integer> mapOfExpectedRecordsCount = prepareMapWithExpectedRecords(
        numberOfStreams, numberOfDummyRecords);
    final Map<String, Integer> checkStatusMap =
        runReadVerifyNumberOfReceivedMsgs(catalog, null, mapOfExpectedRecordsCount);
    validateNumberOfReceivedMsgs(checkStatusMap);
  }

  @Test
  public void testInterim15tableswith50000recordsDb() throws Exception {
    int numberOfDummyRecords = 50051;
    int numberOfStreams = 15;
    String defaultDbSchemaName = "dbo";

    setupDatabase("newinterim15tableswith50000records");

    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog(defaultDbSchemaName,
        numberOfStreams, numberOfDummyRecords);
    final Map<String, Integer> mapOfExpectedRecordsCount = prepareMapWithExpectedRecords(
        numberOfStreams, numberOfDummyRecords);
    final Map<String, Integer> checkStatusMap =
        runReadVerifyNumberOfReceivedMsgs(catalog, null, mapOfExpectedRecordsCount);
    validateNumberOfReceivedMsgs(checkStatusMap);
  }

  @Test
  public void testRegular25tables50000recordsDb() throws Exception {
    int numberOfDummyRecords = 50052;
    int numberOfStreams = 25;
    String defaultDbSchemaName = "dbo";

    setupDatabase("newregular25tables50000records");

    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog(defaultDbSchemaName,
        numberOfStreams, numberOfDummyRecords);
    final Map<String, Integer> mapOfExpectedRecordsCount = prepareMapWithExpectedRecords(
        numberOfStreams, numberOfDummyRecords);
    final Map<String, Integer> checkStatusMap =
        runReadVerifyNumberOfReceivedMsgs(catalog, null, mapOfExpectedRecordsCount);
    validateNumberOfReceivedMsgs(checkStatusMap);
  }

}
