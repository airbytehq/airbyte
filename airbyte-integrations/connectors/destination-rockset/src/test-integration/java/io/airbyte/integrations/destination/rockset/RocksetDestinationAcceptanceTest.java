/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.rockset;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.rockset.client.ApiClient;
import com.rockset.client.api.QueriesApi;
import com.rockset.client.model.QueryRequest;
import com.rockset.client.model.QueryRequestSql;
import com.squareup.okhttp.Response;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.stream.Collectors;
import org.junit.jupiter.api.AfterAll;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testng.collections.Sets;

public class RocksetDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final ObjectMapper mapper = new ObjectMapper();
  private static final Set<String> collectionsToClear = Sets.newHashSet();
  private static final Set<String> collectionsToDelete = Sets.newHashSet();
  private static final ExecutorService tearDownExec = Executors.newCachedThreadPool();
  private static final RocksetSQLNameTransformer nameTransformer = new RocksetSQLNameTransformer();

  private static final Logger LOGGER =
      LoggerFactory.getLogger(RocksetDestinationAcceptanceTest.class);

  @Override
  protected String getImageName() {
    return "airbyte/destination-rockset:dev";
  }

  @Override
  protected JsonNode getConfig() throws IOException {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
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
  protected JsonNode getFailCheckConfig() throws Exception {
    return Jsons.jsonNode(
        ImmutableMap.builder()
            .put("workspace", "commons")
            .put("api_key", "nope nope nope")
            .build());
  }

  @Override
  protected List<JsonNode> retrieveRecords(
                                           TestDestinationEnv testEnv,
                                           String stream,
                                           String namespace,
                                           JsonNode streamSchema)
      throws Exception {

    final String ws = getConfig().get("workspace").asText();
    final ApiClient client = RocksetUtils.apiClientFromConfig(getConfig());
    final String streamName = nameTransformer.convertStreamName(stream);
    LOGGER.info("Retrieving records for " + streamName);

    RocksetUtils.createWorkspaceIfNotExists(client, ws);
    RocksetUtils.createCollectionIfNotExists(client, ws, streamName);
    RocksetUtils.waitUntilCollectionReady(client, ws, streamName);
    collectionsToClear.add(streamName);
    collectionsToDelete.add(streamName);

    // ORDER BY _event_time because the test suite expects to retrieve messages in the order they
    // were
    // originally written
    final String sqlText = String.format("SELECT * FROM %s.%s ORDER BY _event_time;", ws, streamName);

    final QueryRequest query = new QueryRequest().sql(new QueryRequestSql().query(sqlText));

    final QueriesApi queryClient = new QueriesApi(RocksetUtils.apiClientFromConfig(getConfig()));

    LOGGER.info("About to wait for indexing on " + streamName);
    try {
      // As Rockset is not a transactional database, we have to wait a few seconds to be extra sure
      // that we've given documents enough time to be fully indexed when retrieving records
      Thread.sleep(20_000);
    } catch (InterruptedException e) {
      e.printStackTrace();
    }
    List<JsonNode> results = new ArrayList<>();
    int previousResultSize;
    // By heuristic once the document level stabilizes, the ingestion is probably done
    do {
      previousResultSize = results.size();
      Thread.sleep(10_000);
      final Response response = queryClient.queryCall(query, null, null).execute();
      final JsonNode json = mapper.readTree(response.body().string());
      results = Lists.newArrayList(json.get("results").iterator());
      LOGGER.info("Waiting on stable doc counts, prev= " + previousResultSize + " currrent=" + results.size());
    } while (results.size() != previousResultSize);

    return results.stream()
        .peek(RocksetDestinationAcceptanceTest::dropRocksetAddedFields)
        .collect(Collectors.toList());
  }

  private static void dropRocksetAddedFields(JsonNode n) {
    dropFields(n, "_id", "_event_time");
  }

  private static void dropFields(JsonNode node, String... fields) {
    Arrays.stream(fields).forEach(((ObjectNode) node)::remove);
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) {
    // Nothing to do
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    try {
      final ApiClient client = RocksetUtils.apiClientFromConfig(getConfig());
      String workspace = getConfig().get("workspace").asText();
      collectionsToClear.stream()
          .map(
              cn -> CompletableFuture.runAsync(() -> {
                RocksetUtils.clearCollectionIfCollectionExists(client, workspace, cn);
              }, tearDownExec))
          // collect to avoid laziness of stream
          .collect(Collectors.toList())
          .forEach(CompletableFuture::join);
      collectionsToClear.clear();
    } catch (IOException e) {
      e.printStackTrace();
    }
  }

  @AfterAll
  public static void exitSuite() throws Exception {
    LOGGER.info("Deleting all collections used during testing ");
    final JsonNode config = Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
    final ApiClient client = RocksetUtils.apiClientFromConfig(config);
    final String workspace = config.get("workspace").asText();
    collectionsToDelete.stream().map(cn -> deleteCollection(client, workspace, cn)).collect(Collectors.toList()).forEach(CompletableFuture::join);
    tearDownExec.shutdown();

  }

  private static CompletableFuture<Void> deleteCollection(ApiClient client, String workspace, String cn) {
    return CompletableFuture.runAsync(
        () -> Exceptions.toRuntime(
            () -> {
              RocksetUtils.deleteCollectionIfExists(client, workspace, cn);
              RocksetUtils.waitUntilCollectionDeleted(client, workspace, cn);
              Thread.sleep(2500); // Let services pick up deletion in case of re-creation
            }),
        tearDownExec);
  }

}
