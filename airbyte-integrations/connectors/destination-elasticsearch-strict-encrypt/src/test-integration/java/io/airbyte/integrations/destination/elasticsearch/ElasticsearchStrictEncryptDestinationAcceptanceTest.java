/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

import static org.junit.Assert.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.testcontainers.elasticsearch.ElasticsearchContainer;

public class ElasticsearchStrictEncryptDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static ElasticsearchContainer container;
  private static final String IMAGE_NAME = "docker.elastic.co/elasticsearch/elasticsearch:8.3.3";
  private final ObjectMapper mapper = new ObjectMapper();

  @BeforeAll
  public static void beforeAll() {

    container = new ElasticsearchContainer(IMAGE_NAME)
        .withEnv("discovery.type", "single-node")
        .withEnv("network.host", "0.0.0.0")
        .withEnv("logger.org.elasticsearch", "INFO")
        .withEnv("ingest.geoip.downloader.enabled", "false")
        .withExposedPorts(9200)
        .withPassword("s3cret");

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
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("endpoint", String.format("https://%s:%s", container.getHost(), container.getMappedPort(9200)))
        .put("authenticationMethod", getAuthConfig())
        .put("ca_certificate", new String(container.copyFileFromContainer(
            "/usr/share/elasticsearch/config/certs/http_ca.crt",
            InputStream::readAllBytes), StandardCharsets.UTF_8))
        .build());
  }

  protected JsonNode getUnsecureConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("endpoint", String.format("http://%s:%s", container.getHost(), container.getMappedPort(9200)))
        .put("authenticationMethod", getAuthConfig())
        .build());
  }

  protected JsonNode getAuthConfig() {
    return Jsons.jsonNode(Map.of(
        "method", "basic",
        "username", "elastic",
        "password", "s3cret"));
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

  @Test
  public void testCheckConnectionInvalidHttpProtocol() throws Exception {
    assertEquals(Status.FAILED, runCheck(getUnsecureConfig()).getStatus());
  }

}
