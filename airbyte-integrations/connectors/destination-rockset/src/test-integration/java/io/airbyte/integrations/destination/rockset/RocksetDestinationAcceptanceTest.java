/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.rockset;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.rockset.client.RocksetClient;
import com.rockset.client.api.QueriesApi;
import com.rockset.client.model.QueryRequest;
import com.rockset.client.model.QueryRequestSql;
import com.squareup.okhttp.Response;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.io.IOException;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testng.collections.Sets;

public class RocksetDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final ObjectMapper mapper = new ObjectMapper();
  private static final Set<String> collectionNames = Sets.newHashSet();

  private static final Logger LOGGER =
      LoggerFactory.getLogger(RocksetDestinationAcceptanceTest.class);

  @Override
  protected String getImageName() {
    return "airbyte/destination-rockset:dev";
  }

  @Override
  protected JsonNode getConfig() throws IOException {
    return Jsons.deserialize(MoreResources.readResource("secrets/config.json"));
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
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema)
      throws Exception {

    String ws = getConfig().get("workspace").asText();
    RocksetClient client = RocksetUtils.clientFromConfig(getConfig());

    RocksetUtils.createWorkspaceIfNotExists(client, ws);
    RocksetUtils.createCollectionIfNotExists(client, ws, streamName);
    RocksetUtils.waitUntilCollectionReady(client, ws, streamName);
    collectionNames.add(streamName);

    String sqlText = String.format("SELECT * FROM %s.%s;", ws, streamName);

    QueryRequest query =
      new QueryRequest()
        .sql(new QueryRequestSql().query(sqlText));

    QueriesApi queryClient = new QueriesApi(RocksetUtils.apiClientFromConfig(getConfig()));
    Response response = queryClient.queryCall(query, null, null).execute();

    try {
      // As Rockset is not a transactional database, we have to wait a few seconds to be extra sure
      // that we've given documents enough time to be fully indexed when retrieving records
      Thread.sleep(30000);
    } catch (InterruptedException e) {
      e.printStackTrace();
    }

    JsonNode json = mapper.readTree(response.body().string());
    List<JsonNode> results = Lists.newArrayList(json.get("results").iterator());
    results =
        results.stream()
            // remove rockset added fields
            .peek(jn -> ((ObjectNode) jn).remove("_id"))
            .peek(jn -> ((ObjectNode) jn).remove("_event_time"))
            .collect(Collectors.toList());
    return results;
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) {
    // Nothing to do
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    try {
      final RocksetClient client = RocksetUtils.clientFromConfig(getConfig());
      String workspace = getConfig().get("workspace").asText();
      collectionNames.forEach(
          cn -> Exceptions.toRuntime(
              () -> {
                RocksetUtils.deleteCollectionIfExists(client, workspace, cn);
                RocksetUtils.waitUntilCollectionDeleted(client, workspace, cn);
              }));
    } catch (IOException e) {
      e.printStackTrace();
    }
  }

}
