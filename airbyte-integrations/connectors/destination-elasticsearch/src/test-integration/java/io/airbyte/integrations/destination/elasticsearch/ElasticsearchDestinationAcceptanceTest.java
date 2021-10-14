/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.io.IOException;
import java.time.Duration;
import java.util.List;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.elasticsearch.ElasticsearchContainer;

public class ElasticsearchDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(ElasticsearchDestinationAcceptanceTest.class);

  private ObjectMapper mapper = new ObjectMapper();
  //private JsonNode configJson;
  private static ElasticsearchContainer container;

  @BeforeAll
  public static void beforeAll() {
    container = new ElasticsearchContainer("docker.elastic.co/elasticsearch/elasticsearch:7.12.1")
            .withEnv("ES_JAVA_OPTS", "-Xms256m -Xmx256m")
            .withEnv("discovery.type", "single-node")
            .withExposedPorts(9200)
            .withStartupTimeout(Duration.ofSeconds(60));
    container.start();
  }

  @AfterAll
  public static void afterAll() {
    container.stop();
    container.close();
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-elasticsearch:dev";
  }

  @Override
  protected int getMaxRecordValueLimit() {
    return 2000000;
  }

  @Override
  protected JsonNode getConfig() {
    var configJson = mapper.createObjectNode();
    configJson.put("host", container.getHost());
    configJson.put("port", container.getMappedPort(9200));
    //configJson.put("indexPrefix", "test-index");
    return configJson;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    // should result in a failed connection check
    return mapper.createObjectNode();
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema)
      throws IOException {
    // Records returned from this method will be compared against records provided to the connector
    // to verify they were written correctly

    final String tableName = ElasticsearchDestination.streamToIndexName(namespace, streamName);

    ElasticsearchConnection connection = new ElasticsearchConnection(mapper.convertValue(getConfig(), ConnectorConfiguration.class));
    return connection.getRecords(tableName);
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) {

  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {

  }

}
