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
import com.google.common.collect.Lists;
import com.google.gson.internal.LinkedTreeMap;
import com.rockset.client.ApiClient;
import com.rockset.client.ApiException;
import com.rockset.client.RocksetClient;
import com.rockset.client.api.QueriesApi;
import com.rockset.client.model.Collection;
import com.rockset.client.model.CreateCollectionRequest;
import com.rockset.client.model.CreateWorkspaceRequest;
import com.rockset.client.model.DeleteDocumentsRequest;
import com.rockset.client.model.DeleteDocumentsRequestData;
import com.rockset.client.model.ErrorModel;
import com.rockset.client.model.GetCollectionResponse;
import com.rockset.client.model.QueryRequest;
import com.rockset.client.model.QueryRequestSql;
import com.rockset.client.model.QueryResponse;

import java.util.List;
import java.util.stream.Collectors;

import com.squareup.okhttp.Response;
import io.airbyte.commons.json.Jsons;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RocksetUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(RocksetUtils.class);

  public static final String WORKSPACE_ID = "workspace";
  public static final String API_KEY_ID = "api_key";
  public static final String APISERVER_URL = "api.rs2.usw2.rockset.com";

  public static RocksetClient clientFromConfig(JsonNode config) {
    String apiKey = config.get(API_KEY_ID).asText();
    return new RocksetClient(apiKey, APISERVER_URL);
  }

  public static ApiClient apiClientFromConfig(JsonNode config) {
    String apiKey = config.get(API_KEY_ID).asText();
    ApiClient client = new ApiClient();
    client.setApiKey(apiKey);
    client.setVersion("0.9.0");
    return client;
  }

  public static void createWorkspaceIfNotExists(RocksetClient client, String workspace)
      throws Exception {
    CreateWorkspaceRequest request = new CreateWorkspaceRequest().name(workspace);

    try {
      client.createWorkspace(request);
      LOGGER.info(String.format("Created workspace %s", workspace));
    } catch (ApiException e) {
      if (e.getCode() == 400 && e.getErrorModel().getType() == ErrorModel.TypeEnum.ALREADYEXISTS) {
        LOGGER.info(String.format("Workspace %s already exists", workspace));
        return;
      }

      throw e;
    }
  }

  // Assumes the workspace exists
  public static void createCollectionIfNotExists(
      RocksetClient client,
      String workspace,
      String cname)
      throws Exception {
    CreateCollectionRequest request = new CreateCollectionRequest().name(cname);
    try {
      client.createCollection(workspace, request);
      LOGGER.info(String.format("Created collection %s.%s", workspace, cname));
    } catch (ApiException e) {
      if (e.getCode() == 400 && e.getErrorModel().getType() == ErrorModel.TypeEnum.ALREADYEXISTS) {
        LOGGER.info(String.format("Collection %s.%s already exists", workspace, cname));
        return;
      }

      throw e;
    }
  }

  // Assumes the collection exists
  public static void deleteCollectionIfExists(
      RocksetClient client,
      String workspace,
      String cname)
      throws Exception {
    try {
      client.deleteCollection(workspace, cname);
      LOGGER.info(String.format("Deleted collection %s.%s", workspace, cname));
    } catch (ApiException e) {
      if (e.getCode() == 404 && e.getErrorModel().getType() == ErrorModel.TypeEnum.NOTFOUND) {
        LOGGER.info(String.format("Collection %s.%s does not exist", workspace, cname));
        return;
      }

      throw e;
    }
  }

  // Assumes the collection exists
  public static void waitUntilCollectionReady(RocksetClient client, String workspace, String cname)
      throws Exception {
    while (true) {
      GetCollectionResponse resp = client.getCollection(workspace, cname);
      Collection.StatusEnum status = resp.getData().getStatus();
      if (status == Collection.StatusEnum.READY) {
        LOGGER.info(String.format("Collection %s.%s is READY", workspace, cname));
        break;
      } else {
        LOGGER.info(
            String.format(
                "Waiting until %s.%s is READY, it is %s", workspace, cname, status.toString()));
        Thread.sleep(5000);
      }
    }
  }

  // Assumes the collection exists
  public static void waitUntilCollectionDeleted(RocksetClient client, String workspace, String cname)
      throws Exception {
    while (true) {
      try {
        client.getCollection(workspace, cname);
        LOGGER.info(String.format("Collection %s.%s still exists, waiting for deletion to complete", workspace, cname));
        Thread.sleep(5000);
      } catch (ApiException e) {
        if (e.getCode() == 404 && e.getErrorModel().getType() == ErrorModel.TypeEnum.NOTFOUND) {
          LOGGER.info(String.format("Collection %s.%s does not exist", workspace, cname));
          return;
        }

        throw e;
      }
    }
  }

  // Assumes the collection exists
  public static void waitUntilDocCount(RocksetClient client, String sql, int desiredCount)
      throws Exception {
    while (true) {
      LOGGER.info(String.format("Running query %s", sql));

      QueryRequestSql qrs = new QueryRequestSql();
      qrs.setQuery(sql);

      QueryRequest qr = new QueryRequest();
      qr.setSql(qrs);

      QueryResponse response = client.query(qr);
      int resultCount = response.getResults().size();

      if (resultCount == desiredCount) {
        LOGGER.info(String.format("Desired result count %s found", desiredCount));
        break;
      } else {
        LOGGER.info(
            String.format(
                "Waiting for desired result count %s, current is %s", desiredCount, resultCount));
        Thread.sleep(5000);
      }
    }
  }

  public static List<JsonNode> query(RocksetClient client, String queryText) throws Exception {
    QueryResponse queryResponse = client.query(new QueryRequest().sql(new QueryRequestSql().query(queryText)));
    return queryResponse.getResults().stream().map(Jsons::jsonNode).collect(Collectors.toList());
  }

  public static void truncateCollection(RocksetClient client, String workspace, String collection) throws Exception {
    List<JsonNode> allCurrentRecords = query(client, String.format("SELECT * FROM %s.%s", workspace, collection));
    List<DeleteDocumentsRequestData> documentsToDelete = allCurrentRecords.stream()
        .map(json -> new DeleteDocumentsRequestData().id(json.get("_id").asText()))
        .collect(Collectors.toList());

    client.deleteDocuments(workspace, collection, new DeleteDocumentsRequest().data(documentsToDelete));
  }
}
