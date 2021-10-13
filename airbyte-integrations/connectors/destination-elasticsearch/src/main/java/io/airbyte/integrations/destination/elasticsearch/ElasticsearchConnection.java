/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

import co.elastic.clients.base.RestClientTransport;
import co.elastic.clients.base.Transport;
import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._core.CreateResponse;
import co.elastic.clients.elasticsearch._core.SearchResponse;
import co.elastic.clients.elasticsearch._core.search.Hit;
import co.elastic.clients.elasticsearch._core.search.HitsMetadata;
import co.elastic.clients.json.jackson.JacksonJsonpMapper;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.*;
import java.util.stream.Collectors;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import org.apache.http.Header;
import org.apache.http.HttpHost;
import org.apache.http.message.BasicHeader;
import org.elasticsearch.action.search.SearchRequestBuilder;
import org.elasticsearch.client.Node;
import org.elasticsearch.client.RestClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ElasticsearchConnection {

  // this is the max number of hits we can query without paging
  private static final int MAX_HITS = 10000;
  private static Logger log = LoggerFactory.getLogger(ElasticsearchConnection.class);

  private final String tmpIndex = "_airbyte";
  private final String indexPrefix;
  private final ObjectMapper mapper = new ObjectMapper();
  private final ElasticsearchClient client;

  public ElasticsearchConnection(ConnectorConfiguration config) {
    log.info(String.format(
            "creating ElasticsearchConnection: %s:%s with indexPrefix: %s", config.getHost(), config.getPort(), config.getIndexPrefix()));
    this.indexPrefix = config.getIndexPrefix();

    // Create the low-level client
    var httpHost = new HttpHost(config.getHost());
    RestClient restClient = RestClient.builder(httpHost)
            .setDefaultHeaders(configureHeaders(config))
            .build();
    // Create the transport that provides JSON and http services to API clients
    Transport transport = new RestClientTransport(restClient, new JacksonJsonpMapper());
    // And create our API client
    client = new ElasticsearchClient(transport);
  }

  private Header[] configureHeaders(ConnectorConfiguration config) {

    var headerList = new ArrayList<Header>();

    // add Authorization header if credentials are present
    if (Objects.nonNull(config.getApiKeyId()) && Objects.nonNull(config.getApiKeySecret())) {
      var bytes = (config.getApiKeyId() + ":" + config.getApiKeySecret()).getBytes(StandardCharsets.UTF_8);
      var header = "ApiKey " + Base64.getEncoder().encodeToString(bytes);
      headerList.add(new BasicHeader("Authorization", header));
    }

    return headerList.toArray(new Header[headerList.size()]);
  }


  public boolean ping() {
    try {
      return client.ping().value();
    } catch (IOException e) {
      log.error("failed to ping elasticsearch server", e);
      return false;
    }
  }
  public AirbyteConnectionStatus check() {

    Instant now = Instant.now();
    String docID = String.format("_airbyte_%s", now.toEpochMilli());
    // create an empty doc to test with
    ObjectNode document = mapper.createObjectNode();
    try {
      CreateResponse createResponse = client.create(builder ->
              builder.id(docID).document(document).index(tmpIndex));
      log.info("successfully connected to elasticsearch instance");
      log.info("created test doc: {}", createResponse.result());
    } catch (IOException e) {
      return failIO(e);
    }

    try {
      // Search for the doc we created
      SearchResponse<JsonNode> search = client.search(s -> s.index(tmpIndex).query(q -> q.ids(i -> i.addValues(docID))), JsonNode.class);

      HitsMetadata<JsonNode> hitMeta = search.hits();
      // Should we return a failed check if the search results aren't successful?
      if (hitMeta.hits().isEmpty()) {
        log.warn("failed to search test doc.");
      } else {
        for (Hit<JsonNode> hit : hitMeta.hits()) {
          System.out.println(hit.source());
        }
      }
    } catch (IOException e) {
      return failIO(e);
    }

    try {
      client.delete(d -> d.id(docID).index(tmpIndex));
    } catch (IOException e) {
      return failIO(e);
    }

    return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
  }

  public void writeRecord(String index, String id, JsonNode data) throws Exception {
    CreateResponse createResponse = client.create(builder ->
            builder.id(id).document(data).index(index));
    log.debug("wrote record: {}", createResponse.result());
  }

  public List<JsonNode> getRecords(String index) throws IOException {
    SearchResponse<JsonNode> search = client.search(s -> s.index(index).size(MAX_HITS), JsonNode.class);
    HitsMetadata<JsonNode> hitMeta = search.hits();
    return hitMeta.hits().stream().map(Hit::source).collect(Collectors.toList());
  }

  public void close() {
    this.client.shutdown();
  }

  public void createIndexIfMissing(String index) {
    // Create an index, but dont throw an exception
    try {
      final co.elastic.clients.elasticsearch.indices.CreateResponse createResponse = client.indices().create(b -> b.index(index));
      if (createResponse.acknowledged() && createResponse.shardsAcknowledged()) {
        log.info("created index: {}", index);
      } else {
        log.info("did not create index: {}, {}", index, createResponse);
      }
    } catch (IOException e) {
      log.error("failed to create index", e);
    }
  }

  private AirbyteConnectionStatus failIO(IOException e) {
    log.error("fatal exception", e);
    return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED)
            .withMessage(e.getMessage());
  }
}
