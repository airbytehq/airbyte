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
import com.google.common.hash.Hasher;
import com.google.common.hash.Hashing;
import com.google.gson.internal.LinkedTreeMap;
import com.rockset.client.ApiClient;
import com.rockset.client.ApiException;
import com.rockset.client.api.CollectionsApi;
import com.rockset.client.api.DocumentsApi;
import com.rockset.client.api.QueriesApi;
import com.rockset.client.api.WorkspacesApi;
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
import io.airbyte.commons.lang.Exceptions;
import org.awaitility.Awaitility;
import org.awaitility.Duration;
import org.awaitility.core.ConditionFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.charset.Charset;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

public class RocksetUtils {

    private static final Logger LOGGER = LoggerFactory.getLogger(RocksetUtils.class);

    public static final String WORKSPACE_ID = "workspace";
    public static final String API_KEY_ID = "api_key";
    public static final String API_SERVER_ID = "api_server";
    public static final String DEFAULT_API_SERVER = "https://api.rs2.usw2.rockset.com";
    public static final Duration DEFAULT_TIMEOUT = new Duration(20, TimeUnit.MINUTES);
    public static final Duration DEFAULT_POLL_INTERVAL = Duration.FIVE_SECONDS;
    private static final java.time.Duration DEFAULT_HTTP_CLIENT_TIMEOUT = java.time.Duration.ofMinutes(1L);

    public static ApiClient apiClientFromConfig(JsonNode config) {
        final String apiKey = config.get(API_KEY_ID).asText();
        final String apiServer = config.get(API_SERVER_ID).asText(DEFAULT_API_SERVER);
        return apiClient(apiKey, apiServer);
    }

    public static ApiClient apiClient(String apiKey, String apiServer) {
        final ApiClient client = new ApiClient();

        client.setReadTimeout((int) DEFAULT_HTTP_CLIENT_TIMEOUT.toMillis())
                .setConnectTimeout((int) DEFAULT_HTTP_CLIENT_TIMEOUT.toMillis())
                .setWriteTimeout((int) DEFAULT_HTTP_CLIENT_TIMEOUT.toMillis());

        client.setApiKey(apiKey);
        client.setApiServer(apiServer);
        client.setVersion("0.9.0");
        return client;
    }

    public static void createWorkspaceIfNotExists(ApiClient client, String workspace) {
        final CreateWorkspaceRequest request = new CreateWorkspaceRequest().name(workspace);

        try {
            new WorkspacesApi(client).create(request);
            LOGGER.info(String.format("Created workspace %s", workspace));
        } catch (ApiException e) {
            if (e.getCode() == 400 && e.getErrorModel().getType() == ErrorModel.TypeEnum.ALREADYEXISTS) {
                LOGGER.info(String.format("Workspace %s already exists", workspace));
                return;
            }

            throw new RuntimeException(e);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    // Assumes the workspace exists
    public static void createCollectionIfNotExists(ApiClient client, String workspace, String cname) {
        final CreateCollectionRequest request = new CreateCollectionRequest().name(cname);
        try {
            new CollectionsApi(client).create(workspace, request);
            LOGGER.info(String.format("Created collection %s.%s", workspace, cname));
        } catch (ApiException e) {
            if (e.getCode() == 400 && e.getErrorModel().getType() == ErrorModel.TypeEnum.ALREADYEXISTS) {
                LOGGER.info(String.format("Collection %s.%s already exists", workspace, cname));
                return;
            }
            throw new RuntimeException(e);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    // Assumes the collection exists
    public static void deleteCollectionIfExists(ApiClient client, String workspace, String cname) {
        try {
            new CollectionsApi(client).delete(workspace, cname);
            LOGGER.info(String.format("Deleted collection %s.%s", workspace, cname));
        } catch (ApiException e) {
            if (e.getCode() == 404 && e.getErrorModel().getType() == ErrorModel.TypeEnum.NOTFOUND) {
                LOGGER.info(String.format("Collection %s.%s does not exist", workspace, cname));
                return;
            }

            throw new RuntimeException(e);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    // Assumes the collection exists
    public static void waitUntilCollectionReady(ApiClient client, String workspace, String cname) {
        pollingConfig(workspace, cname)
                .until(() ->
                        isCollectionReady(client, workspace, cname)
                );

    }

    private static boolean isCollectionReady(ApiClient client, String workspace, String cname) throws Exception {
        final GetCollectionResponse resp = new CollectionsApi(client).get(workspace, cname);
        final Collection.StatusEnum status = resp.getData().getStatus();
        if (status == Collection.StatusEnum.READY) {
            LOGGER.info(String.format("Collection %s.%s is READY", workspace, cname));
            return true;
        } else {
            LOGGER.info(
                    String.format(
                            "Waiting until %s.%s is READY, it is %s", workspace, cname, status.toString()));
            return false;
        }
    }

    // Assumes the collection exists
    public static void waitUntilCollectionDeleted(ApiClient client, String workspace, String cname) {
        pollingConfig(workspace, cname)
                .until(() ->
                        isCollectionDeleted(client, workspace, cname)
                );

    }

    private static boolean isCollectionDeleted(ApiClient client, String workspace, String cname) throws Exception {
        try {
            new CollectionsApi(client).get(workspace, cname);
            LOGGER.info(
                    String.format(
                            "Collection %s.%s still exists, waiting for deletion to complete",
                            workspace, cname));
        } catch (ApiException e) {
            if (e.getCode() == 404 && e.getErrorModel().getType() == ErrorModel.TypeEnum.NOTFOUND) {
                LOGGER.info(String.format("Collection %s.%s does not exist", workspace, cname));
                return true;
            }

            throw e;
        }
        return false;
    }

    // Assumes the collection exists
    public static void waitUntilDocCount(ApiClient client, String sql, int desiredCount) {
        pollingConfig(sql)
                .until(() ->
                        queryMatchesCount(client, sql, desiredCount)
                );
    }

    private static boolean queryMatchesCount(ApiClient client, String sql, int desiredCount) throws Exception {
        LOGGER.info(String.format("Running query %s", sql));
        final QueryRequestSql qrs = new QueryRequestSql();
        qrs.setQuery(sql);

        final QueryRequest qr = new QueryRequest();
        qr.setSql(qrs);

        final QueryResponse response = new QueriesApi(client).query(qr);
        final int resultCount = response.getResults().size();

        if (resultCount == desiredCount) {
            LOGGER.info(String.format("Desired result count %s found", desiredCount));
            return true;
        } else {
            LOGGER.info(
                    String.format(
                            "Waiting for desired result count %s, current is %s", desiredCount, resultCount));
            return false;
        }
    }

    public static void clearCollectionIfCollectionExists(ApiClient client, String workspace, String cname) {
        Exceptions.toRuntime(() -> {

            final QueryRequest qr = new QueryRequest().sql(new QueryRequestSql().query(String.format("SELECT _id from %s.%s", workspace, cname)));
            try {
                final QueryResponse resp = new QueriesApi(client).query(qr);
                final List<String> ids = resp.getResults().stream().map(f -> (LinkedTreeMap<String, Object>) f).map(f -> (String) f.get("_id")).collect(Collectors.toList());
                final DeleteDocumentsRequest ddr = new DeleteDocumentsRequest();
                for (String id : ids) {
                    ddr.addDataItem(new DeleteDocumentsRequestData().id(id));
                }
                LOGGER.info("Deleting documents from " + cname);
                new DocumentsApi(client).delete(workspace, cname, ddr);
            } catch (Exception e) {
                LOGGER.error("Error while trying to clear a collection ", e);
            }

        });
    }

    private static Duration jitter(String... args) {
        final Hasher hsh = Hashing.murmur3_32().newHasher();
        for (String s : args) {
            hsh.putString(s, Charset.defaultCharset());
        }

        return new Duration(Math.abs(hsh.hash().asInt()) % DEFAULT_POLL_INTERVAL.getValueInMS(), TimeUnit.MILLISECONDS);

    }

    private static ConditionFactory pollingConfig(final String... args) {
        return Awaitility.await()
                .timeout(DEFAULT_TIMEOUT)
                .pollDelay(jitter(args))
                .pollInterval(DEFAULT_POLL_INTERVAL);
    }
}
