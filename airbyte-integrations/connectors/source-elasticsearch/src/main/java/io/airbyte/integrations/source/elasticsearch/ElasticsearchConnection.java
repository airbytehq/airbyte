/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.elasticsearch;

import co.elastic.clients.base.*;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.regex.Pattern;
import org.apache.http.Header;
import org.apache.http.HttpHost;
import org.apache.http.message.BasicHeader;
import org.elasticsearch.action.search.*;
import org.elasticsearch.client.*;
import org.elasticsearch.client.indices.GetIndexRequest;
import org.elasticsearch.client.indices.GetIndexResponse;
import org.elasticsearch.client.indices.GetMappingsRequest;
import org.elasticsearch.client.indices.GetMappingsResponse;
import org.elasticsearch.cluster.metadata.MappingMetadata;
import org.elasticsearch.common.unit.TimeValue;
import org.elasticsearch.index.query.QueryBuilders;
import org.elasticsearch.search.Scroll;
import org.elasticsearch.search.SearchHit;
import org.elasticsearch.search.builder.SearchSourceBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * All communication with Elasticsearch should be done through this class.
 */
public class ElasticsearchConnection {

  private static final int MAX_HITS = 10000;
  private static final Logger log = LoggerFactory.getLogger(ElasticsearchConnection.class);
  private final RestHighLevelClient client;
  private final ObjectMapper mapper = new ObjectMapper();

  /**
   * Creates a new ElasticsearchConnection that can be used to read/write records to indices
   *
   * @param config Configuration parameters for connecting to the Elasticsearch host
   */
  public ElasticsearchConnection(ConnectorConfiguration config) {
    log.info(String.format(
        "creating ElasticsearchConnection: %s", config.getEndpoint()));

    // Create the low-level client

    HttpHost httpHost = HttpHost.create(config.getEndpoint());

    RestClientBuilder builder = RestClient.builder(httpHost).setDefaultHeaders(configureHeaders(config)).setFailureListener((new FailureListener()));
    client = new RestHighLevelClient(builder);
  }

  static class FailureListener extends RestClient.FailureListener {

    @Override
    public void onFailure(Node node) {
      log.error("RestClient failure: {}", node);
    }

  }

  /**
   * Configures the default headers for requests to the Elasticsearch server
   *
   * @param config connection information
   * @return the default headers
   */
  protected Header[] configureHeaders(ConnectorConfiguration config) {
    final var headerList = new ArrayList<Header>();
    // add Authorization header if credentials are present
    final var auth = config.getAuthenticationMethod();
    switch (auth.getMethod()) {
      case secret -> {
        var bytes = (auth.getApiKeyId() + ":" + auth.getApiKeySecret()).getBytes(StandardCharsets.UTF_8);
        var header = "ApiKey " + Base64.getEncoder().encodeToString(bytes);
        headerList.add(new BasicHeader("Authorization", header));
      }
      case basic -> {
        var basicBytes = (auth.getUsername() + ":" + auth.getPassword()).getBytes(StandardCharsets.UTF_8);
        var basicHeader = "Basic " + Base64.getEncoder().encodeToString(basicBytes);
        headerList.add(new BasicHeader("Authorization", basicHeader));
      }
    }
    return headerList.toArray(new Header[headerList.size()]);
  }

  /**
   * Pings the Elasticsearch server for "up" check, and configuration validation
   *
   * @return true if connection was successful
   */
  public boolean checkConnection() {
    log.info("checking elasticsearch connection");
    try {
      final var info = client.info(RequestOptions.DEFAULT);
      log.info("checked elasticsearch connection: {}, node-name: {}, version: {}", info.getClusterName(), info.getNodeName(), info.getVersion());
      return true;
    } catch (ApiException e) {
      log.error("failed to ping elasticsearch", unwrappedApiException("failed write operation", e));
      return false;
    } catch (Exception e) {
      log.error("unknown exception while pinging elasticsearch server", e);
      return false;
    }
  }

  /**
   * Shutdown the connection to the Elasticsearch server
   */
  public void close() throws IOException {
    this.client.close();
  }

  /**
   * Unwraps a rest client ApiException, so we can log the details
   *
   * @param message message to add to the log entry
   * @param e source ApiException
   * @return a new RuntimeException with the ApiException as the source
   */
  private RuntimeException unwrappedApiException(String message, ApiException e) {
    log.error(message);
    if (Objects.isNull(e) || Objects.isNull(e.error())) {
      log.error("unknown ApiException");
      return new RuntimeException(e);
    }
    if (ElasticsearchError.class.isAssignableFrom(e.error().getClass())) {
      ElasticsearchError esException = ((ElasticsearchError) e.error());
      String errorMessage = String.format("ElasticsearchError: status:%s, error:%s", esException.status(), esException.error().toString());
      return new RuntimeException(errorMessage);
    }
    return new RuntimeException(e);
  }

  /**
   * Gets mappings (metadata for fields) from Elasticsearch cluster for given indices
   *
   * @param indices A list of indices for which the mapping is required
   * @return String to MappingMetadata as a native Java Map
   * @throws IOException throws IOException if Elasticsearch request fails
   */
  public Map<String, MappingMetadata> getMappings(final List<String> indices) throws IOException {
    int chunk = 15;
    Map<String, MappingMetadata> mappings = new HashMap<>();
    // Avoid too_long_frame_exception error by "batching"
    // the indexes mapping calls
    for (int i = 0; i < indices.size(); i += chunk) {
      String[] copiedIndices = indices.subList(i, Math.min(indices.size(), i + chunk)).toArray(String[]::new);
      GetMappingsRequest request = new GetMappingsRequest();
      request.indices(copiedIndices);
      GetMappingsResponse getMappingResponse = client.indices().getMapping(request, RequestOptions.DEFAULT);
      mappings.putAll(getMappingResponse.mappings());
    }
    return mappings;
  }

  /**
   * Gets all mappings (metadata for fields) from Elasticsearch cluster
   *
   * @return String to MappingMetadata as a native Java Map
   * @throws IOException throws IOException if Elasticsearch request fails
   */
  public Map<String, MappingMetadata> getAllMappings() throws IOException {
    // Need to exclude system mappings
    GetMappingsRequest request = new GetMappingsRequest();
    GetMappingsResponse getMappingResponse = client.indices().getMapping(request, RequestOptions.DEFAULT);
    return getMappingResponse.mappings();
  }

  /**
   * Returns a list of all records, without the metadata in JsonNode format Uses scroll API for
   * pagination
   *
   * @param index index name in Elasticsearch cluster
   * @return list of documents
   * @throws IOException throws IOException if Elasticsearch request fails
   */
  public List<JsonNode> getRecords(String index) throws IOException {
    final Scroll scroll = new Scroll(TimeValue.timeValueMinutes(1L));
    SearchSourceBuilder searchSourceBuilder = new SearchSourceBuilder();
    searchSourceBuilder.size(MAX_HITS);
    searchSourceBuilder.query(QueryBuilders.matchAllQuery());

    SearchRequest searchRequest = new SearchRequest(index);
    searchRequest.scroll(scroll);
    searchRequest.source(searchSourceBuilder);

    SearchResponse searchResponse = client.search(searchRequest, RequestOptions.DEFAULT);
    String scrollId = searchResponse.getScrollId();
    log.info("Running scroll query with scrollId {}", scrollId);
    SearchHit[] searchHits = searchResponse.getHits().getHits();
    List<JsonNode> data = new ArrayList<>();

    while (searchHits != null && searchHits.length > 0) {
      SearchScrollRequest scrollRequest = new SearchScrollRequest(scrollId);
      scrollRequest.scroll(scroll);
      searchResponse = client.scroll(scrollRequest, RequestOptions.DEFAULT);
      scrollId = searchResponse.getScrollId();

      for (SearchHit hit : searchHits) {
        data.add(mapper.convertValue(hit, JsonNode.class).get("sourceAsMap"));

      }
      searchHits = searchResponse.getHits().getHits();
    }

    ClearScrollRequest clearScrollRequest = new ClearScrollRequest();
    clearScrollRequest.addScrollId(scrollId);
    ClearScrollResponse clearScrollResponse = client.clearScroll(clearScrollRequest, RequestOptions.DEFAULT);
    boolean succeeded = clearScrollResponse.isSucceeded();
    if (succeeded) {
      log.info("scroll response cleared successfully");
    } else {
      log.error("failed to clear scroll response");
    }

    return data;
  }

  /**
   * Returns a list of user defined indices, with system indices exclusions made using regex variable
   * ALL_INDICES_QUERY
   *
   * @return indices list
   * @throws IOException throws IOException if Elasticsearch request fails
   */
  public List<String> userIndices() throws IOException {
    GetIndexRequest request = new GetIndexRequest(ElasticsearchConstants.ALL_INDICES_QUERY);
    GetIndexResponse response = this.client.indices().get(request, RequestOptions.DEFAULT);
    List<String> indices = Arrays.asList(response.getIndices());
    Pattern pattern = Pattern.compile(ElasticsearchConstants.REGEX_FOR_USER_INDICES_ONLY);
    indices = indices.stream().filter(pattern.asPredicate().negate()).toList();
    return indices;
  }

  /**
   * Returns a list of all indices including Elasticsearch system indices
   *
   * @return indices list
   * @throws IOException throws IOException if Elasticsearch request fails
   */
  public List<String> allIndices() throws IOException {
    GetIndexRequest request = new GetIndexRequest(ElasticsearchConstants.ALL_INDICES_QUERY);
    GetIndexResponse response = this.client.indices().get(request, RequestOptions.DEFAULT);
    return Arrays.asList(response.getIndices());
  }

}
