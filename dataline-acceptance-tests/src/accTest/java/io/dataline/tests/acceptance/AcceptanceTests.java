/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.tests.acceptance;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.node.JsonNodeFactory;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.dataline.api.model.SourceIdRequestBody;
import io.dataline.api.model.SourceImplementationCreate;
import io.dataline.api.model.SourceImplementationRead;
import io.dataline.api.model.SourceReadList;
import io.dataline.api.model.SourceSpecificationRead;
import io.dataline.commons.json.Jsons;
import io.dataline.config.persistence.PersistenceConstants;
import java.io.IOException;
import java.util.UUID;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

public class AcceptanceTests {

  static final MediaType JSON_CONTENT = MediaType.get("application/json; charset=utf-8");
  static final String SERVER_URL = "http://localhost:8001/api/v1/";
  static final OkHttpClient HTTP_CLIENT = new OkHttpClient();

  static PostgreSQLContainer PSQL_DB1;

  @BeforeAll
  public static void init() {
    PSQL_DB1 = new PostgreSQLContainer();
    PSQL_DB1.start();
  }

  @Test
  public void testCreateSourceImplementation() throws IOException {
    UUID postgresSourceId = getPostgresSourceId();
    SourceSpecificationRead sourceSpecRead =
        callApi("source_specifications/get", new SourceIdRequestBody().sourceId(postgresSourceId), SourceSpecificationRead.class);

    ObjectNode dbConfiguration = new ObjectNode(JsonNodeFactory.instance)
        .put("host", PSQL_DB1.getHost())
        .put("password", PSQL_DB1.getPassword())
        .put("port", PSQL_DB1.getFirstMappedPort())
        .put("dbname", PSQL_DB1.getDatabaseName())
        .put("filter_dbs", PSQL_DB1.getDatabaseName())
        .put("user", PSQL_DB1.getUsername());

    UUID defaultWorkspaceId = PersistenceConstants.DEFAULT_WORKSPACE_ID;
    UUID sourceSpecificationId = sourceSpecRead.getSourceSpecificationId();

    SourceImplementationCreate sourceImplementationCreate = new SourceImplementationCreate()
            .sourceSpecificationId(sourceSpecificationId)
        .workspaceId(defaultWorkspaceId)
        .connectionConfiguration(dbConfiguration);

    SourceImplementationRead createResponse = callApi("source_implementations/create", sourceImplementationCreate, SourceImplementationRead.class);

    assertEquals(defaultWorkspaceId, createResponse.getWorkspaceId());
    assertEquals(sourceSpecificationId, createResponse.getSourceSpecificationId());
    assertEquals(dbConfiguration, Jsons.jsonNode(createResponse.getConnectionConfiguration()));
  }

  private UUID getPostgresSourceId() throws IOException {
    return callApi("sources/list", "", SourceReadList.class).getSources()
        .stream()
        .filter(sourceRead -> sourceRead.getName().toLowerCase().equals("postgres"))
        .findFirst()
        .orElseThrow()
        .getSourceId();
  }

  private <Input, Output> Output callApi(String relativePath, Input requestBody, Class<Output> outputClass)
      throws IOException {
    RequestBody body = RequestBody.create(Jsons.serialize(requestBody), JSON_CONTENT);
    Request request = new Request.Builder().post(body).url(SERVER_URL + relativePath).build();
    try (Response response = HTTP_CLIENT.newCall(request).execute()) {
      Output responseBody = Jsons.deserialize(response.body().string(), outputClass);
      return responseBody;
    }
  }

}
