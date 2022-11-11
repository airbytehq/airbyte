/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
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
  private static ElasticsearchContainer container;

  @BeforeAll
  public static void beforeAll() {
    container = new ElasticsearchContainer("docker.elastic.co/elasticsearch/elasticsearch:7.15.1")
        .withEnv("ES_JAVA_OPTS", "-Xms512m -Xms512m")
        .withEnv("discovery.type", "single-node")
        .withEnv("network.host", "0.0.0.0")
        .withEnv("logger.org.elasticsearch", "INFO")
        .withEnv("ingest.geoip.downloader.enabled", "false")
        .withEnv("xpack.security.enabled", "false")
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
    // TODO: Enable supportArrayDataTypeTest after ticket 14568 will be done
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
    var configJson = mapper.createObjectNode();
    configJson.put("endpoint", String.format("http://%s:%s", container.getHost(), container.getMappedPort(9200)));
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
    final String indexName = new ElasticsearchWriteConfig()
        .setNamespace(namespace)
        .setStreamName(streamName)
        .getIndexName();

    ElasticsearchConnection connection = new ElasticsearchConnection(mapper.convertValue(getConfig(), ConnectorConfiguration.class));
    return connection.getRecords(indexName);
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) {}

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    ElasticsearchConnection connection = new ElasticsearchConnection(mapper.convertValue(getConfig(), ConnectorConfiguration.class));
    connection.allIndices().forEach(connection::deleteIndexIfPresent);
  }

}
