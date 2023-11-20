/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.commons.json.Jsons;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.BeforeAll;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KinesisDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(KinesisDestinationAcceptanceTest.class);

  private JsonNode configJson;

  private KinesisStream kinesisStream;

  private KinesisNameTransformer kinesisNameTransformer;

  private static KinesisContainerInitializr.KinesisContainer kinesisContainer;

  @BeforeAll
  static void initContainer() {
    kinesisContainer = KinesisContainerInitializr.initContainer();
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) {
    configJson = KinesisDataFactory.jsonConfig(
        kinesisContainer.getEndpointOverride().toString(),
        kinesisContainer.getRegion(),
        kinesisContainer.getAccessKey(),
        kinesisContainer.getSecretKey());
    kinesisStream = new KinesisStream(new KinesisConfig(configJson));
    kinesisNameTransformer = new KinesisNameTransformer();
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new AdvancedTestDataComparator();
  }

  @Override
  protected boolean supportBasicDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportArrayDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportObjectDataTypeTest() {
    return true;
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    kinesisStream.deleteAllStreams();
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-kinesis:dev";
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected JsonNode getConfig() {
    return configJson;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return KinesisDataFactory.jsonConfig(
        "127.0.0.9",
        "eu-west-1",
        "random_access_key",
        "random_secret_key");
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema) {
    final var stream = kinesisNameTransformer.streamName(namespace, streamName);
    return kinesisStream.getRecords(stream).stream()
        .sorted(Comparator.comparing(KinesisRecord::getTimestamp))
        .map(KinesisRecord::getData)
        .map(Jsons::deserialize)
        .collect(Collectors.toList());
  }

}
