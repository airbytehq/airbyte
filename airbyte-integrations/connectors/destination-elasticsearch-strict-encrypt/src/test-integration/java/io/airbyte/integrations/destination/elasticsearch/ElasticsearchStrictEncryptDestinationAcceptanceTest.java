/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.testcontainers.elasticsearch.ElasticsearchContainer;

public class ElasticsearchStrictEncryptDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private final ObjectMapper mapper = new ObjectMapper();
  private static ElasticsearchContainer container;

  @BeforeAll
  public static void beforeAll() {

    container = new ElasticsearchContainer("docker.elastic.co/elasticsearch/elasticsearch:7.15.1")
        .withPassword("MagicWord");

    container.start();
  }

  @AfterAll
  public static void afterAll() {
    container.stop();
    container.close();
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-elasticsearch-strict-encrypt:dev";
  }

  @Override
  protected int getMaxRecordValueLimit() {
    return 2000000;
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected boolean supportsNormalization() {
    return false;
  }

  @Override
  protected boolean supportBasicDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportArrayDataTypeTest() {
    return false;
  }

  @Override
  protected boolean supportObjectDataTypeTest() {
    return true;
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new AdvancedTestDataComparator();
  }

  @Override
  protected JsonNode getConfig() {

    final JsonNode authConfig = Jsons.jsonNode(Map.of(
        "method", "basic",
        "username", "elastic",
        "password", "MagicWord"));

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("endpoint", String.format("http://%s:%s", container.getHost(), container.getMappedPort(9200)))
        .put("authenticationMethod", authConfig)
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    // should result in a failed connection check
    return mapper.createObjectNode();
  }

  @Override
  protected List<JsonNode> retrieveRecords(DestinationAcceptanceTest.TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema)
      throws IOException {
    // Records returned from this method will be compared against records provided to the connector
    // to verify they were written correctly
    final String indexName = new ElasticsearchWriteConfig()
        .setNamespace(namespace)
        .setStreamName(streamName)
        .getIndexName();

    ElasticsearchConnection connection = new ElasticsearchConnection(mapper.convertValue(getConfig(), ConnectorConfiguration.class));
    return connection.getRecords(indexName);
  }

  @Override
  protected void setup(DestinationAcceptanceTest.TestDestinationEnv testEnv) {}

  @Override
  protected void tearDown(DestinationAcceptanceTest.TestDestinationEnv testEnv) {
    ElasticsearchConnection connection = new ElasticsearchConnection(mapper.convertValue(getConfig(), ConnectorConfiguration.class));
    connection.allIndices().forEach(connection::deleteIndexIfPresent);
  }

}
