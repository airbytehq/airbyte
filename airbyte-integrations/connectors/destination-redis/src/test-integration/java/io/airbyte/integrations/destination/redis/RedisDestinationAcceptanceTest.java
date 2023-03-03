/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.BeforeAll;

class RedisDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private JsonNode jsonConfig;

  private RedisCache redisCache;

  private RedisNameTransformer redisNameTransformer;

  private static RedisContainerInitializr.RedisContainer redisContainer;

  @BeforeAll
  static void initContainer() {
    redisContainer = RedisContainerInitializr.initContainer();
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) {
    jsonConfig = RedisDataFactory.jsonConfig(
        redisContainer.getHost(),
        redisContainer.getFirstMappedPort());
    redisCache = new RedisHCache(jsonConfig);
    redisNameTransformer = new RedisNameTransformer();
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    redisCache.flushAll();
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-redis:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return jsonConfig;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return RedisDataFactory.jsonConfig(
        "127.0.0.9",
        8080);
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
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
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema) {
    var key = redisNameTransformer.keyName(namespace, streamName);
    return redisCache.getAll(key).stream()
        .sorted(Comparator.comparing(RedisRecord::getTimestamp))
        .map(RedisRecord::getData)
        .map(Jsons::deserialize)
        .collect(Collectors.toList());
  }

}
