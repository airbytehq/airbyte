/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.opensearch;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.regex.Pattern;
import org.apache.http.Header;
import org.apache.http.HttpHost;
import org.apache.http.message.BasicHeader;
import org.opensearch.action.search.ClearScrollRequest;
import org.opensearch.action.search.ClearScrollResponse;
import org.opensearch.action.search.SearchRequest;
import org.opensearch.action.search.SearchResponse;
import org.opensearch.action.search.SearchScrollRequest;
import org.opensearch.client.Node;
import org.opensearch.client.RequestOptions;
import org.opensearch.client.RestClient;
import org.opensearch.client.RestClientBuilder;
import org.opensearch.client.RestHighLevelClient;
import org.opensearch.client.indices.GetIndexRequest;
import org.opensearch.client.indices.GetIndexResponse;
import org.opensearch.client.indices.GetMappingsRequest;
import org.opensearch.client.indices.GetMappingsResponse;
import org.opensearch.client.opensearch._types.OpenSearchException;
import org.opensearch.cluster.metadata.MappingMetadata;
import org.opensearch.common.unit.TimeValue;
import org.opensearch.index.query.QueryBuilders;
import org.opensearch.search.Scroll;
import org.opensearch.search.SearchHit;
import org.opensearch.search.builder.SearchSourceBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * All communication with OpenSearch should be done through this class.
 */
public class OpenSearchConnection {

  private static final int MAX_HITS = 10000;
  private static final Logger log = LoggerFactory.getLogger(OpenSearchConnection.class);
  private final RestHighLevelClient client;
  private final ObjectMapper mapper = new ObjectMapper();

  /**
   * Creates a new OpenSearchConnection that can be used to read/write records to indices
   *
   * @param config Configuration parameters for connecting to the OpenSearch host
   */
  public OpenSearchConnection(ConnectorConfiguration config) {
    log.info(String.format(
        "creating OpenSearchConnection: %s", config.getEndpoint()));

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
   * Configures the default headers for requests to the OpenSearch server
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
   * Pings the OpenSearch server for "up" check, and configuration validation
   *
   * @return true if connection was successful
   */
  public boolean checkConnection() {
    log.info("checking OpenSearch connection");
    try {
      final var info = client.info(RequestOptions.DEFAULT);
      log.info("checked OpenSearch connection: {}, node-name: {}, version: {}", info.getClusterName(), info.getNodeName(), info.getVersion());
      return true;
    } catch (OpenSearchException e) {
      log.error("failed to ping OpenSearch", unwrappedApiException("failed write operation", e));
      return false;
    } catch (Exception e) {
      log.error("unknown exception while pinging OpenSearch server", e);
      return false;
    }
  }

  /**
   * Shutdown the connection to the OpenSearch server
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
  private RuntimeException unwrappedApiException(String message, OpenSearchException e) {
    log.error(message);
    if (Objects.isNull(e) || Objects.isNull(e.error())) {
      log.error("unknown ApiException");
      return new RuntimeException(e);
    }
    if (OpenSearchException.class.isAssignableFrom(e.getCause().getClass())) {
      OpenSearchException esException = ((OpenSearchException) e.getCause());
      String errorMessage = String.format("OpenSearchException: status:%s, error:%s", esException.status(), esException.error().toString());
      return new RuntimeException(errorMessage);
    }
    return new RuntimeException(e);
  }

  /**
   * Gets mappings (metadata for fields) from OpenSearch cluster for given indices
   *
   * @param indices A list of indices for which the mapping is required
   * @return String to MappingMetadata as a native Java Map
   * @throws IOException throws IOException if OpenSearch request fails
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
   * Gets all mappings (metadata for fields) from OpenSearch cluster
   *
   * @return String to MappingMetadata as a native Java Map
   * @throws IOException throws IOException if OpenSearch request fails
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
   * @param index index name in OpenSearch cluster
   * @return list of documents
   * @throws IOException throws IOException if OpenSearch request fails
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
   * @throws IOException throws IOException if OpenSearch request fails
   */
  public List<String> userIndices() throws IOException {
    GetIndexRequest request = new GetIndexRequest(OpenSearchConstants.ALL_INDICES_QUERY);
    GetIndexResponse response = this.client.indices().get(request, RequestOptions.DEFAULT);
    List<String> indices = Arrays.asList(response.getIndices());
    Pattern pattern = Pattern.compile(OpenSearchConstants.REGEX_FOR_USER_INDICES_ONLY);
    indices = indices.stream().filter(pattern.asPredicate().negate()).toList();
    return indices;
  }

  /**
   * Returns a list of all indices including OpenSearch system indices
   *
   * @return indices list
   * @throws IOException throws IOException if OpenSearch request fails
   */
  public List<String> allIndices() throws IOException {
    GetIndexRequest request = new GetIndexRequest(OpenSearchConstants.ALL_INDICES_QUERY);
    GetIndexResponse response = this.client.indices().get(request, RequestOptions.DEFAULT);
    return Arrays.asList(response.getIndices());
  }

}
