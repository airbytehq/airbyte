/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.opensearch;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.io.IOException;
import java.time.Duration;
import java.util.Date;
import java.util.HashMap;
import org.apache.http.HttpHost;
import org.opensearch.action.index.IndexRequest;
import org.opensearch.action.index.IndexResponse;
import org.opensearch.client.RequestOptions;
import org.opensearch.client.RestClient;
import org.opensearch.client.RestClientBuilder;
import org.opensearch.client.RestHighLevelClient;
import org.opensearch.client.indices.CreateIndexRequest;
import org.opensearch.client.indices.CreateIndexResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.opensearch.testcontainers.OpensearchContainer;

public class OpenSearchSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(OpenSearchSourceAcceptanceTest.class);
  private static final ObjectMapper mapper = MoreMappers.initMapper();
  private static final String index = "sample";

  // TODO -> OpenSearchContainer -> Add depenency
  private static OpensearchContainer container;
  private RestHighLevelClient client;
  private JsonNode config;

  @Override
  protected String getImageName() {
    return "airbyte/source-opensearch:dev";
  }

  @Override
  protected JsonNode getConfig() {
    var configJson = mapper.createObjectNode();
    configJson.put("endpoint", String.format("http://%s:%s", container.getHost(), container.getMappedPort(9200)));
    return configJson;
  }

  @Override
  protected void setupEnvironment(TestDestinationEnv environment) throws Exception {
    container = new OpenSearchContainer("opensearchproject/opensearch:2.0.0")
        .withEnv("ES_JAVA_OPTS", "-Xms512m -Xms512m")
        .withEnv("discovery.type", "single-node")
        .withEnv("network.host", "0.0.0.0")
        .withEnv("logger.org.elasticsearch", "INFO")
        .withEnv("ingest.geoip.downloader.enabled", "false")
        .withEnv("xpack.security.enabled", "false")
        .withExposedPorts(9200)
        .withStartupTimeout(Duration.ofSeconds(60));
    container.start();
    getRestHighLevelClient(container);
    createIndex(client);
    addDocument(client);
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {
    client.close();
    container.stop();
    container.close();
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() throws IOException {
    return Jsons.deserialize(MoreResources.readResource("configured_catalog.json"), ConfiguredAirbyteCatalog.class);
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

  private void getRestHighLevelClient(OpenSearchContainer container) {
    RestClientBuilder restClientBuilder =
        RestClient.builder(HttpHost.create(container.getHttpHostAddress())).setHttpClientConfigCallback(httpClientBuilder -> httpClientBuilder);
    client = new RestHighLevelClient(restClientBuilder);
  }

  private void createIndex(final RestHighLevelClient client) throws IOException {
    CreateIndexRequest request = new CreateIndexRequest(index);
    CreateIndexResponse createIndexResponse = client.indices().create(request, RequestOptions.DEFAULT);
    if (createIndexResponse.isAcknowledged()) {
      LOGGER.info("Successfully created index: {}", index);
    }
  }

  private void addDocument(final RestHighLevelClient client) throws IOException {
    IndexRequest indexRequest = new IndexRequest(index)
        .id("1")
        .source("user", "kimchy",
            "postDate", new Date(),
            "message", "trying out OpenSearch");
    IndexResponse indexResponse = client.index(indexRequest, RequestOptions.DEFAULT);
    LOGGER.info("Index response status: {}", indexResponse.status());
  }

}
